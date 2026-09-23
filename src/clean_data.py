from src.db import run_query

SCHEMA = "workspace.credit_analysis"
SOURCE = f"{SCHEMA}.fact_credit"
TARGET = f"{SCHEMA}.fact_credit_clean"

# Seuil réaliste basé sur le 1er centile observé (~3M), on prend une marge de sécurité
SEUIL_REVENU_MIN = 500000

create_query = f"""
CREATE OR REPLACE TABLE {TARGET} AS
WITH derniere_decision AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY num_canevas
            ORDER BY id_decision DESC
        ) AS rn
    FROM {SOURCE}
)
SELECT
    num_canevas, code_agence, code_produit, date_key, id_decision, id_profil,
    montant_sollicite, revenu_annuel, retenue_mensuelle, taux_endettement,
    delai_mep_jours, est_accord, est_rejet
FROM derniere_decision
WHERE rn = 1
  AND revenu_annuel >= {SEUIL_REVENU_MIN}
"""

run_query(create_query)
print("✅ Table fact_credit_clean créée")

# Vérification rapide
count_source = run_query(f"SELECT COUNT(*) FROM {SOURCE}")[0][0]
count_clean = run_query(f"SELECT COUNT(*) FROM {TARGET}")[0][0]
print(f"Lignes source : {count_source}")
print(f"Lignes après nettoyage : {count_clean}")
print(f"Lignes supprimées : {count_source - count_clean}")
