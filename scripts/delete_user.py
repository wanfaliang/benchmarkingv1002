"""
Delete User Script
File: scripts/delete_user.py

Usage: python scripts/delete_user.py simoncaseload@gmail.com
"""

import sqlite3
import sys
from pathlib import Path

def delete_user(email: str):
    """Delete a user by email address"""
    
    db_path = "financial_analysis.db"
    
    if not Path(db_path).exists():
        print(f"✗ Error: Database file '{db_path}' not found!")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id, email, full_name FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"✗ User with email '{email}' not found.")
            conn.close()
            return
        
        user_id, user_email, full_name = user
        
        print(f"\n{'='*60}")
        print(f"Found user:")
        print(f"  User ID: {user_id}")
        print(f"  Email: {user_email}")
        print(f"  Name: {full_name}")
        print(f"{'='*60}\n")
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to DELETE this user? (type 'yes' to confirm): ")
        
        if confirm.lower() != 'yes':
            print("Deletion cancelled.")
            conn.close()
            return
        
        # Check for related data (analyses)
        cursor.execute("SELECT COUNT(*) FROM analyses WHERE user_id = ?", (user_id,))
        analysis_count = cursor.fetchone()[0]
        
        if analysis_count > 0:
            print(f"\n⚠️  Warning: This user has {analysis_count} analysis/analyses.")
            confirm2 = input(f"Delete user AND all their analyses? (type 'yes' to confirm): ")
            if confirm2.lower() != 'yes':
                print("Deletion cancelled.")
                conn.close()
                return
        
        # Delete user (cascade will delete related analyses and sections)
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        conn.commit()
        
        print(f"\n✓ User '{email}' successfully deleted!")
        if analysis_count > 0:
            print(f"✓ {analysis_count} analysis/analyses also deleted.")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        conn.rollback()
        conn.close()
        sys.exit(1)


def list_all_users():
    """List all users in the database"""
    
    db_path = "financial_analysis.db"
    
    if not Path(db_path).exists():
        print(f"✗ Error: Database file '{db_path}' not found!")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, email, full_name, auth_provider, email_verified, created_at 
            FROM users 
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        
        if not users:
            print("No users found in database.")
            conn.close()
            return
        
        print(f"\n{'='*80}")
        print(f"All Users ({len(users)} total):")
        print(f"{'='*80}")
        
        for user in users:
            user_id, email, full_name, auth_provider, email_verified, created_at = user
            verified_status = "✓ Verified" if email_verified else "✗ Not Verified"
            print(f"\n  Email: {email}")
            print(f"  Name: {full_name or 'N/A'}")
            print(f"  Auth: {auth_provider}")
            print(f"  Status: {verified_status}")
            print(f"  Created: {created_at}")
            print(f"  ID: {user_id}")
        
        print(f"\n{'='*80}\n")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        conn.close()
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Delete a user from the database')
    parser.add_argument('email', nargs='?', help='Email address of user to delete')
    parser.add_argument('--list', action='store_true', help='List all users')
    
    args = parser.parse_args()
    
    if args.list:
        list_all_users()
    elif args.email:
        delete_user(args.email)
    else:
        print("Usage:")
        print("  python scripts/delete_user.py simoncaseload@gmail.com")
        print("  python scripts/delete_user.py --list")
        sys.exit(1)