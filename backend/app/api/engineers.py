from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.engineer_repository import EngineerRepository
from app.schemas.engineer import EngineerStatusUpdateSchema
from app.api.deps import require_roles
from app.models.user import User

router = APIRouter(prefix="/api/engineers", tags=["Engineers"])

@router.get("")
def list_engineers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SUPPORT", "ADMIN"]))
):
    repo = EngineerRepository(db)
    return repo.get_all()

@router.patch("/{agent_id}/availability")
def toggle_availability(
    agent_id: str,
    payload: EngineerStatusUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"]))
):
    repo = EngineerRepository(db)
    eng = repo.set_availability(agent_id, payload.is_available)
    if not eng:
        raise HTTPException(status_code=404, detail="Engineer not found")
    return {"status": "success", "agent_id": agent_id, "is_available": eng.is_available}
