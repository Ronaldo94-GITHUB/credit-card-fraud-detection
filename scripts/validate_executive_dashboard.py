from fastapi.testclient import TestClient

from src.api import app


def main() -> int:
    client = TestClient(app)

    dashboard = client.get(
        "/executive"
    )

    report = client.get(
        "/executive/report?period=7d"
    )

    schema = app.openapi()

    paths = schema.get(
        "paths",
        {}
    )

    dashboard_ok = (
        dashboard.status_code == 200
        and "Dashboard Executivo MLOps"
        in dashboard.text
    )

    report_ok = (
        report.status_code == 200
        and "Relatório Executivo MLOps"
        in report.text
        and "window.print()"
        in report.text
    )

    routes_ok = (
        "/executive" in paths
        and "/executive/report"
        in paths
    )

    periods_ok = all(
        period in dashboard.text
        for period in [
            "24h",
            "7d",
            "30d",
        ]
    )

    metrics_ok = all(
        endpoint in dashboard.text
        for endpoint in [
            "/metrics/persistent",
            "/metrics/timeseries",
            "/drift/statistical",
            "/alerts/mlops",
            "/metrics/ground-truth",
            "/model-info",
        ]
    )

    no_secret = (
        "X-Admin-API-Key"
        not in dashboard.text
        and "ADMIN_API_KEY"
        not in dashboard.text
    )

    print(
        "EXECUTIVE_DASHBOARD_ROUTE_OK="
        + str(dashboard_ok)
    )

    print(
        "EXECUTIVE_REPORT_ROUTE_OK="
        + str(report_ok)
    )

    print(
        "EXECUTIVE_OPENAPI_ROUTES_OK="
        + str(routes_ok)
    )

    print(
        "EXECUTIVE_PERIOD_FILTERS_OK="
        + str(periods_ok)
    )

    print(
        "EXECUTIVE_MLOPS_DATA_SOURCES_OK="
        + str(metrics_ok)
    )

    print(
        "EXECUTIVE_ADMIN_SECRET_EXPOSED="
        + str(
            not no_secret
        )
    )

    print(
        "EXECUTIVE_PDF_PRINT_READY="
        + str(report_ok)
    )

    passed = all(
        [
            dashboard_ok,
            report_ok,
            routes_ok,
            periods_ok,
            metrics_ok,
            no_secret,
        ]
    )

    print(
        "PHASE29_EXECUTIVE_VALIDATION_OK="
        + str(passed)
    )

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
