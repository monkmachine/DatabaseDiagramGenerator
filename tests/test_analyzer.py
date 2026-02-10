import unittest
import sqlite3
from sqlalchemy import create_engine, text
from src.analyzer import get_db_schema

import os
import tempfile

class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create a temp file
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.db_fd) # Close immediately, let SQLAlchemy handle access
        self.connection_string = f"sqlite:///{self.db_path}"
        
        # Populate DB
        self.engine = create_engine(self.connection_string)
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT
                )
            """))
            conn.execute(text("""
                CREATE TABLE posts (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    title TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """))
            conn.commit()

    def tearDown(self):
        self.engine.dispose()
        if os.path.exists(self.db_path):
             try:
                 os.unlink(self.db_path)
             except PermissionError:
                 pass # Best effort cleanup

    def test_get_db_schema_tables(self):
        schema = get_db_schema(self.connection_string)
        self.assertIsNotNone(schema)
        self.assertIn("users", schema["tables"])
        self.assertIn("posts", schema["tables"])

    def test_get_db_schema_columns(self):
        schema = get_db_schema(self.connection_string)
        users_columns = schema["tables"]["users"]["columns"]
        
        # Verify columns exist
        col_names = [c["name"] for c in users_columns]
        self.assertIn("id", col_names)
        self.assertIn("username", col_names)
        self.assertIn("email", col_names)
        
        # Verify PK
        id_col = next(c for c in users_columns if c["name"] == "id")
        self.assertTrue(id_col["pk"])

    def test_get_db_schema_relationships(self):
        schema = get_db_schema(self.connection_string)
        posts_fks = schema["tables"]["posts"]["foreign_keys"]
        
        self.assertEqual(len(posts_fks), 1)
        fk = posts_fks[0]
        self.assertEqual(fk["target_table"], "users")
        self.assertEqual(fk["from_column"], "user_id")
        self.assertEqual(fk["to_column"], "id")

if __name__ == '__main__':
    unittest.main()
