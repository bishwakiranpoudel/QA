"""
SAP TestOS - Self-Healing API Routes
Endpoints for automated test healing
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.responses import (
    HealingRequest, HealingResponse, TestFailure
)
from app.services.self_healing_service import get_self_healing_service, SelfHealingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/self-healing", tags=["Self-Healing"])


@router.post("/analyze-and-heal", response_model=HealingResponse)
async def analyze_and_heal(request: HealingRequest):
    """
    Analyze test failures and propose/apply fixes.
    Uses AST-based surgical patching to preserve business logic.
    """
    try:
        service = get_self_healing_service()
        result = await service.analyze_and_heal(request)
        return result
    except Exception as e:
        logger.error(f"Self-healing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-check")
async def health_check():
    """Check self-healing service status"""
    return {
        "status": "operational",
        "service": "self-healing",
        "version": "1.0.0"
    }


@router.get("/statistics")
async def get_statistics():
    """Get healing operation statistics"""
    service = get_self_healing_service()
    stats = await service.get_healing_statistics()
    return stats


@router.post("/suggest-fix")
async def suggest_fix(failure: TestFailure):
    """Get healing suggestion for a single failure"""
    try:
        service = get_self_healing_service()
        
        # Create minimal request
        request = HealingRequest(
            failures=[failure],
            application_url="http://sap-app.local",
            auto_apply=False
        )
        
        result = await service.analyze_and_heal(request)
        
        if result['suggestions']:
            return result['suggestions'][0]
        else:
            return {"error": "Could not generate suggestion"}
            
    except Exception as e:
        logger.error(f"Suggestion generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
