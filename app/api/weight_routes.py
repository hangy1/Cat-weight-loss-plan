"""Weight tracking API routes"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.weight_tracker import (
    WeightEntryCreate,
    WeightEntryUpdate,
    WeightEntryResponse,
    WeightEntryList
)
from app.services.weight_tracker import (
    create_weight_entry,
    get_all_weight_entries,
    get_weight_entry_by_id,
    update_weight_entry,
    delete_weight_entry
)
from app.services.calculator import kg_to_lb

router = APIRouter(prefix="/weight", tags=["Weight Tracking"])


def _to_response(entry) -> WeightEntryResponse:
    """Convert WeightEntry model to response schema"""
    return WeightEntryResponse(
        id=entry.id,
        date=entry.date,
        weight_kg=round(entry.weight_kg, 2),
        weight_lb=round(kg_to_lb(entry.weight_kg), 2),
        notes=entry.notes,
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )


@router.post("/entries", response_model=WeightEntryResponse, status_code=201)
def create_entry(data: WeightEntryCreate, db: Session = Depends(get_db)):
    """
    Create a new weight entry

    Validates that:
    - Weight is positive
    - Unit is 'kg' or 'lb'
    - Date is not in the future
    """
    if data.unit.lower() not in ['kg', 'lb']:
        raise HTTPException(
            status_code=400,
            detail="unit must be either 'kg' or 'lb'"
        )

    try:
        entry = create_weight_entry(
            db=db,
            date=data.date,
            weight=data.weight,
            unit=data.unit.lower(),
            notes=data.notes
        )
        return _to_response(entry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries", response_model=WeightEntryList)
def get_entries(db: Session = Depends(get_db)):
    """
    Get all weight entries sorted by date (chronological)

    Returns entries with both kg and lb values for display
    """
    try:
        entries = get_all_weight_entries(db)
        return WeightEntryList(
            entries=[_to_response(e) for e in entries],
            total=len(entries)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries/{entry_id}", response_model=WeightEntryResponse)
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a specific weight entry by ID"""
    entry = get_weight_entry_by_id(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Weight entry not found")
    return _to_response(entry)


@router.put("/entries/{entry_id}", response_model=WeightEntryResponse)
def update_entry(
    entry_id: int,
    data: WeightEntryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a weight entry

    Can update any combination of: date, weight, unit, notes
    """
    if data.unit and data.unit.lower() not in ['kg', 'lb']:
        raise HTTPException(
            status_code=400,
            detail="unit must be either 'kg' or 'lb'"
        )

    try:
        entry = update_weight_entry(
            db=db,
            entry_id=entry_id,
            date=data.date,
            weight=data.weight,
            unit=data.unit.lower() if data.unit else None,
            notes=data.notes
        )
        if not entry:
            raise HTTPException(status_code=404, detail="Weight entry not found")
        return _to_response(entry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/entries/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a weight entry"""
    try:
        success = delete_weight_entry(db, entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Weight entry not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
