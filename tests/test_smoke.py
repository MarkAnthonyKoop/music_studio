"""Smoke test for music_studio — design-only project, no importable package."""

def test_readme_exists():
    from pathlib import Path
    assert Path(__file__).parent.parent.joinpath("README.md").exists()
