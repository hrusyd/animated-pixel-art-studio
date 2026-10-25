# Working in this repository

Read `skills/animated-pixel-art-studio/SKILL.md` for creative tasks. Keep the skill self-contained: scripts must work when only that folder is copied elsewhere. The root `studio.py` is a convenience launcher.

Use Python 3.10+ and Pillow. Do not add a model provider, paid service, telemetry, or network request to the renderer. Write original assets. The examples and code are MIT licensed; do not import unlicensed sprites.

For renderer changes run `python -m unittest discover -s tests -v`, regenerate examples with `python tools/build_examples.py` if needed, render at least one example, and inspect its contact sheet. Use an empty output directory. Never delete user scenes or overwrite outputs to make tests pass.

Keep README.md and README.id.md consistent. Do not claim video or visual checks passed without running them. `report.json` is diagnostic evidence, not an artistic quality score.
