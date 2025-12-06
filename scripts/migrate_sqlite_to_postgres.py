"""
Migration Script: SQLite to PostgreSQL
=======================================
This script migrates all data from the SQLite database to PostgreSQL.

Usage:
    python scripts/migrate_sqlite_to_postgres.py

Prerequisites:
    1. PostgreSQL server running with target database created
    2. Install psycopg2-binary: pip install psycopg2-binary
    3. Set POSTGRES_URL environment variable or edit the script

The script will:
    1. Connect to both databases
    2. Create all tables in PostgreSQL (if they don't exist)
    3. Copy all data from SQLite to PostgreSQL
    4. Preserve all relationships and foreign keys
"""

import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Import all models to ensure they're registered with Base
from backend.app.database import Base
from backend.app.models import User, Analysis, Section, Dataset, Dashboard, SavedQuery
from backend.app.models.dataset import DatasetShareLog, DatasetExportLog, dataset_shares


def get_postgres_url():
    """Get PostgreSQL URL from environment or prompt user"""
    postgres_url = os.environ.get("POSTGRES_URL")

    if not postgres_url:
        print("\n" + "="*60)
        print("PostgreSQL Connection Setup")
        print("="*60)
        print("\nEnter your PostgreSQL connection details:")

        host = input("  Host [localhost]: ").strip() or "localhost"
        port = input("  Port [5432]: ").strip() or "5432"
        database = input("  Database name [finexus]: ").strip() or "finexus"
        username = input("  Username [postgres]: ").strip() or "postgres"
        password = input("  Password: ").strip()

        postgres_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"

    return postgres_url


def migrate_table(sqlite_session, postgres_session, model_class, table_name):
    """Migrate a single table from SQLite to PostgreSQL"""
    print(f"\n  Migrating {table_name}...")

    # Get all records from SQLite
    records = sqlite_session.query(model_class).all()
    count = len(records)

    if count == 0:
        print(f"    -> No records to migrate")
        return 0

    # Get column names from the model
    mapper = inspect(model_class)
    columns = [column.key for column in mapper.columns]

    # Copy each record
    migrated = 0
    for record in records:
        # Create a dict of column values
        data = {col: getattr(record, col) for col in columns}

        # Create new instance for PostgreSQL
        new_record = model_class(**data)

        try:
            postgres_session.merge(new_record)
            migrated += 1
        except Exception as e:
            print(f"    -> Error migrating record: {e}")

    postgres_session.flush()
    print(f"    -> Migrated {migrated}/{count} records")
    return migrated


def migrate_association_table(sqlite_engine, postgres_engine, table):
    """Migrate association table (many-to-many)"""
    table_name = table.name
    print(f"\n  Migrating association table {table_name}...")

    with sqlite_engine.connect() as sqlite_conn:
        # Get all records
        result = sqlite_conn.execute(text(f"SELECT * FROM {table_name}"))
        rows = result.fetchall()
        columns = result.keys()

        if not rows:
            print(f"    -> No records to migrate")
            return 0

        with postgres_engine.connect() as pg_conn:
            migrated = 0
            for row in rows:
                # Build insert statement
                col_names = ", ".join(columns)
                placeholders = ", ".join([f":{col}" for col in columns])

                insert_sql = text(f"""
                    INSERT INTO {table_name} ({col_names})
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """)

                try:
                    pg_conn.execute(insert_sql, dict(zip(columns, row)))
                    migrated += 1
                except Exception as e:
                    print(f"    -> Error: {e}")

            pg_conn.commit()
            print(f"    -> Migrated {migrated}/{len(rows)} records")
            return migrated


def main():
    print("\n" + "="*60)
    print("  Finexus Database Migration: SQLite -> PostgreSQL")
    print("="*60)

    # SQLite connection
    sqlite_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "financial_analysis.db"
    )

    if not os.path.exists(sqlite_path):
        print(f"\nError: SQLite database not found at {sqlite_path}")
        sys.exit(1)

    sqlite_url = f"sqlite:///{sqlite_path}"
    print(f"\nSource (SQLite): {sqlite_path}")

    # PostgreSQL connection
    postgres_url = get_postgres_url()

    # Mask password in display
    display_url = postgres_url
    if "@" in postgres_url:
        parts = postgres_url.split("@")
        prefix = parts[0].rsplit(":", 1)[0]
        display_url = f"{prefix}:****@{parts[1]}"
    print(f"Target (PostgreSQL): {display_url}")

    # Create engines
    print("\nConnecting to databases...")

    try:
        sqlite_engine = create_engine(sqlite_url)
        SQLiteSession = sessionmaker(bind=sqlite_engine)
        sqlite_session = SQLiteSession()
        print("  -> SQLite connection successful")
    except Exception as e:
        print(f"  -> SQLite connection failed: {e}")
        sys.exit(1)

    try:
        postgres_engine = create_engine(postgres_url)
        # Test connection
        with postgres_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        PostgresSession = sessionmaker(bind=postgres_engine)
        postgres_session = PostgresSession()
        print("  -> PostgreSQL connection successful")
    except Exception as e:
        print(f"  -> PostgreSQL connection failed: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL server is running")
        print("  2. Database exists (create with: CREATE DATABASE finexus;)")
        print("  3. User has proper permissions")
        sys.exit(1)

    # Create tables in PostgreSQL
    print("\nCreating tables in PostgreSQL...")
    try:
        Base.metadata.create_all(bind=postgres_engine)
        print("  -> Tables created successfully")
    except Exception as e:
        print(f"  -> Error creating tables: {e}")
        sys.exit(1)

    # Migration order (respecting foreign key dependencies)
    # Users must be migrated first, then analyses, then sections
    migration_order = [
        (User, "users"),
        (Analysis, "analyses"),
        (Section, "sections"),
        (Dataset, "datasets"),
        (Dashboard, "dashboards"),
        (SavedQuery, "saved_queries"),
        (DatasetShareLog, "dataset_share_logs"),
        (DatasetExportLog, "dataset_export_logs"),
    ]

    print("\n" + "-"*60)
    print("Starting data migration...")
    print("-"*60)

    total_migrated = 0

    try:
        # Migrate main tables
        for model_class, table_name in migration_order:
            count = migrate_table(sqlite_session, postgres_session, model_class, table_name)
            total_migrated += count

        # Migrate association tables
        count = migrate_association_table(sqlite_engine, postgres_engine, dataset_shares)
        total_migrated += count

        # Commit all changes
        postgres_session.commit()

        print("\n" + "="*60)
        print(f"  Migration completed successfully!")
        print(f"  Total records migrated: {total_migrated}")
        print("="*60)

        # Verification
        print("\nVerification - Record counts in PostgreSQL:")
        for model_class, table_name in migration_order:
            count = postgres_session.query(model_class).count()
            print(f"  {table_name}: {count} records")

    except Exception as e:
        postgres_session.rollback()
        print(f"\nMigration failed: {e}")
        print("All changes have been rolled back.")
        sys.exit(1)

    finally:
        sqlite_session.close()
        postgres_session.close()

    print("\n" + "-"*60)
    print("Next steps:")
    print("-"*60)
    print("1. Update your .env file:")
    print(f'   DATABASE_URL="{postgres_url}"')
    print("\n2. Restart your FastAPI server")
    print("\n3. Test the application to verify data integrity")
    print("-"*60 + "\n")


if __name__ == "__main__":
    main()
