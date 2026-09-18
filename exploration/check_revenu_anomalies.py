from src.db import run_query

TABLE = "workspace.credit_analysis.fact_credit"

query = f"""
    SELECT
        MIN(revenu_annuel) AS min_revenu,
        AVG(revenu_annuel) AS avg_revenu,
        MAX(revenu_annuel) AS max_revenu,
        PERCENTILE(revenu_annuel, 0.01) AS p1_revenu
    FROM {TABLE}
"""
print(run_query(query)[0])

