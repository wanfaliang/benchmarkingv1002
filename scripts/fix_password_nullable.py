# scripts/fix_password_nullable.py
import sqlite3

conn = sqlite3.connect('financial_analysis.db')
cursor = conn.cursor()

cursor.executescript('''
    PRAGMA foreign_keys=off;
    
    BEGIN TRANSACTION;
    
    CREATE TABLE users_new (
        user_id VARCHAR PRIMARY KEY,
        email VARCHAR UNIQUE NOT NULL,
        password_hash VARCHAR,
        full_name VARCHAR,
        is_active BOOLEAN DEFAULT 1,
        created_at DATETIME,
        google_id VARCHAR UNIQUE,
        auth_provider VARCHAR DEFAULT 'local',
        avatar_url VARCHAR
    );
    
    INSERT INTO users_new SELECT * FROM users;
    DROP TABLE users;
    ALTER TABLE users_new RENAME TO users;
    
    COMMIT;
    PRAGMA foreign_keys=on;
''')

conn.close()
print("✓ Fixed password_hash nullable constraint!")