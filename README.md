# Database Diagram Generator

A powerful, interactive tool to visualize database schemas. 
It generates both a **standalone interactive HTML diagram** (React Flow based) and a **Markdown file** (Mermaid.js syntax).

![Demo](media__1770715126820.png)

## Features

- **Interactive HTML Output**: Search tables, highlight connections, filter columns, and toggle Light/Dark mode.
- **Multi-Database Support**: Connect to **SQLite**, **PostgreSQL**, **MySQL**, **Oracle**, and **SQL Server**.
- **Privacy Focused**: Runs entirely locally. No data is sent to the cloud.
- **Zero Config**: Just point it at a database and go.

## Installation

1.  Clone the repository.
2.  Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1. SQLite (Simples)

For a local SQLite file, just provide the path:

```bash
python main.py my_database.db
```

### 2. Connection Strings (SQLAlchemy)

For other databases, provide a standard SQLAlchemy connection string.

**PostgreSQL:**
```bash
python main.py postgresql://user:password@localhost:5432/mydatabase
```

**MySQL:**
```bash
python main.py mysql+pymysql://user:password@localhost/mydatabase
```

**SQL Server:**
```bash
python main.py "mssql+pymssql://user:password@host/dbname"
```

### 3. Output

The tool will generate two files in the current directory:
-   `[db_name].html`: The interactive visualizer.
-   `[db_name].md`: A markdown file with Mermaid syntax.

## Oracle Database & SSL

To connect to Oracle (especially cloud databases like ATP/ADW which require SSL/Wallets), use the `oracle+oracledb` driver.

### Basic One-Way SSL
If your database uses standard SSL (TCPS) without client certificates:

```bash
python main.py "oracle+oracledb://user:password@host:port/?service_name=myservice&protocol=tcps"
```

### Mutual TLS (mTLS) with a Wallet
If you have an **Oracle Wallet** (e.g., `cwallet.sso`), you need to tell the driver where it is.

The easiest way with `python-oracledb` (Thin mode) is to set the `TNS_ADMIN` environment variable to the directory containing your wallet files, then use the TNS alias from `tnsnames.ora`.

**Steps:**
1.  Unzip your wallet to a folder (e.g., `C:\oracle\wallet`).
2.  Set environment variable:
    -   **Windows**: `set TNS_ADMIN=C:\oracle\wallet`
    -   **Linux/Mac**: `export TNS_ADMIN=/path/to/wallet`
3.  Run the tool using the alias defined in `tnsnames.ora`:

```bash
python main.py oracle+oracledb://user:password@MyAlias
```

## Troubleshooting

-   **Drivers**: Ensure you have installed the drivers from `requirements.txt`.
-   **Connection Issues**: Wrap connection strings in quotes if they contain special characters like `^`, `&` or `;`.
