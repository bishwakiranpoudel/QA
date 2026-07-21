"""
SAP TestOS - VLM Agent API Routes
Endpoints for test automation conversion
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.responses import (
    ManualTestCreate, ConversionRequest, ConversionResponse,
    TestStep, SAPModule
)
from app.services.vlm_agent_service import get_vlm_agent_service, VLMAgentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vlm-agent", tags=["VLM Agent"])


@router.post("/convert", response_model=ConversionResponse)
async def convert_tests(request: ConversionRequest):
    """
    Convert manual test cases to Playwright automation scripts.
    Uses hybrid DOM + Vision approach optimized for SAP Fiori.
    """
    try:
        service = get_vlm_agent_service()
        result = await service.convert_manual_to_automated(request)
        return result
    except Exception as e:
        logger.error(f"Test conversion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample-manual-test")
async def get_sample_test():
    """Get a sample manual test case for testing"""
    return {
        "test_id": "SAMPLE_001",
        "title": "Create Sales Order",
        "description": "Test creating a new sales order in SAP SD module",
        "module": "SD",
        "steps": [
            {"step_number": 1, "action": "Navigate to Sales Order creation page", "expected_result": "Sales Order form is displayed"},
            {"step_number": 2, "action": "Enter customer ID 'CUST001'", "expected_result": "Customer details auto-populate"},
            {"step_number": 3, "action": "Add material 'MAT001' with quantity 10", "expected_result": "Material line item added"},
            {"step_number": 4, "action": "Click Save button", "expected_result": "Sales order created with confirmation message"},
        ],
        "preconditions": "User has SD role authorization",
        "test_data": {"customer_id": "CUST001", "material_id": "MAT001", "quantity": 10}
    }


@router.post("/batch-convert")
async def batch_convert(request: List[ManualTestCreate]):
    """Convert multiple manual tests in batch"""
    try:
        service = get_vlm_agent_service()
        conv_request = ConversionRequest(
            manual_tests=request,
            target_url="http://sap-fiori-app.local",
            include_pom=True,
            add_assertions=True
        )
        result = await service.convert_manual_to_automated(conv_request)
        return result
    except Exception as e:
        logger.error(f"Batch conversion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
