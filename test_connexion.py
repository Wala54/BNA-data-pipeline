import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

url = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

try:
    engine = create_engine(url)
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version();")).scalar()
        nb_tables = conn.execute(text("""
            SELECT count(*) FROM information_schema.tables
            WHERE table_schema = 'public';
        """)).scalar()
    print("✅ Connexion réussie")
    print(f"Version  : {version.split(',')[0]}")
    print(f"Tables   : {nb_tables} dans le schéma public")
except Exception as e:
    print("❌ Échec de connexion")
    print(type(e).__name__, ":", e)
