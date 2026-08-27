from fastapi import APIRouter, Request, status
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/webhooks", tags=["Webhooks & Écosystème Maroc"])

class CMIWebhookPayload(BaseModel):
    cmi_trans_id: str
    amount: float
    status: str # APPROVED, DECLINED
    auth_code: str

@router.post("/cmi/callback", status_code=status.HTTP_200_OK)
async def cmi_payment_callback(payload: CMIWebhookPayload):
    # Process 3D-secure CMI notification
    return {"status": "SUCCESS", "message": "CMI Pre-authorization processed", "cmi_trans_id": payload.cmi_trans_id}

@router.post("/cashplus/deposit", status_code=status.HTTP_200_OK)
async def cashplus_deposit_webhook(request: Request):
    data = await request.json()
    return {"status": "ACK", "message": "CashPlus deposit received", "data": data}
