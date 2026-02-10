
import sys
import os
import argparse
from src.analyzer import get_db_schema
from src.generator import generate_mermaid
from src.html_generator import generate_html


def main():
    parser = argparse.ArgumentParser(description="Generate Mermaid ER diagram and Interactive HTML from a database.")
    parser.add_argument("connection_string", help="Database connection string (e.g. 'sqlite:///mydb.db' or path to sqlite file)")
    parser.add_argument("--output", "-o", default=None, help="Output file path (default: [db_name].md)")
    
    args = parser.parse_args()
    
    conn_str = args.connection_string
    
    # Heuristic for convenience: if it looks like a file path and not a URI, assume SQLite
    if "://" not in conn_str:
        if os.path.exists(conn_str):
            # Convert to absolute path for safety with sqlite:///
            abs_path = os.path.abspath(conn_str)
            conn_str = f"sqlite:///{abs_path}"
        else:
            # If it's not a file that exists, and doesn't look like a URI, warn but try anyway (maybe creating new?)
            # But we are analyzing, so it must exist.
             print(f"Error: File '{conn_str}' not found and does not look like a connection string.")
             sys.exit(1)
        
    print(f"Analyzing database: {conn_str}")
    schema = get_db_schema(conn_str)
    
    if not schema:
        print("Failed to extract schema. Please check your connection string and drivers.")
        sys.exit(1)
        
    print("Generating diagram...")
    mermaid_code = generate_mermaid(schema)
    
    # WRAPPING IN MARKDOWN
    markdown_content = f"```mermaid\n{mermaid_code}\n```\n"
    
    # Determine base output name
    if args.output:
        base_output_path = os.path.splitext(args.output)[0]
    else:
        # Try to derive a name from the connection string
        if "sqlite" in conn_str:
             # simple approach for sqlite files
             base_name = os.path.basename(conn_str.replace("sqlite:///", ""))
             base_output_path = os.path.splitext(base_name)[0]
        else:
             # for other dbs (e.g. postgresql://user@localhost/mydb), take the last part
             from urllib.parse import urlparse
             try:
                 url = urlparse(conn_str)
                 # url.path might be '/mydb'
                 path_part = url.path.strip('/')
                 base_output_path = path_part if path_part else "database_diagram"
             except:
                 base_output_path = "database_diagram"

    # Write Markdown
    md_path = f"{base_output_path}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Mermaid diagram extracted to: {md_path}")

    # Write HTML
    html_content = generate_html(schema)
    html_path = f"{base_output_path}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Interactive diagram extracted to: {html_path}")

    print("Success! Open the HTML file in your browser or the MD file in VS Code.")

if __name__ == "__main__":
    main()
