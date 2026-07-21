"""
SAP TestOS - Consultant Repository
Specialized repository for consultant operations with matching logic
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.models.entities import Consultant, AvailabilityStatus
from app.repositories.base import BaseRepository
from app.schemas.responses import SAPModule


class ConsultantRepository(BaseRepository[Consultant]):
    """Repository for consultant-specific operations"""
    
    def __init__(self, db_session: AsyncSession):
        super().__init__(Consultant, db_session)
    
    async def find_by_modules(
        self, 
        modules: List[SAPModule],
        min_experience: int = 0,
        max_hourly_rate: Optional[float] = None,
        availability: Optional[str] = "available",
        limit: int = 50
    ) -> List[Consultant]:
        """Find consultants by SAP modules with filters"""
        # Convert enum to string values for JSON comparison
        module_values = [m.value if hasattr(m, 'value') else str(m) for m in modules]
        
        query = select(self.model)
        
        # Filter by availability
        if availability:
            query = query.where(self.model.availability == AvailabilityStatus(availability))
        
        # Filter by minimum experience
        query = query.where(self.model.years_experience >= min_experience)
        
        # Filter by max hourly rate
        if max_hourly_rate is not None:
            query = query.where(self.model.hourly_rate <= max_hourly_rate)
        
        # Filter by modules (JSON contains check)
        # Note: SQLite JSON support is limited, we'll filter in memory for MVP
        result = await self.db_session.execute(query.limit(limit * 2))  # Get more for in-memory filtering
        consultants = list(result.scalars().all())
        
        # In-memory module filtering (better for MVP with SQLite)
        filtered = []
        for consultant in consultants:
            consultant_modules = consultant.modules or []
            if any(mod in consultant_modules for mod in module_values):
                filtered.append(consultant)
        
        return filtered[:limit]
    
    async def calculate_match_score(
        self, 
        consultant: Consultant,
        required_modules: List[SAPModule],
        project_description: str
    ) -> float:
        """
        Calculate match score based on multiple factors:
        - Skill match (40%): Module alignment
        - Experience fit (30%): Years of experience relevance
        - Certification bonus (15%): Relevant certifications
        - Rate efficiency (10%): Cost effectiveness
        - Availability (5%): Immediate availability
        """
        score = 0.0
        
        # Module match (40%)
        consultant_modules = set(consultant.modules or [])
        required_module_set = {m.value if hasattr(m, 'value') else str(m) for m in required_modules}
        
        if required_module_set:
            matched_modules = len(consultant_modules.intersection(required_module_set))
            module_score = (matched_modules / len(required_module_set)) * 40
        else:
            # If no specific modules, check keyword match in bio
            module_score = 20  # Base score
            if consultant.bio:
                bio_lower = consultant.bio.lower()
                if any(keyword in bio_lower for keyword in ['sap', 's/4hana', 'fiori']):
                    module_score = 30
        
        score += module_score
        
        # Experience fit (30%)
        exp_years = consultant.years_experience or 0
        if exp_years >= 8:
            score += 30
        elif exp_years >= 5:
            score += 25
        elif exp_years >= 3:
            score += 20
        elif exp_years >= 1:
            score += 15
        else:
            score += 10
        
        # Certification bonus (15%)
        certifications = consultant.certifications or []
        relevant_certs = ['S/4HANA', 'FICO', 'MM', 'SD', 'Fiori', 'Basis', 'SuccessFactors']
        cert_matches = sum(1 for cert in certifications if any(rc in cert for rc in relevant_certs))
        cert_score = min(cert_matches * 5, 15)  # Max 15 points
        score += cert_score
        
        # Rate efficiency (10%) - lower rates get higher scores
        hourly_rate = consultant.hourly_rate or 100
        if hourly_rate <= 80:
            score += 10
        elif hourly_rate <= 120:
            score += 7
        elif hourly_rate <= 150:
            score += 5
        else:
            score += 2
        
        # Availability (5%)
        if consultant.availability == AvailabilityStatus.AVAILABLE:
            score += 5
        elif consultant.availability == AvailabilityStatus.BUSY:
            score += 2
        
        return min(score, 100.0)  # Cap at 100
    
    async def search_by_keyword(
        self, 
        keyword: str, 
        limit: int = 20
    ) -> List[Consultant]:
        """Search consultants by keyword in name, bio, or certifications"""
        consultants = await self.search(
            search_term=keyword,
            search_fields=['name', 'bio'],
            limit=limit * 2
        )
        
        # Additional in-memory search in certifications
        keyword_lower = keyword.lower()
        for consultant in consultants:
            certs = consultant.certifications or []
            if any(keyword_lower in cert.lower() for cert in certs):
                if consultant not in consultants:
                    consultants.append(consultant)
        
        return consultants[:limit]
    
    async def get_available_consultants(self, limit: int = 50) -> List[Consultant]:
        """Get all available consultants"""
        return await self.get_all(
            filters={'availability': AvailabilityStatus.AVAILABLE},
            limit=limit
        )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get consultant statistics"""
        total = await self.count()
        available = await self.count({'availability': AvailabilityStatus.AVAILABLE})
        busy = await self.count({'availability': AvailabilityStatus.BUSY})
        
        # Get average hourly rate
        query = select(func.avg(self.model.hourly_rate))
        result = await self.db_session.execute(query)
        avg_rate = result.scalar() or 0
        
        # Get average experience
        query = select(func.avg(self.model.years_experience))
        result = await self.db_session.execute(query)
        avg_exp = result.scalar() or 0
        
        return {
            'total_consultants': total,
            'available': available,
            'busy': busy,
            'unavailable': total - available - busy,
            'average_hourly_rate': round(avg_rate, 2),
            'average_experience_years': round(avg_exp, 1)
        }
