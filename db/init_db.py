import sqlite3
import pandas as pd
from sqlite3 import Connection

# Ruta de la base de datos (en la raíz del proyecto)
DB_PATH = "trades.db"

def get_connection() -> Connection:
    """
    Abre conexión a la base de datos SQLite.
    Si no existe, la crea en DB_PATH.
    """
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    return conn

def init_db() -> None:
    """
    Crea la tabla 'trades' si no existe.
    Debe ejecutarse al arrancar la app.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            pair TEXT NOT NULL,
            leverage INTEGER,
            qty REAL,
            entry_price REAL,
            entry_value REAL,
            exit_price REAL,
            exit_value REAL,
            commission_pct REAL,
            commission REAL,
            pnl REAL,
            roi REAL
        )
    """)
    conn.commit()
    conn.close()

def load_all_trades() -> pd.DataFrame:
    """
    Recupera todas las operaciones de la tabla 'trades',
    ordenadas por id, y las devuelve como DataFrame.
    """
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM trades ORDER BY id", conn)
    conn.close()
    return df
