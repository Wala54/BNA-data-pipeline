from src.db import run_query

TABLE = "workspace.credit_analysis.fact_credit"

print("=== Détail des doublons sur num_canevas ===")
query_doublons = f"""
    SELECT num_canevas, COUNT(*) AS nb_occurrences
    FROM {TABLE}
    GROUP BY num_canevas
    HAVING COUNT(*) > 1
"""
doublons = run_query(query_doublons)
for d in doublons:
    print(d)

print("\n=== Lignes complètes des doublons ===")
for d in doublons:
    num_canevas = d[0]
    query_detail = f"""
        SELECT * FROM {TABLE}
        WHERE num_canevas = '{num_canevas}'
    """
    for row in run_query(query_detail):
        print(row)

print("\n=== Détail des anomalies taux_endettement (hors 0-100) ===")
query_anomalies = f"""
    SELECT num_canevas, code_agence, montant_sollicite, revenu_annuel,
           retenue_mensuelle, taux_endettement
    FROM {TABLE}
    WHERE taux_endettement < 0 OR taux_endettement > 100
"""
for row in run_query(query_anomalies):
    print(row)
