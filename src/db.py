import os
from dotenv import load_dotenv
from databricks import sql

load_dotenv()

CATALOG = "workspace"
SCHEMA = "credit_analysis"


def get_connection():
    """Retourne une connexion Databricks SQL prête à l'emploi."""
    return sql.connect(
        server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_TOKEN")
    )


def run_query(query: str):
    """Exécute une requête SQL et retourne les résultats sous forme de liste de tuples."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
