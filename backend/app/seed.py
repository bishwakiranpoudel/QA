"""
SAP TestOS - Database Seeder
Populates database with initial sample data
"""
import asyncio
import logging
from app.core.database import init_db, async_session_maker, engine, Base
from app.models.entities import Consultant, AvailabilityStatus

logger = logging.getLogger(__name__)


async def seed_database():
    """Seed database with sample consultants"""
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    sample_consultants = [
        {
            "name": "Maria Schmidt",
            "email": "maria.schmidt@saptestos.com",
            "modules": ["FICO", "S/4HANA"],
            "years_experience": 12,
            "hourly_rate": 150.00,
            "certifications": ["SAP S/4HANA Finance", "SAP FICO Certified"],
            "availability": AvailabilityStatus.AVAILABLE,
            "location": "Munich, Germany",
            "bio": "Senior SAP Finance consultant specializing in S/4HANA migrations for manufacturing clients."
        },
        {
            "name": "Raj Patel",
            "email": "raj.patel@saptestos.com",
            "modules": ["MM", "Ariba", "S/4HANA"],
            "years_experience": 8,
            "hourly_rate": 120.00,
            "certifications": ["SAP MM Certified", "Ariba Sourcing"],
            "availability": AvailabilityStatus.AVAILABLE,
            "location": "Bangalore, India",
            "bio": "Supply chain and procurement expert with extensive Ariba integration experience."
        },
        {
            "name": "Sophie Dubois",
            "email": "sophie.dubois@saptestos.com",
            "modules": ["SD", "Fiori", "S/4HANA"],
            "years_experience": 10,
            "hourly_rate": 140.00,
            "certifications": ["SAP SD Certified", "SAP Fiori Design"],
            "availability": AvailabilityStatus.BUSY,
            "location": "Paris, France",
            "bio": "Sales & Distribution specialist with strong UX/Fiori design background."
        },
        {
            "name": "James Wilson",
            "email": "james.wilson@saptestos.com",
            "modules": ["Basis", "S/4HANA", "BW"],
            "years_experience": 15,
            "hourly_rate": 160.00,
            "certifications": ["SAP Basis Administrator", "SAP BW/4HANA"],
            "availability": AvailabilityStatus.AVAILABLE,
            "location": "London, UK",
            "bio": "Technical architect with deep expertise in SAP infrastructure and migrations."
        },
        {
            "name": "Anna Kowalski",
            "email": "anna.kowalski@saptestos.com",
            "modules": ["PP", "QM", "S/4HANA"],
            "years_experience": 9,
            "hourly_rate": 130.00,
            "certifications": ["SAP PP Certified", "Lean Six Sigma"],
            "availability": AvailabilityStatus.AVAILABLE,
            "location": "Warsaw, Poland",
            "bio": "Production planning and quality management expert for discrete manufacturing."
        },
        {
            "name": "Carlos Rodriguez",
            "email": "carlos.rodriguez@saptestos.com",
            "modules": ["SuccessFactors", "Concur"],
            "years_experience": 7,
            "hourly_rate": 110.00,
            "certifications": ["SuccessFactors Employee Central", "Concur Travel"],
            "availability": AvailabilityStatus.AVAILABLE,
            "location": "Madrid, Spain",
            "bio": "HCM and travel management specialist with cloud implementation focus."
        },
        {
            "name": "Li Wei",
            "email": "li.wei@saptestos.com",
            "modules": ["BI", "BW", "S/4HANA"],
            "years_experience": 11,
            "hourly_rate": 135.00,
            "certifications": ["SAP BW/4HANA", "SAP Analytics Cloud"],
            "availability": AvailabilityStatus.BUSY,
            "location": "Shanghai, China",
            "bio": "Business intelligence and analytics expert with SAP Analytics Cloud specialization."
        },
        {
            "name": "Emma Thompson",
            "email": "emma.thompson@saptestos.com",
            "modules": ["PS", "PM", "S/4HANA"],
            "years_experience": 13,
            "hourly_rate": 145.00,
            "certifications": ["SAP PS Certified", "PMP"],
            "availability": AvailabilityStatus.AVAILABLE,
            "location": "Sydney, Australia",
            "bio": "Project systems and plant maintenance consultant for utilities and infrastructure."
        }
    ]
    
    # Insert consultants
    async with async_session_maker() as session:
        for consultant_data in sample_consultants:
            # Check if already exists
            from sqlalchemy import select
            
            result = await session.execute(
                select(Consultant).where(Consultant.email == consultant_data["email"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                consultant = Consultant(**consultant_data)
                session.add(consultant)
                logger.info(f"Added consultant: {consultant_data['name']}")
            else:
                logger.info(f"Consultant already exists: {consultant_data['name']}")
        
        await session.commit()
    
    logger.info("Database seeding completed")


if __name__ == "__main__":
    asyncio.run(seed_database())
