from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.model_registry import (
    get_registry_status,
    promote_model,
    register_model,
    rollback_model,
)


def print_json(
    payload: object,
) -> None:
    print(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Versioned model registry "
            "management CLI."
        )
    )

    subparsers = (
        parser.add_subparsers(
            dest="command",
            required=True,
        )
    )

    subparsers.add_parser(
        "status"
    )

    register_parser = (
        subparsers.add_parser(
            "register"
        )
    )

    register_parser.add_argument(
        "--version",
        required=True,
    )

    register_parser.add_argument(
        "--path",
        required=True,
    )

    register_parser.add_argument(
        "--name",
        required=True,
    )

    register_parser.add_argument(
        "--description",
        default="",
    )

    promote_parser = (
        subparsers.add_parser(
            "promote"
        )
    )

    promote_parser.add_argument(
        "--version",
        required=True,
    )

    subparsers.add_parser(
        "rollback"
    )

    args = parser.parse_args()

    if args.command == "status":
        print_json(
            get_registry_status()
        )
        return

    if args.command == "register":
        result = register_model(
            version=args.version,
            model_path=Path(
                args.path
            ),
            model_name=args.name,
            description=(
                args.description
            ),
        )

        print_json(result)
        return

    if args.command == "promote":
        result = promote_model(
            args.version
        )

        print_json(result)
        return

    if args.command == "rollback":
        result = rollback_model()

        print_json(result)
        return


if __name__ == "__main__":
    main()
