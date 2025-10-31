# scripts/update_saved_queries_table.py
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.database import engine
from backend.app.models.dataset import SavedQuery


def update_saved_queries_table():
    """Drop and recreate saved_queries table with nullable dataset_id"""
    print("Updating saved_queries table...")
    
    # Drop old table
    SavedQuery.__table__.drop(engine, checkfirst=True)
    print("  ✓ Dropped old table")
    
    # Create new table with updated schema
    SavedQuery.__table__.create(engine, checkfirst=True)
    print("  ✓ Created new table")
    
    print("✅ Migration complete!")


if __name__ == "__main__":
    update_saved_queries_table()