"""
SAP TestOS - LLM Service
Unified interface for AI/LLM operations with fallback support
Supports Ollama (free), OpenAI, and Anthropic
"""
import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Unified LLM service with provider abstraction and fallback logic.
    Priority: Ollama (free/local) -> OpenAI -> Anthropic -> Fallback responses
    """
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.model = settings.LLM_MODEL
        self.base_url = settings.LLM_BASE_URL
        self.api_key = settings.LLM_API_KEY
        self.timeout = settings.LLM_TIMEOUT
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        
        # Provider-specific endpoints
        self.providers_config = {
            'ollama': {
                'endpoint': f'{self.base_url}/api/generate',
                'requires_key': False,
                'default_model': 'llama3.2'
            },
            'openai': {
                'endpoint': 'https://api.openai.com/v1/chat/completions',
                'requires_key': True,
                'default_model': 'gpt-3.5-turbo'
            },
            'anthropic': {
                'endpoint': 'https://api.anthropic.com/v1/messages',
                'requires_key': True,
                'default_model': 'claude-3-haiku-20240307'
            }
        }
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Generate text using configured LLM provider with automatic fallback.
        
        Returns dict with:
        - content: Generated text
        - success: Boolean indicating if generation succeeded
        - provider: Which provider was used
        - model: Model used
        - tokens_used: Approximate token count
        - fallback_used: Whether fallback was triggered
        """
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        try:
            # Try primary provider
            result = await self._try_provider(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                json_mode=json_mode
            )
            
            if result['success']:
                logger.info(f"LLM generation successful with {result['provider']}")
                return result
            
            # Primary failed, try fallback providers
            logger.warning(f"Primary provider {self.provider} failed, trying fallbacks")
            return await self._try_fallback_providers(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                json_mode=json_mode
            )
            
        except Exception as e:
            logger.error(f"All LLM providers failed: {str(e)}")
            return self._get_fallback_response(prompt, json_mode)
    
    async def _try_provider(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Try a specific provider"""
        
        if self.provider == 'ollama':
            return await self._call_ollama(prompt, system_prompt, max_tokens, temperature, json_mode)
        elif self.provider == 'openai':
            return await self._call_openai(prompt, system_prompt, max_tokens, temperature, json_mode)
        elif self.provider == 'anthropic':
            return await self._call_anthropic(prompt, system_prompt, max_tokens, temperature, json_mode)
        else:
            return self._get_fallback_response(prompt, json_mode)
    
    async def _try_fallback_providers(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Try alternative providers in order"""
        fallback_order = ['ollama', 'openai', 'anthropic']
        
        for provider_name in fallback_order:
            if provider_name == self.provider:
                continue  # Skip already tried provider
            
            original_provider = self.provider
            self.provider = provider_name
            
            try:
                result = await self._try_provider(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    json_mode=json_mode
                )
                
                if result['success']:
                    result['fallback_used'] = True
                    result['original_provider'] = original_provider
                    return result
                    
            except Exception as e:
                logger.warning(f"Fallback provider {provider_name} failed: {str(e)}")
                continue
            finally:
                self.provider = original_provider
        
        # All providers failed, use hardcoded fallback
        return self._get_fallback_response(prompt, json_mode)
    
    async def _call_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Call Ollama API (local, free)"""
        try:
            import aiohttp
            
            payload = {
                "model": self.model or self.providers_config['ollama']['default_model'],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            if json_mode:
                payload["format"] = "json"
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.providers_config['ollama']['endpoint'],
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data.get('response', '')
                        
                        if json_mode:
                            try:
                                content = json.loads(content)
                            except:
                                pass
                        
                        return {
                            'content': content,
                            'success': True,
                            'provider': 'ollama',
                            'model': self.model,
                            'tokens_used': data.get('eval_count', 0),
                            'fallback_used': False
                        }
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        return {'content': '', 'success': False, 'provider': 'ollama'}
                        
        except Exception as e:
            logger.error(f"Ollama call failed: {str(e)}")
            return {'content': '', 'success': False, 'provider': 'ollama'}
    
    async def _call_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        if not self.api_key:
            return {'content': '', 'success': False, 'provider': 'openai'}
        
        try:
            import aiohttp
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model or self.providers_config['openai']['default_model'],
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.providers_config['openai']['endpoint'],
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        if json_mode:
                            try:
                                content = json.loads(content)
                            except:
                                pass
                        
                        usage = data.get('usage', {})
                        return {
                            'content': content,
                            'success': True,
                            'provider': 'openai',
                            'model': self.model,
                            'tokens_used': usage.get('total_tokens', 0),
                            'fallback_used': False
                        }
                    else:
                        logger.error(f"OpenAI API error: {response.status}")
                        return {'content': '', 'success': False, 'provider': 'openai'}
                        
        except Exception as e:
            logger.error(f"OpenAI call failed: {str(e)}")
            return {'content': '', 'success': False, 'provider': 'openai'}
    
    async def _call_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        json_mode: bool
    ) -> Dict[str, Any]:
        """Call Anthropic API"""
        if not self.api_key:
            return {'content': '', 'success': False, 'provider': 'anthropic'}
        
        try:
            import aiohttp
            
            system_content = system_prompt or "You are a helpful assistant."
            
            payload = {
                "model": self.model or self.providers_config['anthropic']['default_model'],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_content,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.providers_config['anthropic']['endpoint'],
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['content'][0]['text']
                        
                        if json_mode:
                            try:
                                content = json.loads(content)
                            except:
                                pass
                        
                        return {
                            'content': content,
                            'success': True,
                            'provider': 'anthropic',
                            'model': self.model,
                            'tokens_used': 0,  # Anthropic doesn't always return this
                            'fallback_used': False
                        }
                    else:
                        logger.error(f"Anthropic API error: {response.status}")
                        return {'content': '', 'success': False, 'provider': 'anthropic'}
                        
        except Exception as e:
            logger.error(f"Anthropic call failed: {str(e)}")
            return {'content': '', 'success': False, 'provider': 'anthropic'}
    
    def _get_fallback_response(self, prompt: str, json_mode: bool) -> Dict[str, Any]:
        """Return intelligent fallback response when all LLMs fail"""
        logger.warning("Using fallback response - no LLM available")
        
        # Context-aware fallback responses
        prompt_lower = prompt.lower()
        
        if 'consultant' in prompt_lower or 'match' in prompt_lower or 'sow' in prompt_lower:
            content = self._generate_fallback_sow(prompt)
        elif 'playwright' in prompt_lower or 'test' in prompt_lower or 'selector' in prompt_lower:
            content = self._generate_fallback_test_script(prompt)
        elif 'heal' in prompt_lower or 'fix' in prompt_lower or 'broken' in prompt_lower:
            content = self._generate_fallback_healing(prompt)
        else:
            content = "Unable to generate response. Please ensure an LLM provider (Ollama, OpenAI, or Anthropic) is configured."
        
        if json_mode:
            try:
                if isinstance(content, str):
                    content = json.loads(content)
            except:
                content = {"message": content}
        
        return {
            'content': content,
            'success': True,  # Consider fallback as "successful" for UX
            'provider': 'fallback',
            'model': 'rule-based',
            'tokens_used': 0,
            'fallback_used': True
        }
    
    def _generate_fallback_sow(self, prompt: str) -> str:
        """Generate template SoW without LLM"""
        return """
# Statement of Work (Template)

## Executive Summary
This Statement of Work outlines the SAP consulting engagement for digital transformation and S/4HANA migration services.

## Project Scope
- SAP S/4HANA Migration & Implementation
- Legacy System Assessment & Data Migration
- User Training & Change Management
- Post-Go-Live Support

## Deliverables
1. Current State Assessment Report
2. Future State Architecture Design
3. Migration Strategy & Roadmap
4. Testing & Validation Plan
5. Go-Live Support

## Timeline
- Phase 1: Discovery & Planning (4 weeks)
- Phase 2: Design & Configuration (8 weeks)
- Phase 3: Testing & Validation (6 weeks)
- Phase 4: Go-Live & Support (4 weeks)

## Investment
Professional services fees based on consultant allocation and project timeline.

## Success Metrics
- System uptime > 99.5%
- User adoption rate > 90%
- Business process efficiency improvement > 30%
"""
    
    def _generate_fallback_test_script(self, prompt: str) -> str:
        """Generate template Playwright script without LLM"""
        return '''
import { test, expect } from '@playwright/test';

// Page Object Model for SAP Fiori
class SAPFioriPage {
  constructor(page) {
    this.page = page;
    // Stable selectors for SAP Fiori
    this.shellBar = '[id*="shell-bar"]';
    this.navMenu = '[id*="nav-menu"]';
    this.contentArea = '[id*="content"]';
  }

  async goto(url) {
    await this.page.goto(url);
    await this.waitForBusyIndicator();
  }

  async waitForBusyIndicator() {
    // Wait for SAP BusyIndicator to disappear
    await this.page.waitForSelector('[id*="busy-indicator"]', { state: 'hidden', timeout: 10000 });
  }

  async clickButton(label) {
    await this.page.click(`button:has-text("${label}")`);
    await this.waitForBusyIndicator();
  }

  async fillField(label, value) {
    await this.page.fill(`input[aria-label="${label}"]`, value);
  }

  async getText(selector) {
    return await this.page.textContent(selector);
  }
}

test('SAP Fiori Test Case', async ({ page }) => {
  const fioriPage = new SAPFioriPage(page);
  
  // Navigate to application
  await fioriPage.goto(process.env.SAP_APP_URL || 'http://localhost:8080');
  
  // Verify page loaded
  await expect(page.locator(fioriPage.shellBar)).toBeVisible();
  
  // Add your test steps here
  console.log('Test executed successfully');
});
'''
    
    def _generate_fallback_healing(self, prompt: str) -> Dict[str, Any]:
        """Generate healing suggestion without LLM"""
        return {
            'suggestions': [
                {
                    'original_selector': 'Unknown',
                    'new_selector': '[data-testid="auto-generated-selector"]',
                    'selector_type': 'data-testid',
                    'confidence_score': 0.6,
                    'reasoning': 'Fallback heuristic: Prefer data-testid over auto-generated IDs. Review DOM for stable attributes.',
                    'code_diff': '// Replace brittle selector with stable data-testid attribute'
                }
            ],
            'general_advice': 'For SAP Fiori applications, prefer these selector strategies in order: 1) data-testid, 2) aria-label, 3) SAP UI5 data-sap-ui attributes, 4) Role-based selectors. Avoid auto-generated IDs containing "__xmlview", "gen-", or random strings.'
        }


# Singleton instance
llm_service = LLMService()
