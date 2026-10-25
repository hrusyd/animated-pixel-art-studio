#!/usr/bin/env python3
"""Repository entry point; the distributable implementation lives in the skill."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).parent / "skills" / "animated-pixel-art-studio" / "scripts" / "studio.py"), run_name="__main__")
