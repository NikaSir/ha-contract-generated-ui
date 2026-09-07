#!/usr/bin/env python3
"""Fetch public, revision-pinned NikaS source snapshots for inspection."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def read_targets(registry: Path) -> list[tuple[str, str]]:
    targets: list[tuple[str, str]] = []
    seen: set[str] = set()
    profiles = sorted(registry.glob("*.json"))
    if not profiles:
        raise ValueError("No repository profiles found")
    for path in profiles:
        profile = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(profile, dict):
            raise ValueError(f"Expected a profile object in {path.name}")
        repository = profile.get("repository", "")
        revision = profile.get("source_revision", "")
        if not isinstance(repository, str) or not re.fullmatch(
            r"NikaSir/(?:\.github|[A-Za-z0-9][A-Za-z0-9._-]*)", repository
        ):
            raise ValueError(f"Invalid NikaS repository in {path.name}")
        if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise ValueError(f"Expected a full source revision in {path.name}")
        if repository in seen:
            raise ValueError(f"Duplicate repository: {repository}")
        seen.add(repository)
        targets.append((repository, revision))
    return targets


def checkout(registry: Path, destination: Path) -> None:
    targets = read_targets(registry)
    # Validate every destination before starting any download. Never reuse or
    # overwrite a user's checkout, including a dangling symbolic link.
    destinations = [destination / repo.split("/")[1] for repo, _ in targets]
    for path in destinations:
        if path.exists() or path.is_symlink():
            raise ValueError(f"Snapshot destination already exists: {path}")
    destination.mkdir(parents=True, exist_ok=True)
    for (repository, revision), path in zip(targets, destinations, strict=True):
        subprocess.run(["git", "init", "--quiet", str(path)], check=True)
        subprocess.run(
            ["git", "-C", str(path), "remote", "add", "origin",
             f"https://github.com/{repository}.git"], check=True,
        )
        subprocess.run(
            ["git", "-C", str(path), "-c", "protocol.file.allow=never",
             "fetch", "--quiet", "--depth", "1", "origin", revision],
            check=True, timeout=120,
        )
        subprocess.run(
            ["git", "-C", str(path), "checkout", "--quiet", "--detach", "FETCH_HEAD"],
            check=True,
        )
        actual = subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True,
        ).strip()
        if actual != revision:
            raise ValueError(f"Fetched revision mismatch for {repository}")
        print(f"{repository} {actual}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    try:
        checkout(args.registry, args.destination)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(2, f"Snapshot checkout failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
