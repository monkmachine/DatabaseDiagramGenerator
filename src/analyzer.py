from typing import Dict, Any, List
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

def get_db_schema(connection_string: str) -> Dict[str, Any]:
    """
    Analyzes a database using SQLAlchemy and returns its schema structure.
    
    Args:
        connection_string: A valid SQLAlchemy connection string 
                          (e.g., 'sqlite:///path/to.db', 'postgresql://user:pass@host/db')
    
    Returns:
        A dictionary with:
        - 'tables': Dict mapping table names to their info (columns, fks)
    """
    try:
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        
        schema = {"tables": {}}
        
        # Get all table names
        table_names = inspector.get_table_names()
        
        for table_name in table_names:
            table_info = {
                "columns": [],
                "foreign_keys": []
            }
            
            # Get columns
            # inspector.get_columns returns: [{'name': 'id', 'type': INTEGER(), 'nullable': False, 'default': None, 'primary_key': 1}, ...]
            columns = inspector.get_columns(table_name)
            for col in columns:
                # Stringify the type to make it JSON serializable
                col_type = str(col['type'])
                
                table_info["columns"].append({
                    "name": col['name'],
                    "type": col_type,
                    "pk": bool(col.get('primary_key', False)),
                    "nullable": col.get('nullable', True),
                    "default": str(col.get('default')) if col.get('default') is not None else None
                })
                
            # Get foreign keys
            # inspector.get_foreign_keys returns: [{'name': '...', 'constrained_columns': ['user_id'], 'referred_schema': None, 'referred_table': 'users', 'referred_columns': ['id']}, ...]
            fks = inspector.get_foreign_keys(table_name)
            for fk in fks:
                # SQLAlchemy returns lists for columns (composite keys), we'll flatten for simple edges logic
                # Complex composite keys might create multiple edges or need better handling, but this suffices for the visualizer
                constrained_cols = fk.get('constrained_columns', [])
                referred_cols = fk.get('referred_columns', [])
                target_table = fk.get('referred_table')
                
                for i in range(len(constrained_cols)):
                    table_info["foreign_keys"].append({
                        "target_table": target_table,
                        "from_column": constrained_cols[i],
                        "to_column": referred_cols[i] if i < len(referred_cols) else None
                    })
            
            schema["tables"][table_name] = table_info
            
        return schema

    except Exception as e:
        print(f"An error occurred analyzing the database: {e}")
        return None
    finally:
        if 'engine' in locals():
            engine.dispose()
