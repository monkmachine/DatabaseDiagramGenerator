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
            
            # Explicitly fetch PKs (more robust for some dialects)
            pk_constraint = inspector.get_pk_constraint(table_name)
            pk_cols = set(pk_constraint.get('constrained_columns', []))
            
            for col in columns:
                # Stringify the type to make it JSON serializable
                col_type = str(col['type'])
                is_pk = col['name'] in pk_cols or bool(col.get('primary_key', False))
                
                table_info["columns"].append({
                    "name": col['name'],
                    "type": col_type,
                    "pk": is_pk,
                    "nullable": col.get('nullable', True),
                    "default": str(col.get('default')) if col.get('default') is not None else None
                })
                
            # Get foreign keys
            # inspector.get_foreign_keys returns: [{'name': '...', 'constrained_columns': ['user_id'], 'referred_schema': None, 'referred_table': 'users', 'referred_columns': ['id']}, ...]
            fks = inspector.get_foreign_keys(table_name)
            
            # Fallback checks (e.g. for SQL Server)
            if not fks and '.' not in table_name:
                try:
                    # Try explicit 'dbo' schema
                    fks_dbo = inspector.get_foreign_keys(table_name, schema='dbo')
                    if fks_dbo:
                        print(f"DEBUG: Found FKs for {table_name} by explicitly checking schema 'dbo'")
                        fks = fks_dbo
                except Exception:
                    pass

            if not fks:
                # Debug print for empty FKs (might be normal, but useful if user expects them)
                # print(f"DEBUG: No FKs found for table {table_name}")
                pass
                
            for fk in fks:
                print(f"DEBUG: Found FK in {table_name}: {fk}")
                # SQLAlchemy returns lists for columns (composite keys), we'll flatten for simple edges logic
                # Complex composite keys might create multiple edges or need better handling, but this suffices for the visualizer
                constrained_cols = fk.get('constrained_columns', [])
                referred_cols = fk.get('referred_columns', [])
                target_table = fk.get('referred_table')
                
                # Logic to resolve target table
                if target_table not in table_names:
                    # 1. Try stripping schema
                    if target_table and '.' in target_table:
                        possible_name = target_table.split('.')[-1]
                        if possible_name in table_names:
                            target_table = possible_name
                    
                    # 2. Try Case-Insensitive (both full and stripped)
                    if target_table not in table_names:
                        # Build lower-case map
                        table_map_lower = {t.lower(): t for t in table_names}
                        
                        target_lower = target_table.lower() if target_table else ""
                        
                        if target_lower in table_map_lower:
                            target_table = table_map_lower[target_lower]
                        elif '.' in target_table:
                             # Try stripping schema + case-insensitive
                             stripped_lower = target_table.split('.')[-1].lower()
                             if stripped_lower in table_map_lower:
                                 target_table = table_map_lower[stripped_lower]
                
                # Debug if still missing
                if target_table not in table_names:
                    print(f"DEBUG: Could not resolve FK target '{fk.get('referred_table')}' (normalized: '{target_table}') in known tables: {list(table_names)[:5]}...")

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
