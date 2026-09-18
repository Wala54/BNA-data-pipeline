from datetime import datetime
from src.db import run_query
from src.data_validation import check_completude, check_unicite, check_validite

SCHEMA = "workspace.credit_analysis"
TABLE = f"{SCHEMA}.fact_credit_clean"
REPORT_TABLE = f"{SCHEMA}.data_quality_report"

# Pondération des trois dimensions de qualité
POIDS = {"completude": 0.4, "unicite": 0.3, "validite": 0.3}


def calculer_scores():
    # --- Complétude ---
    resultats = []
    colonnes_completude = [
        "montant_sollicite",
        "revenu_annuel",
        "code_agence",
        "date_key",
    ]
    scores_completude = []
    for col in colonnes_completude:
        r = check_completude(col)
        score = 100 - r["taux_null_pct"]
        scores_completude.append(score)
        resultats.append(
            {
                "table_name": "fact_credit_clean",
                "colonne": col,
                "type_controle": "completude",
                "score": round(score, 2),
                "detail": f"{r['nb_null']} valeurs NULL sur {r['total']}",
            }
        )
    score_completude_global = sum(scores_completude) / len(scores_completude)

    # --- Unicité ---
    r = check_unicite("num_canevas")
    total = run_query(f"SELECT COUNT(*) FROM {TABLE}")[0][0]
    score_unicite = 100 - round((r["nb_doublons"] / total) * 100, 2) if total else 0
    resultats.append(
        {
            "table_name": "fact_credit_clean",
            "colonne": "num_canevas",
            "type_controle": "unicite",
            "score": round(score_unicite, 2),
            "detail": f"{r['nb_doublons']} doublons sur {total}",
        }
     )
    # --- Validité ---
    validites = [
        check_validite("montant_sollicite", minimum=0),
        check_validite("taux_endettement", minimum=0, maximum=100),
    ]
    scores_validite = []
    for r in validites:
        score = 100 - round((r["nb_anomalies"] / total) * 100, 2) if total else 0
        scores_validite.append(score)
        resultats.append(
            {
                "table_name": "fact_credit_clean",
                "colonne": r["colonne"],
                "type_controle": "validite",
                "score": round(score, 2),
                "detail": f"{r['nb_anomalies']} anomalies détectées",
            }
        )
    score_validite_global = sum(scores_validite) / len(scores_validite)

    # --- Score global pondéré ---
    score_global = (
        score_completude_global * POIDS["completude"]
        + score_unicite * POIDS["unicite"]
        + score_validite_global * POIDS["validite"]
    )

    resultats.append(
        {
            "table_name": "fact_credit_clean",
            "colonne": "GLOBAL",
            "type_controle": "score_global",
            "score": round(score_global, 2),
            "detail": (
                f"Complétude={round(score_completude_global, 2)} | "
                f"Unicité={round(score_unicite, 2)} | "
                f"Validité={round(score_validite_global, 2)}"
            ),
        }
    )

    return resultats


def exporter_vers_databricks(resultats):
    run_query(f"""
        CREATE TABLE IF NOT EXISTS {REPORT_TABLE} (
            table_name STRING,
            colonne STRING,
            type_controle STRING,
            score DOUBLE,
            detail STRING,
            date_audit TIMESTAMP
        )
    """)

    date_audit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values = ", ".join(
        f"('{r['table_name']}', '{r['colonne']}', '{r['type_controle']}', "
        f"{r['score']}, '{r['detail']}', TIMESTAMP('{date_audit}'))"
        for r in resultats
    )
    run_query(f"INSERT INTO {REPORT_TABLE} VALUES {values}")
    print(f"✅ {len(resultats)} lignes insérées dans {REPORT_TABLE}")


if __name__ == "__main__":
    resultats = calculer_scores()
    print("\n=== Scores de qualité ===")
    for r in resultats:
        print(r)

    exporter_vers_databricks(resultats)
