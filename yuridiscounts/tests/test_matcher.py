from yuridiscounts.services.matcher import score_similaridade


def test_titulos_similares_score_alto():
    score = score_similaridade("dipirona 500mg", "Dipirona 500mg Generico")
    assert score > 70


def test_titulos_diferentes_score_baixo():
    score = score_similaridade("dipirona 500mg", "shampoo anticaspa")
    assert score < 50
