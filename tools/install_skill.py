#!/usr/bin/env python3
"""Copy the self-contained skill to an explicitly chosen agent skills directory."""
import argparse
from pathlib import Path
import shutil


def install(target):
    source = Path(__file__).resolve().parents[1] / "skills" / "animated-pixel-art-studio"
    destination = Path(target).expanduser().resolve() / source.name
    if destination.exists():
        raise ValueError(f"Refusing to overwrite {destination}. Choose another target or manage the existing installation explicitly.")
    if destination.is_relative_to(source):
        raise ValueError("Destination cannot be inside the source skill")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Your agent's skills directory, not the final skill folder")
    args = parser.parse_args()
    try:
        print(f"Copied skill to {install(args.target)}")
        print("Enable or load it according to your agent host. Dependencies are not installed automatically.")
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")
