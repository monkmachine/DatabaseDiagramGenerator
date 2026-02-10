
from typing import Dict, Any

def generate_mermaid(schema: Dict[str, Any]) -> str:
    """
    Generates Mermaid ER diagram syntax from the schema dictionary.
    """
    if not schema or "tables" not in schema:
        return "erDiagram\n    %% No tables found"

    lines = ["erDiagram"]
    
    tables = schema["tables"]
    
    # Generate tables
    for table_name, info in tables.items():
        lines.append(f"    {table_name} {{")
        for col in info["columns"]:
            # Mermaid needs type then name
            # If type is empty, default to string or similar
            col_type = col["type"] if col["type"] else "any"
            # Sanitize formatting if needed, but basic should work
            pk_str = " PK" if col["pk"] else ""
            lines.append(f"        {col_type} {col['name']}{pk_str}")
        lines.append("    }")

    # Generate relationships
    # Relation syntax: Table1 }|..|{ Table2 : label
    # We will look at FKs.
    # If TableA has FK to TableB, it means TableB (1) --- (Many) TableA
    # Usually visualized as TableB ||--o{ TableA : "FK_Col"
    
    for table_name, info in tables.items():
        for fk in info["foreign_keys"]:
            target_table = fk["target_table"]
            # To avoid potential duplicates or self-referencing issues, we check if target exists
            if target_table in tables:
                # Target ||--o{ Source
                lines.append(f'    {target_table} ||--o{{ {table_name} : "has"')
    
    return "\n".join(lines)
