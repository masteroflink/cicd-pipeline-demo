#!/usr/bin/env python3
"""Capture portfolio screenshots from GitHub."""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_OWNER = "masteroflink"
REPO_NAME = "cicd-pipeline-demo"
SCREENSHOTS_DIR = Path("assets/screenshots")


def capture_screenshots() -> None:
    """Capture screenshots of GitHub pages."""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        # 1. GitHub Actions - Workflow runs
        print("Capturing GitHub Actions workflows...")
        page.goto(f"https://github.com/{REPO_OWNER}/{REPO_NAME}/actions")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(SCREENSHOTS_DIR / "github-actions-workflows.png"))
        print("  Saved github-actions-workflows.png")

        # 2. Successful workflow run
        print("Capturing successful workflow run...")
        page.goto(
            f"https://github.com/{REPO_OWNER}/{REPO_NAME}/actions/workflows/ci.yml"
        )
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(SCREENSHOTS_DIR / "ci-workflow-runs.png"))
        print("  Saved ci-workflow-runs.png")

        # 3. GitHub Container Registry
        print("Capturing Container Registry...")
        page.goto(f"https://github.com/{REPO_OWNER}/{REPO_NAME}/pkgs/container/{REPO_NAME}")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(SCREENSHOTS_DIR / "container-registry.png"))
        print("  Saved container-registry.png")

        # 4. GitHub Release
        print("Capturing GitHub Release...")
        page.goto(f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(SCREENSHOTS_DIR / "github-releases.png"))
        print("  Saved github-releases.png")

        # 5. Repository main page
        print("Capturing repository main page...")
        page.goto(f"https://github.com/{REPO_OWNER}/{REPO_NAME}")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(SCREENSHOTS_DIR / "repository-main.png"))
        print("  Saved repository-main.png")

        browser.close()

    print(f"\nAll screenshots saved to {SCREENSHOTS_DIR}")


if __name__ == "__main__":
    capture_screenshots()
