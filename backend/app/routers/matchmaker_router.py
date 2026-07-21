"""
SAP TestOS - Matchmaker API Routes
Endpoints for consultant matching and SoW generation
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.responses import (
    ConsultantResponse, MatchRequest, MatchResponse,
    SowGenerationRequest, SowGenerationResponse,
    HealthResponse, StatsResponse
)
from app.services.matchmaker_service import get_matchmaker_service, MatchmakerService
from app.repositories.consultant_repository import ConsultantRepository
from app.models.entities import Consultant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matchmaker", tags=["Matchmaker"])


@router.get("/consultants", response_model=List[ConsultantResponse])
async def get_consultants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    availability: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    db=Depends(get_db)
):
    """Get all consultants with optional filters"""
    repo = ConsultantRepository(db)
    
    filters = {}
    if availability:
        filters['availability'] = availability
    
    consultants = await repo.get_all(skip=skip, limit=limit, filters=filters)
    
    # If module filter provided, do in-memory filtering
    if module:
        filtered = []
        for c in consultants:
            if module.lower() in [m.lower() for m in (c.modules or [])]:
                filtered.append(c)
        consultants = filtered
    
    return consultants


@router.post("/match", response_model=MatchResponse)
async def match_consultants(
    request: MatchRequest,
    db=Depends(get_db)
):
    """
    Find best matching consultants for a project.
    Uses intelligent multi-factor scoring algorithm.
    """
    try:
        service = get_matchmaker_service(db)
        result = await service.find_matching_consultants(request)
        return result
    except Exception as e:
        logger.error(f"Matching failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-sow", response_model=SowGenerationResponse)
async def generate_sow(
    request: SowGenerationRequest,
    db=Depends(get_db)
):
    """
    Generate professional Statement of Work document.
    Requires selected consultant IDs.
    """
    try:
        service = get_matchmaker_service(db)
        result = await service.generate_statement_of_work(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"SoW generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats(db=Depends(get_db)):
    """Get consultant statistics"""
    repo = ConsultantRepository(db)
    stats = await repo.get_statistics()
    return stats
