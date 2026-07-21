"""
SAP TestOS - SQLAlchemy Models
Database models with async support
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.schemas.responses import SAPModule
import enum


class AvailabilityStatus(str, enum.Enum):
    """Consultant availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"


class Consultant(Base):
    """Consultant profile model"""
    __tablename__ = "consultants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    modules = Column(JSON, nullable=False)  # List of SAP modules
    years_experience = Column(Integer, nullable=False)
    hourly_rate = Column(Float, nullable=False)
    certifications = Column(JSON, default=list)
    availability = Column(SQLEnum(AvailabilityStatus), default=AvailabilityStatus.AVAILABLE)
    location = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("ProjectAssignment", back_populates="consultant")
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "modules": self.modules,
            "years_experience": self.years_experience,
            "hourly_rate": self.hourly_rate,
            "certifications": self.certifications,
            "availability": self.availability.value if self.availability else "available",
            "location": self.location,
            "bio": self.bio,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Project(Base):
    """Project/Engagement model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    client_name = Column(String(255), nullable=False)
    required_modules = Column(JSON, default=list)
    status = Column(String(50), default="active")  # active, completed, cancelled
    budget_usd = Column(Float, nullable=True)
    timeline_weeks = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assignments = relationship("ProjectAssignment", back_populates="project")
    sow_documents = relationship("SowDocument", back_populates="project")


class ProjectAssignment(Base):
    """Consultant-Project assignment mapping"""
    __tablename__ = "project_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    consultant_id = Column(Integer, ForeignKey("consultants.id"), nullable=False)
    role = Column(String(100), nullable=False)
    allocation_percentage = Column(Integer, default=100)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="assignments")
    consultant = relationship("Consultant", back_populates="projects")


class SowDocument(Base):
    """Statement of Work document model"""
    __tablename__ = "sow_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    document_content = Column(Text, nullable=False)
    executive_summary = Column(Text, nullable=False)
    team_composition = Column(JSON, default=list)
    estimated_cost = Column(Float, nullable=True)
    timeline_milestones = Column(JSON, default=list)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="sow_documents")


class AutomatedTest(Base):
    """Automated test script model"""
    __tablename__ = "automated_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    module = Column(String(50), nullable=False)
    original_manual_test = Column(JSON, nullable=True)
    playwright_script = Column(Text, nullable=False)
    page_objects = Column(JSON, default=dict)
    selectors_used = Column(JSON, default=list)
    confidence_score = Column(Float, default=1.0)
    last_run_status = Column(String(50), default="pending")  # pending, passed, failed
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TestHealingLog(Base):
    """Log of test healing operations"""
    __tablename__ = "test_healing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(100), nullable=False, index=True)
    original_selector = Column(String(500), nullable=False)
    new_selector = Column(String(500), nullable=False)
    selector_type = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)
    code_diff = Column(Text, nullable=False)
    applied_automatically = Column(Integer, default=0)  # boolean as int
    healing_timestamp = Column(DateTime(timezone=True), server_default=func.now())
