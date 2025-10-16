"""
Database Migration Script - Add Google OAuth Fields
File: scripts/migrate_add_google_oauth.py

Run this script to add Google OAuth columns to existing database without losing data.
Usage: python scripts/migrate_add_google_oauth.py
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import from backend
sys.path.insert(0, str(Path(__file__).parent.parent))

def migrate_database():
    """Add Google OAuth fields to users table"""
    
    # Database path - matches your .env DATABASE_URL
    db_path = "financial_analysis.db"
    
    print(f"Starting migration on {db_path}...")
    print(f"Database location: {Path(db_path).absolute()}")
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"\n✗ Error: Database file '{db_path}' not found!")
        print("Please verify your DATABASE_URL setting in .env")
        sys.exit(1)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        if not cursor.fetchone():
            print("\n✗ Error: 'users' table not found in database!")
            print("Please run init_db.py first to create tables.")
            conn.close()
            sys.exit(1)
        
        # Check current columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"\nCurrent columns in users table: {columns}")
        
        migrations_needed = []
        
        # Check which columns need to be added
        if 'google_id' not in columns:
            migrations_needed.append('google_id')
        
        if 'auth_provider' not in columns:
            migrations_needed.append('auth_provider')
        
        if 'avatar_url' not in columns:
            migrations_needed.append('avatar_url')
        
        if not migrations_needed:
            print("\n✓ All Google OAuth columns already exist. No migration needed.")
            conn.close()
            return
        
        print(f"\nColumns to add: {migrations_needed}")
        
        # Count existing users
        cursor.execute("SELECT COUNT(*) FROM users")
        existing_user_count = cursor.fetchone()[0]
        print(f"Existing users in database: {existing_user_count}")
        
        # Ask for confirmation
        if existing_user_count > 0:
            print("\n" + "="*60)
            print("⚠️  WARNING: This will modify your database structure")
            print("="*60)
            response = input(f"\nProceed with migration? (yes/no): ")
            if response.lower() != 'yes':
                print("Migration cancelled.")
                conn.close()
                return
        
        # Backup existing data first
        print("\n1. Backing up users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_backup AS 
            SELECT * FROM users
        """)
        conn.commit()
        print("✓ Backup created: users_backup table")
        
        # Add new columns
        print("\n2. Adding new columns...")
        
        if 'google_id' in migrations_needed:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN google_id TEXT DEFAULT NULL
            """)
            print("✓ Added column: google_id")
            
            # Create unique index for google_id
            try:
                cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_id 
                    ON users(google_id) 
                    WHERE google_id IS NOT NULL
                """)
                print("✓ Created unique index on google_id")
            except sqlite3.Error as e:
                print(f"⚠️  Warning: Could not create index on google_id: {e}")
        
        if 'auth_provider' in migrations_needed:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN auth_provider TEXT DEFAULT 'local'
            """)
            print("✓ Added column: auth_provider")
            
            # Update existing users to have 'local' provider
            cursor.execute("""
                UPDATE users 
                SET auth_provider = 'local' 
                WHERE auth_provider IS NULL
            """)
            print(f"✓ Set auth_provider='local' for {existing_user_count} existing users")
        
        if 'avatar_url' in migrations_needed:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN avatar_url TEXT DEFAULT NULL
            """)
            print("✓ Added column: avatar_url")
        
        # Commit changes
        conn.commit()
        
        # Verify migration
        print("\n3. Verifying migration...")
        cursor.execute("PRAGMA table_info(users)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns: {new_columns}")
        
        # Check data integrity
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✓ Total users in database: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE auth_provider = 'local'")
        local_users = cursor.fetchone()[0]
        print(f"✓ Local auth users: {local_users}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE google_id IS NOT NULL")
        google_users = cursor.fetchone()[0]
        print(f"✓ Google auth users: {google_users}")
        
        print("\n" + "="*60)
        print("Migration completed successfully! ✓")
        print("="*60)
        print("\nWhat was done:")
        print("  • Added google_id column (unique, indexed)")
        print("  • Added auth_provider column (default: 'local')")
        print("  • Added avatar_url column")
        print(f"  • All {existing_user_count} existing users set to 'local' provider")
        print("  • Backup created: users_backup table")
        print("\nYour existing data is safe and unchanged.")
        print("You can now use Google OAuth authentication!")
        print("\nNext steps:")
        print("  1. Update your User model (add new fields)")
        print("  2. Update your schemas (add optional fields)")
        print("  3. Add Google OAuth routes to your API")
        print("  4. Test with a Google login!")
        
        # Close connection
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n✗ Migration failed: {e}")
        print("Rolling back changes...")
        conn.rollback()
        conn.close()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        conn.close()
        sys.exit(1)


def rollback_migration():
    """Rollback migration if needed"""
    db_path = "financial_analysis.db"
    
    print(f"Rolling back migration on {db_path}...")
    
    if not Path(db_path).exists():
        print(f"✗ Error: Database file '{db_path}' not found!")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if backup exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users_backup'
        """)
        
        if not cursor.fetchone():
            print("✗ No backup found. Cannot rollback.")
            conn.close()
            return
        
        print("\n⚠️  WARNING: This will restore users table from backup")
        response = input("Are you sure you want to rollback? (yes/no): ")
        if response.lower() != 'yes':
            print("Rollback cancelled.")
            conn.close()
            return
        
        print("Restoring from backup...")
        
        # Drop current users table
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Rename backup to users
        cursor.execute("ALTER TABLE users_backup RENAME TO users")
        
        conn.commit()
        print("✓ Rollback completed. Database restored from backup.")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"✗ Rollback failed: {e}")
        conn.rollback()
        conn.close()
        sys.exit(1)


def show_status():
    """Show current database status"""
    db_path = "financial_analysis.db"
    
    if not Path(db_path).exists():
        print(f"✗ Error: Database file '{db_path}' not found!")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        if not cursor.fetchone():
            print("✗ 'users' table not found in database!")
            conn.close()
            return
        
        # Get columns
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("\n" + "="*60)
        print("Database Status: financial_analysis.db")
        print("="*60)
        print("\nUsers table columns:")
        for col in columns:
            print(f"  • {col[1]} ({col[2]})")
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        print(f"\nTotal users: {total}")
        
        if 'auth_provider' in [col[1] for col in columns]:
            cursor.execute("SELECT COUNT(*) FROM users WHERE auth_provider = 'local'")
            local = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE auth_provider = 'google'")
            google = cursor.fetchone()[0]
            print(f"  • Local auth: {local}")
            print(f"  • Google auth: {google}")
        
        # Check for backup
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users_backup'
        """)
        if cursor.fetchone():
            print("\nBackup: users_backup table exists")
        else:
            print("\nBackup: No backup found")
        
        print("="*60)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate database for Google OAuth')
    parser.add_argument('--rollback', action='store_true', 
                       help='Rollback migration and restore from backup')
    parser.add_argument('--status', action='store_true',
                       help='Show current database status')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.rollback:
        rollback_migration()
    else:
        migrate_database()