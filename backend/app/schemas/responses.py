"""
SAP TestOS - Pydantic Schemas
Request/Response models for API validation
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============== MATCHMAKER SCHEMAS ==============

class SAPModule(str, Enum):
    """SAP Module Enumeration"""
    FICO = "FICO"
    MM = "MM"
    SD = "SD"
    PP = "PP"
    QM = "QM"
    PM = "PM"
    PS = "PS"
    BW = "BW"
    BI = "BI"
    S4HANA = "S/4HANA"
    FIORI = "Fiori"
    BASIS = "Basis"
    SUCCESSFACTORS = "SuccessFactors"
    ARIBA = "Ariba"
    CONCUR = "Concur"


class ConsultantBase(BaseModel):
    """Base consultant schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    modules: List[SAPModule]
    years_experience: int = Field(..., ge=0, le=30)
    hourly_rate: float = Field(..., ge=0)
    certifications: List[str] = []
    availability: str = "available"  # available, busy, unavailable
    location: Optional[str] = None
    bio: Optional[str] = None


class ConsultantCreate(ConsultantBase):
    """Schema for creating a consultant"""
    pass


class ConsultantResponse(ConsultantBase):
    """Schema for consultant response"""
    id: int
    match_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class MatchRequest(BaseModel):
    """Request schema for consultant matching"""
    project_description: str = Field(..., min_length=10, max_length=5000)
    required_modules: List[SAPModule] = []
    min_experience: int = Field(default=0, ge=0, le=30)
    max_hourly_rate: Optional[float] = None
    limit: int = Field(default=10, ge=1, le=50)


class MatchResponse(BaseModel):
    """Response schema for consultant matching"""
    consultants: List[ConsultantResponse]
    total_matches: int
    search_metadata: Dict[str, Any] = {}


class SowGenerationRequest(BaseModel):
    """Request schema for SoW generation"""
    client_name: str
    project_title: str
    project_description: str
    selected_consultants: List[int]  # Consultant IDs
    timeline_weeks: int = Field(default=12, ge=1, le=104)
    budget_usd: Optional[float] = None


class SowGenerationResponse(BaseModel):
    """Response schema for SoW generation"""
    statement_of_work: str
    executive_summary: str
    team_composition: List[Dict[str, Any]]
    estimated_cost: float
    timeline_milestones: List[Dict[str, Any]]
    generated_at: datetime


# ============== VLM AGENT SCHEMAS ==============

class TestStep(BaseModel):
    """Individual test step"""
    step_number: int
    action: str
    expected_result: str


class ManualTest(BaseModel):
    """Manual test case"""
    test_id: str
    title: str
    description: str
    module: SAPModule
    steps: List[TestStep]
    preconditions: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None


class ManualTestCreate(BaseModel):
    """Schema for creating manual test"""
    test_id: Optional[str] = None
    title: str
    description: str
    module: SAPModule
    steps: List[TestStep]
    preconditions: Optional[str] = None


class PlaywrightScript(BaseModel):
    """Generated Playwright script"""
    script_code: str
    page_objects: Dict[str, str]
    test_file_name: str
    estimated_execution_time_seconds: int
    selectors_used: List[str]
    confidence_score: float = Field(ge=0, le=1)


class ConversionRequest(BaseModel):
    """Request for test conversion"""
    manual_tests: List[ManualTestCreate]
    target_url: str
    include_pom: bool = True
    add_assertions: bool = True


class ConversionResponse(BaseModel):
    """Response for test conversion"""
    scripts: List[PlaywrightScript]
    total_steps_converted: int
    warnings: List[str] = []
    processing_time_ms: int


# ============== SELF-HEALING SCHEMAS ==============

class TestFailure(BaseModel):
    """Test failure information"""
    test_file: str
    test_name: str
    error_message: str
    line_number: Optional[int] = None
    selector_used: Optional[str] = None
    screenshot_path: Optional[str] = None
    dom_snapshot: Optional[str] = None


class HealingSuggestion(BaseModel):
    """Proposed fix for broken test"""
    original_selector: str
    new_selector: str
    selector_type: str  # css, xpath, data-testid, etc.
    confidence_score: float
    reasoning: str
    code_diff: str


class HealingRequest(BaseModel):
    """Request for test healing"""
    failures: List[TestFailure]
    application_url: str
    auto_apply: bool = False


class HealingResponse(BaseModel):
    """Response for test healing"""
    healed_scripts: List[Dict[str, Any]]
    suggestions: List[HealingSuggestion]
    success_rate: float
    total_failures_analyzed: int
    total_healed: int
    processing_time_ms: int


# ============== COMMON SCHEMAS ==============

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    services: Dict[str, str]
    timestamp: datetime


class StatsResponse(BaseModel):
    """Statistics response"""
    total_consultants: int
    active_projects: int
    tests_automated: int
    tests_healed: int
    maintenance_hours_saved: int
    avg_match_accuracy: float


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
