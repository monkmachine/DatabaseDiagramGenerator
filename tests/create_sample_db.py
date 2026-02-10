
import sqlite3
import os

def create_sample_db(db_name="sample.db"):
    if os.path.exists(db_name):
        os.remove(db_name)
        
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Table: Users
    cursor.execute("""
    CREATE TABLE Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Table: Posts
    cursor.execute("""
    CREATE TABLE Posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,
        content TEXT,
        published BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES Users(id)
    );
    """)
    
    # Table: Comments
    cursor.execute("""
    CREATE TABLE Comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        user_id INTEGER,
        body TEXT NOT NULL,
        FOREIGN KEY (post_id) REFERENCES Posts(id),
        FOREIGN KEY (user_id) REFERENCES Users(id)
    );
    """)
    
    conn.commit()
    conn.close()
    print(f"Created {db_name} with Users, Posts, and Comments tables.")

if __name__ == "__main__":
    create_sample_db()
