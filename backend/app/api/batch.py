import json
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.ticket import TicketCreateSchema
from app.services.ticket_service import TicketService
from app.api.deps import require_roles
from app.models.user import User
from typing import List

router = APIRouter(prefix="/api/batch", tags=["Batch Ingest"])

@router.post("/ingest")
def ingest_batch_payloads(
    tickets: List[TicketCreateSchema],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"]))
):
    service = TicketService(db)
    results = []
    for payload in tickets:
        res = service.process_incoming_ticket(payload)
        results.append(res)
    return {"status": "success", "ingested_count": len(results), "results": results}

@router.post("/ingest-sample-data")
def ingest_sample_data_file(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"]))
):
    sample_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "sample_data", "tickets_batch.json")
    if not os.path.exists(sample_file_path):
        raise HTTPException(status_code=404, detail="sample_data/tickets_batch.json file not found")
    
    with open(sample_file_path, "r", encoding="utf-8") as f:
        tickets_raw = json.load(f)

    service = TicketService(db)
    results = []
    for raw in tickets_raw:
        payload = TicketCreateSchema(**raw)
        res = service.process_incoming_ticket(payload)
        results.append(res)

    return {"status": "success", "ingested_count": len(results), "results": results}
