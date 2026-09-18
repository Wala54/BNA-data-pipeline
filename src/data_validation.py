from src.db import run_query

TABLE = "workspace.credit_analysis.fact_credit_clean"


def check_completude(colonne: str):
    """Retourne le nombre et le % de valeurs NULL sur une colonne."""
    query = f"""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN {colonne} IS NULL THEN 1 ELSE 0 END) AS nb_null
        FROM {TABLE}
    """
    total, nb_null = run_query(query)[0]
    taux_null = round((nb_null / total) * 100, 2) if total else 0
    return {"colonne": colonne, "total": total, "nb_null": nb_null, "taux_null_pct": taux_null}


def check_unicite(cle: str):
    """Vérifie l'unicité d'une clé (doublons)."""
    query = f"""
        SELECT COUNT(*) AS nb_doublons FROM (
            SELECT {cle}, COUNT(*) AS cnt
            FROM {TABLE}
            GROUP BY {cle}
            HAVING COUNT(*) > 1
        )
    """
    nb_doublons = run_query(query)[0][0]
    return {"cle": cle, "nb_doublons": nb_doublons}


def check_validite(colonne: str, minimum=None, maximum=None):
    """Vérifie que les valeurs respectent une plage acceptable."""
    conditions = []
    if minimum is not None:
        conditions.append(f"{colonne} < {minimum}")
    if maximum is not None:
        conditions.append(f"{colonne} > {maximum}")
    where_clause = " OR ".join(conditions) if conditions else "1=0"

    query = f"""
        SELECT COUNT(*) FROM {TABLE}
        WHERE {where_clause}
    """
    nb_anomalies = run_query(query)[0][0]
    return {"colonne": colonne, "min": minimum, "max": maximum, "nb_anomalies": nb_anomalies}


if __name__ == "__main__":
    print("=== Complétude ===")
    for col in ["montant_sollicite", "revenu_annuel", "code_agence", "date_key"]:
        print(check_completude(col))

    print("\n=== Unicité ===")
    print(check_unicite("num_canevas"))

    print("\n=== Validité ===")
    print(check_validite("montant_sollicite", minimum=0))
    print(check_validite("taux_endettement", minimum=0, maximum=100))
