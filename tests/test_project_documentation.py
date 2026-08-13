from pathlib import Path

ROOT = Path(
    __file__
).resolve().parents[1]


def test_phase28_documents_exist():
    files = [
        "docs/architecture.md",
        "docs/mlops-lifecycle.md",
        "docs/portfolio-case-study.md",
    ]

    for item in files:
        assert (
            ROOT / item
        ).exists()


def test_readme_has_phase28_section():
    readme = (
        ROOT / "README.md"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "Production MLOps Architecture"
        in readme
    )


def test_architecture_contains_mermaid():
    document = (
        ROOT
        / "docs"
        / "architecture.md"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "```mermaid"
        in document
    )

    assert (
        "TreeSHAP"
        in document
    )


def test_portfolio_mentions_mlops_governance():
    document = (
        ROOT
        / "docs"
        / "portfolio-case-study.md"
    ).read_text(
        encoding="utf-8"
    ).lower()

    assert (
        "governed retraining"
        in document
    )

    assert (
        "controlled promotion"
        in document
    )

    assert (
        "feature contracts"
        in document
    )
