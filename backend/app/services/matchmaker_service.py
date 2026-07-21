"""
SAP TestOS - Matchmaker Service
Intelligent consultant matching and SoW generation
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.llm_service import llm_service
from app.repositories.consultant_repository import ConsultantRepository
from app.schemas.responses import SAPModule, MatchRequest, SowGenerationRequest
from app.core.config import settings

logger = logging.getLogger(__name__)


class MatchmakerService:
    """
    Service for intelligent consultant matching and Statement of Work generation.
    Implements hybrid search combining keyword matching with semantic scoring.
    """
    
    # SAP Module synonym mapping for intelligent keyword extraction
    MODULE_SYNONYMS = {
        'FICO': ['finance', 'accounting', 'financial', 'controlling', 'fico'],
        'MM': ['materials', 'procurement', 'purchasing', 'inventory', 'mm'],
        'SD': ['sales', 'distribution', 'order', 'customer', 'sd'],
        'PP': ['production', 'planning', 'manufacturing', 'pp'],
        'QM': ['quality', 'assurance', 'inspection', 'qm'],
        'PM': ['plant', 'maintenance', 'equipment', 'pm'],
        'PS': ['project', 'systems', 'ps'],
        'BW': ['business', 'warehouse', 'bw', 'data warehousing'],
        'BI': ['business', 'intelligence', 'analytics', 'reporting', 'bi'],
        'S/4HANA': ['s/4hana', 's4hana', 's4 hana', 'next-gen', 'next generation'],
        'Fiori': ['fiori', 'ux', 'user experience', 'web dynpro'],
        'Basis': ['basis', 'infrastructure', 'system admin', 'technical'],
        'SuccessFactors': ['successfactors', 'success factors', 'hr', 'human capital', 'hcm'],
        'Ariba': ['ariba', 'sourcing', 'procurement', 'supplier'],
        'Concur': ['concur', 'travel', 'expense']
    }
    
    def __init__(self, db_session):
        self.consultant_repo = ConsultantRepository(db_session)
    
    async def find_matching_consultants(self, request: MatchRequest) -> List[Dict[str, Any]]:
        """
        Find consultants matching project requirements using multi-factor scoring.
        
        Algorithm:
        1. Extract required modules from project description
        2. Filter consultants by availability and basic criteria
        3. Calculate match scores using weighted factors
        4. Sort and return top matches
        """
        start_time = datetime.now()
        
        # Step 1: Extract modules from project description if not provided
        required_modules = request.required_modules
        if not required_modules:
            required_modules = await self._extract_modules_from_description(
                request.project_description
            )
        
        logger.info(f"Searching for consultants with modules: {[m.value for m in required_modules]}")
        
        # Step 2: Get candidate consultants
        candidates = await self.consultant_repo.find_by_modules(
            modules=required_modules,
            min_experience=request.min_experience,
            max_hourly_rate=request.max_hourly_rate,
            limit=request.limit * 2  # Get more for scoring
        )
        
        # Step 3: Calculate match scores
        scored_consultants = []
        for consultant in candidates:
            score = await self.consultant_repo.calculate_match_score(
                consultant=consultant,
                required_modules=required_modules,
                project_description=request.project_description
            )
            
            consultant_dict = consultant.to_dict()
            consultant_dict['match_score'] = round(score, 2)
            scored_consultants.append(consultant_dict)
        
        # Step 4: Sort by score and limit results
        scored_consultants.sort(key=lambda x: x['match_score'], reverse=True)
        matched_consultants = scored_consultants[:request.limit]
        
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.info(f"Found {len(matched_consultants)} matches in {elapsed_ms:.2f}ms")
        
        return {
            'consultants': matched_consultants,
            'total_matches': len(matched_consultants),
            'search_metadata': {
                'required_modules': [m.value for m in required_modules],
                'min_experience': request.min_experience,
                'max_hourly_rate': request.max_hourly_rate,
                'processing_time_ms': round(elapsed_ms, 2),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    async def _extract_modules_from_description(self, description: str) -> List[SAPModule]:
        """Extract SAP modules from project description using keyword matching"""
        description_lower = description.lower()
        detected_modules = []
        
        for module, synonyms in self.MODULE_SYNONYMS.items():
            if any(synonym in description_lower for synonym in synonyms):
                try:
                    detected_modules.append(SAPModule(module))
                except ValueError:
                    continue
        
        # Fallback: if no modules detected, return all as potential match
        if not detected_modules:
            logger.warning("No SAP modules detected in description, using broad search")
            detected_modules = list(SAPModule)[:5]  # Default to first 5 modules
        
        return detected_modules
    
    async def generate_statement_of_work(self, request: SowGenerationRequest) -> Dict[str, Any]:
        """
        Generate professional Statement of Work document.
        Uses LLM when available, falls back to template otherwise.
        """
        start_time = datetime.now()
        
        # Get consultant details
        consultants_data = []
        for consultant_id in request.selected_consultants:
            consultant = await self.consultant_repo.get(consultant_id)
            if consultant:
                consultants_data.append({
                    'id': consultant.id,
                    'name': consultant.name,
                    'modules': consultant.modules,
                    'years_experience': consultant.years_experience,
                    'hourly_rate': consultant.hourly_rate,
                    'role': self._infer_role(consultant, request.project_description)
                })
        
        if not consultants_data:
            raise ValueError("No valid consultants selected for SoW generation")
        
        # Build prompt for LLM
        system_prompt = """You are an expert SAP consulting proposal writer. 
        Generate a professional, detailed Statement of Work (SoW) document.
        Output MUST be valid JSON with these exact keys:
        - executive_summary: 2-3 paragraph overview
        - statement_of_work: Full detailed SoW content in markdown
        - team_composition: Array of team member objects with name, role, responsibilities, allocation
        - timeline_milestones: Array of milestone objects with phase, duration_weeks, deliverables
        - estimated_cost: Total project cost in USD"""
        
        prompt = f"""
        Generate a Statement of Work for:
        
        Client: {request.client_name}
        Project: {request.project_title}
        Description: {request.project_description}
        Timeline: {request.timeline_weeks} weeks
        Budget: ${request.budget_usd:,.2f} USD (if specified)
        
        Team:
        {self._format_team_for_prompt(consultants_data)}
        
        Include specific SAP S/4HANA migration phases, deliverables, success metrics, and risk mitigation.
        """
        
        # Call LLM service with fallback
        llm_result = await llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=True,
            max_tokens=4096
        )
        
        # Process response
        content = llm_result['content']
        
        # Ensure we have proper structure
        if isinstance(content, str):
            try:
                import json
                content = json.loads(content)
            except:
                content = self._structure_fallback_sow(content, consultants_data, request)
        
        # Calculate estimated cost if not provided
        if 'estimated_cost' not in content or not content['estimated_cost']:
            content['estimated_cost'] = self._calculate_estimated_cost(consultants_data, request.timeline_weeks)
        
        # Add metadata
        content['generated_at'] = datetime.now().isoformat()
        content['team_composition'] = content.get('team_composition', consultants_data)
        content['timeline_milestones'] = content.get('timeline_milestones', self._generate_default_milestones(request.timeline_weeks))
        
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.info(f"SoW generated in {elapsed_ms:.2f}ms using {llm_result['provider']}")
        
        return {
            'statement_of_work': content.get('statement_of_work', ''),
            'executive_summary': content.get('executive_summary', ''),
            'team_composition': content.get('team_composition', []),
            'estimated_cost': content.get('estimated_cost', 0),
            'timeline_milestones': content.get('timeline_milestones', []),
            'generated_at': content['generated_at'],
            'metadata': {
                'provider_used': llm_result['provider'],
                'fallback_used': llm_result.get('fallback_used', False),
                'processing_time_ms': round(elapsed_ms, 2)
            }
        }
    
    def _infer_role(self, consultant, project_description: str) -> str:
        """Infer consultant role based on modules and project"""
        modules = consultant.modules or []
        desc_lower = project_description.lower()
        
        if 'FICO' in modules or 'finance' in desc_lower:
            return "Lead Finance Consultant"
        elif 'MM' in modules or 'materials' in desc_lower:
            return "Supply Chain Consultant"
        elif 'SD' in modules or 'sales' in desc_lower:
            return "Sales & Distribution Consultant"
        elif 'Basis' in modules or 'technical' in desc_lower:
            return "Technical Architect"
        elif 'S/4HANA' in modules or 'migration' in desc_lower:
            return "S/4HANA Migration Lead"
        else:
            return "Senior SAP Consultant"
    
    def _format_team_for_prompt(self, consultants_data: List[Dict]) -> str:
        """Format team data for LLM prompt"""
        lines = []
        for c in consultants_data:
            lines.append(f"- {c['name']}: {c['role']} ({c['years_experience']} yrs exp, ${c['hourly_rate']}/hr)")
            lines.append(f"  Modules: {', '.join(c['modules'])}")
        return '\n'.join(lines)
    
    def _calculate_estimated_cost(self, consultants: List[Dict], timeline_weeks: int) -> float:
        """Calculate estimated project cost"""
        hours_per_week = 40
        total_cost = 0
        
        for consultant in consultants:
            hourly_rate = consultant.get('hourly_rate', 100)
            allocation = 100  # Assume full-time for MVP
            weekly_cost = hourly_rate * hours_per_week * (allocation / 100)
            total_cost += weekly_cost * timeline_weeks
        
        return round(total_cost, 2)
    
    def _generate_default_milestones(self, timeline_weeks: int) -> List[Dict[str, Any]]:
        """Generate default project milestones"""
        phase_duration = max(4, timeline_weeks // 4)
        
        return [
            {
                'phase': 'Phase 1: Discovery & Planning',
                'duration_weeks': phase_duration,
                'deliverables': ['Current State Assessment', 'Future State Design', 'Project Plan']
            },
            {
                'phase': 'Phase 2: Configuration & Development',
                'duration_weeks': phase_duration * 2,
                'deliverables': ['System Configuration', 'Custom Developments', 'Integration Setup']
            },
            {
                'phase': 'Phase 3: Testing & Validation',
                'duration_weeks': phase_duration,
                'deliverables': ['Unit Tests', 'Integration Tests', 'UAT Support', 'Performance Testing']
            },
            {
                'phase': 'Phase 4: Go-Live & Hypercare',
                'duration_weeks': phase_duration,
                'deliverables': ['Cutover Plan', 'Go-Live Support', 'Knowledge Transfer', 'Hypercare']
            }
        ]
    
    def _structure_fallback_sow(self, content: str, consultants: List[Dict], request: SowGenerationRequest) -> Dict:
        """Structure unstructured LLM/text response into proper format"""
        return {
            'executive_summary': f"This project involves {request.project_title} for {request.client_name}. The engagement will span {request.timeline_weeks} weeks focusing on SAP implementation and optimization.",
            'statement_of_work': content if content else self._get_template_sow(),
            'team_composition': consultants,
            'estimated_cost': self._calculate_estimated_cost(consultants, request.timeline_weeks),
            'timeline_milestones': self._generate_default_milestones(request.timeline_weeks)
        }
    
    def _get_template_sow(self) -> str:
        """Return template SoW content"""
        return """
# Statement of Work

## 1. Executive Summary
This Statement of Work defines the terms and deliverables for SAP consulting services.

## 2. Scope of Services
- SAP S/4HANA Migration
- Business Process Optimization
- Data Migration & Integration
- User Training & Change Management

## 3. Deliverables
1. Current State Assessment Report
2. Solution Design Document
3. Configured SAP Environment
4. Test Plans & Results
5. Go-Live Support

## 4. Timeline
Project duration as specified with phased delivery approach.

## 5. Investment
Professional services fees calculated based on team allocation and timeline.

## 6. Success Criteria
- System availability > 99.5%
- User adoption rate > 90%
- Business process efficiency improvement
"""


# Factory function
def get_matchmaker_service(db_session):
    return MatchmakerService(db_session)
