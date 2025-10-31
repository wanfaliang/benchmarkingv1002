"""
File: backend/scripts/migrate_dataset_tables.py

Run this to create the new tables:
python backend/scripts/migrate_dataset_tables.py
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent  # Go up 2 levels from scripts/
sys.path.insert(0, str(project_root))
from backend.app.database import engine, Base
from backend.app.models.dataset import Dataset, Dashboard, SavedQuery, DatasetShareLog, DatasetExportLog, dataset_shares

def create_dataset_tables():
    """Create all dataset-related tables"""
    print("Creating dataset tables...")
    Base.metadata.create_all(bind=engine, tables=[
        Dataset.__table__,
        Dashboard.__table__,
        SavedQuery.__table__,
        DatasetShareLog.__table__,
        DatasetExportLog.__table__,
        dataset_shares,
    ])
    print("✓ Dataset tables and shares created successfully!")


if __name__ == "__main__":
    create_dataset_tables()