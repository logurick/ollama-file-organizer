from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import Category

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("")
def list_categories(db: Session = Depends(get_db)):
    items = db.scalars(select(Category).order_by(Category.category_id)).all()
    return [{"id": item.id, "category_id": item.category_id, "display_name": item.display_name, "destination_template": item.destination_template, "enabled": item.enabled} for item in items]
