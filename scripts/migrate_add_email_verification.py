import sqlite3
import sys
from pathlib import Path

def migrate_database():
    """Add email verification fields to users table"""
    
    db_path = "financial_analysis.db"
    
    print(f"Starting email verification migration on {db_path}...")
    
    if not Path(db_path).exists():
        print(f"✗ Error: Database file '{db_path}' not found!")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns: {columns}")
        
        migrations_needed = []
        
        if 'email_verified' not in columns:
            migrations_needed.append('email_verified')
        
        if 'verification_token' not in columns:
            migrations_needed.append('verification_token')
        
        if 'verification_token_expires' not in columns:
            migrations_needed.append('verification_token_expires')
        
        if not migrations_needed:
            print("✓ All email verification columns already exist.")
            conn.close()
            return
        
        print(f"\nAdding columns: {migrations_needed}")
        
        # Add new columns
        if 'email_verified' in migrations_needed:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN email_verified BOOLEAN DEFAULT 0
            """)
            print("✓ Added column: email_verified")
            
            # Set existing users and Google OAuth users as verified
            cursor.execute("""
                UPDATE users 
                SET email_verified = 1 
                WHERE google_id IS NOT NULL OR created_at < datetime('now')
            """)
            print("✓ Set existing users as verified")
        
        if 'verification_token' in migrations_needed:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN verification_token TEXT DEFAULT NULL
            """)
            print("✓ Added column: verification_token")
        
        if 'verification_token_expires' in migrations_needed:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN verification_token_expires DATETIME DEFAULT NULL
            """)
            print("✓ Added column: verification_token_expires")
        
        conn.commit()
        print("\n✓ Email verification migration completed!")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        conn.close()
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()