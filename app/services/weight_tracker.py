"""Weight tracking service layer"""
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from app.db.models import WeightEntry
from app.services.calculator import kg_to_lb, lb_to_kg


def create_weight_entry(
    db: Session,
    date: datetime,
    weight: float,
    unit: str,
    notes: Optional[str] = None
) -> WeightEntry:
    """
    Create a new weight entry

    Args:
        db: Database session
        date: Date of measurement
        weight: Weight value
        unit: 'kg' or 'lb'
        notes: Optional notes

    Returns:
        Created WeightEntry

    Raises:
        ValueError: If date is in the future or weight is invalid
    """
    # Validate date is not in the future
    if date > datetime.now(timezone.utc):
        raise ValueError("Date cannot be in the future")

    # Convert to kg for storage
    weight_kg = weight if unit == 'kg' else lb_to_kg(weight)

    entry = WeightEntry(
        date=date,
        weight_kg=weight_kg,
        notes=notes
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_all_weight_entries(db: Session) -> List[WeightEntry]:
    """
    Get all weight entries ordered by date (oldest first)

    Args:
        db: Database session

    Returns:
        List of WeightEntry objects
    """
    return db.query(WeightEntry).order_by(WeightEntry.date).all()


def get_weight_entry_by_id(db: Session, entry_id: int) -> Optional[WeightEntry]:
    """
    Get a weight entry by ID

    Args:
        db: Database session
        entry_id: Entry ID

    Returns:
        WeightEntry or None if not found
    """
    return db.query(WeightEntry).filter(WeightEntry.id == entry_id).first()


def update_weight_entry(
    db: Session,
    entry_id: int,
    date: Optional[datetime] = None,
    weight: Optional[float] = None,
    unit: Optional[str] = None,
    notes: Optional[str] = None
) -> Optional[WeightEntry]:
    """
    Update a weight entry

    Args:
        db: Database session
        entry_id: Entry ID
        date: New date (optional)
        weight: New weight value (optional)
        unit: Unit for new weight (optional)
        notes: New notes (optional)

    Returns:
        Updated WeightEntry or None if not found

    Raises:
        ValueError: If date is in the future
    """
    entry = get_weight_entry_by_id(db, entry_id)
    if not entry:
        return None

    if date is not None:
        if date > datetime.now(timezone.utc):
            raise ValueError("Date cannot be in the future")
        entry.date = date

    if weight is not None and unit is not None:
        entry.weight_kg = weight if unit == 'kg' else lb_to_kg(weight)

    if notes is not None:
        entry.notes = notes

    db.commit()
    db.refresh(entry)
    return entry


def delete_weight_entry(db: Session, entry_id: int) -> bool:
    """
    Delete a weight entry

    Args:
        db: Database session
        entry_id: Entry ID

    Returns:
        True if deleted, False if not found
    """
    entry = get_weight_entry_by_id(db, entry_id)
    if not entry:
        return False

    db.delete(entry)
    db.commit()
    return True
