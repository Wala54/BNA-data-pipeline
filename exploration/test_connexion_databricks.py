import os
from dotenv import load_dotenv
from databricks import sql

load_dotenv()

server_hostname = os.getenv("DATABRICKS_SERVER_HOSTNAME")
http_path = os.getenv("DATABRICKS_HTTP_PATH")
access_token = os.getenv("DATABRICKS_TOKEN")

try:
    connection = sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=access_token
    )
    cursor = connection.cursor()

    cursor.execute("SELECT current_version()")
    result = cursor.fetchone()
    print("✅ Connexion réussie")
    print("Version Databricks :", result)

    print("\n📂 Catalogues disponibles :")
    cursor.execute("SHOW CATALOGS")
    for c in cursor.fetchall():
        print(" -", c)

    print("\n📂 Schémas dans le catalogue courant :")
    cursor.execute("SHOW SCHEMAS")
    for s in cursor.fetchall():
        print(" -", s)
    print("\n📋 Tables dans credit_analysis :")
    cursor.execute("SHOW TABLES IN workspace.credit_analysis")
    for t in cursor.fetchall():
        print(" -", t)
    cursor.close()
    connection.close()

except Exception as e:
    print("❌ Échec de connexion")
    print(type(e).__name__, ":", e)
