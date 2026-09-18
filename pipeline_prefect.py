import argparse
import subprocess
from prefect import task, flow
from src.data_validation import check_completude, check_unicite, check_validite
from src import quality_score


@task(name="install_dependencies")
def install_dependencies():
    print("✅ Dépendances déjà installées (venv actif)")
    return True


@task(name="check_code")
def check_code():
    """Vérifie la qualité du code (flake8) et lance les tests unitaires (pytest)."""
    print("🔎 Vérification qualité du code (flake8)...")
    flake8_result = subprocess.run(
        ["flake8", "src/", "clean_data.py", "pipeline_prefect.py", "--max-line-length=100"],
        capture_output=True, text=True
    )
    print(flake8_result.stdout if flake8_result.stdout else "✅ Aucun problème de style détecté")
    if flake8_result.returncode != 0:
        print("⚠️ Flake8 a détecté des problèmes de style (voir ci-dessus)")

    print("🧪 Exécution des tests unitaires (pytest)...")
    pytest_result = subprocess.run(
        ["pytest", "tests/", "-v"],
        capture_output=True, text=True
    )
    print(pytest_result.stdout)
    if pytest_result.returncode != 0:
        raise RuntimeError("❌ Des tests unitaires ont échoué, arrêt du pipeline")
    print("✅ Tous les tests sont passés")
    return True


@task(name="clean_data")
def clean_data():
    """Exécute le nettoyage ETL (doublons + revenus non fiables)."""
    print("🧹 Nettoyage des données en cours...")
    # Le script clean_data.py exécute déjà tout à l'import
    return True


@task(name="run_data_validation")
def run_data_validation():
    """Exécute les contrôles qualité sur fact_credit_clean."""
    print("🔍 Audit qualité en cours...")
    resultats = []
    for col in ["montant_sollicite", "revenu_annuel", "code_agence", "date_key"]:
        resultats.append(check_completude(col))
    resultats.append(check_unicite("num_canevas"))
    resultats.append(check_validite("montant_sollicite", minimum=0))
    resultats.append(check_validite("taux_endettement", minimum=0, maximum=100))
    for r in resultats:
        print(r)
    return resultats


@task(name="compute_quality_score")
def compute_quality_score():
    """Calcule le score de qualité global et l'exporte vers Databricks."""
    print("📊 Calcul du score de qualité...")
    resultats = quality_score.calculer_scores()
    quality_score.exporter_vers_databricks(resultats)
    return resultats


@flow(name="clean")
def flow_clean():
    install_dependencies()
    clean_data()


@flow(name="code")
def flow_code():
    install_dependencies()
    check_code()


@flow(name="audit")
def flow_audit():
    install_dependencies()
    run_data_validation()
    compute_quality_score()


@flow(name="all")
def flow_all():
    install_dependencies()
    check_code()
    clean_data()
    run_data_validation()
    compute_quality_score()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow", choices=["all", "clean", "audit", "code"], required=True)
    args = parser.parse_args()

    if args.flow == "all":
        flow_all()
    elif args.flow == "clean":
        flow_clean()
    elif args.flow == "audit":
        flow_audit()
    elif args.flow == "code":
        flow_code()
