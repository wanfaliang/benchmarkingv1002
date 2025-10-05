"""Initialize database - create all tables"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from backend.app.database import engine, Base
from backend.app.models import User, Analysis, Section

def init_database():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    # Print created tables
    print("\nCreated tables:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == "__main__":
    init_database()