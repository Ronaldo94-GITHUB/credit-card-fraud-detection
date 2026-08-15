from scripts import production_smoke_test


def test_production_endpoint_list_contains_health():
    assert "/health" in (
        production_smoke_test.PUBLIC_ENDPOINTS
    )


def test_production_endpoint_list_contains_readiness():
    assert "/readiness" in (
        production_smoke_test.PUBLIC_ENDPOINTS
    )


def test_production_base_url_is_https():
    assert (
        production_smoke_test.BASE_URL.startswith(
            "https://"
        )
    )
