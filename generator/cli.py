from __future__ import annotations

import argparse
from pathlib import Path

from .validation import validate_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ha-contract-ui")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser(
        "validate",
        help="validate contracts, semantic inventory and panel manifests",
    )
    validate.add_argument(
        "repo_root",
        nargs="?",
        default=".",
        type=Path,
        help="repository root (default: current directory)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "validate":
        issues = validate_repository(args.repo_root)
        if issues:
            for issue in issues:
                print(issue)
            print(f"Validation failed: {len(issues)} issue(s).")
            return 1

        print("Contract-generated UI inputs are valid.")
        return 0

    raise AssertionError(f"unhandled command: {args.command}")
