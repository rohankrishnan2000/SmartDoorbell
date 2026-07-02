from backend.app.ml.risk import RobberyRiskModel


def test_package_theft_risk_scores_warning():
    result = RobberyRiskModel().score(
        [{"label": "person", "confidence": 0.9}, {"label": "package", "confidence": 0.8}],
        hour=23,
        package_waiting=True,
    )
    assert result.risk_score >= 0.7
    assert result.severity in {"warning", "critical"}

