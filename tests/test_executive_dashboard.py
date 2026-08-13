from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_executive_dashboard_is_available():
    response = client.get(
        "/executive"
    )

    assert response.status_code == 200

    assert (
        "Dashboard Executivo MLOps"
        in response.text
    )

    assert (
        "Gerar Relat?rio PDF"
        in response.text
    )


def test_executive_report_is_available():
    response = client.get(
        "/executive/report"
    )

    assert response.status_code == 200

    assert (
        "Relat?rio Executivo MLOps"
        in response.text
    )

    assert (
        "window.print()"
        in response.text
    )


def test_executive_dashboard_does_not_embed_admin_secret():
    response = client.get(
        "/executive"
    )

    text = response.text.lower()

    assert "admin_api_key" not in text

    assert "x-admin-api-key" not in text


def test_phase29_routes_are_in_openapi():
    schema = app.openapi()

    paths = schema.get(
        "paths",
        {}
    )

    assert "/executive" in paths

    assert (
        "/executive/report"
        in paths
    )
