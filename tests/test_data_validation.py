from unittest.mock import patch
from src.data_validation import check_completude, check_unicite, check_validite


@patch("src.data_validation.run_query")
def test_check_completude_sans_null(mock_run_query):
    """100 lignes, 0 NULL => taux_null_pct doit être 0.0"""
    mock_run_query.return_value = [(100, 0)]
    resultat = check_completude("montant_sollicite")
    assert resultat["total"] == 100
    assert resultat["nb_null"] == 0
    assert resultat["taux_null_pct"] == 0.0


@patch("src.data_validation.run_query")
def test_check_completude_avec_null(mock_run_query):
    """100 lignes, 25 NULL => taux_null_pct doit être 25.0"""
    mock_run_query.return_value = [(100, 25)]
    resultat = check_completude("revenu_annuel")
    assert resultat["nb_null"] == 25
    assert resultat["taux_null_pct"] == 25.0


@patch("src.data_validation.run_query")
def test_check_completude_table_vide(mock_run_query):
    """0 ligne au total => pas de division par zéro, taux = 0"""
    mock_run_query.return_value = [(0, 0)]
    resultat = check_completude("montant_sollicite")
    assert resultat["taux_null_pct"] == 0


@patch("src.data_validation.run_query")
def test_check_unicite_sans_doublons(mock_run_query):
    """0 doublon détecté"""
    mock_run_query.return_value = [(0,)]
    resultat = check_unicite("num_canevas")
    assert resultat["nb_doublons"] == 0
    assert resultat["cle"] == "num_canevas"


@patch("src.data_validation.run_query")
def test_check_unicite_avec_doublons(mock_run_query):
    """2 doublons détectés (comme observé sur num_canevas)"""
    mock_run_query.return_value = [(2,)]
    resultat = check_unicite("num_canevas")
    assert resultat["nb_doublons"] == 2


@patch("src.data_validation.run_query")
def test_check_validite_sans_anomalie(mock_run_query):
    """0 anomalie hors plage 0-100"""
    mock_run_query.return_value = [(0,)]
    resultat = check_validite("taux_endettement", minimum=0, maximum=100)
    assert resultat["nb_anomalies"] == 0
    assert resultat["min"] == 0
    assert resultat["max"] == 100


@patch("src.data_validation.run_query")
def test_check_validite_avec_anomalies(mock_run_query):
    """6 anomalies détectées (comme observé avant nettoyage)"""
    mock_run_query.return_value = [(6,)]
    resultat = check_validite("taux_endettement", minimum=0, maximum=100)
    assert resultat["nb_anomalies"] == 6
