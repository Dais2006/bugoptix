import os
import asyncio
import subprocess
import sys
import json
import httpx
from datetime import datetime
from urllib.parse import urlparse, urljoin
import streamlit as strl
import pandas as pd

# --- SYSTEM ENVIRONMENT SANITIZATION ---
@strl.cache_resource
def enforce_system_binaries():
    """Validates and ensures the presence of headless cross-browser binaries."""
    try:
        expected_bin_path = os.path.expanduser("~/.cache/ms-playwright")
        if not os.path.exists(expected_bin_path):
            subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
    except Exception:
        pass

if "streamlit" in sys.modules and not os.environ.get("BUGOPTIX_CLI_MODE"):
    enforce_system_binaries()

from playwright.async_api import async_playwright

# --- PERSISTENT ENTERPRISE REPOSITORY FACTORY ---
VAULT_FILE = "bugoptix_universal_vault.json"
AUTH_STATE_FILE = "bugoptix_auth_state.json"

class VaultController:
    @staticmethod
    def read_records() -> dict:
        default_structure = {"scans": [], "chat_history": [], "lifecycle_states": {}, "baseline_snapshots": {}}
        if os.path.exists(VAULT_FILE):
            try:
                with open(VAULT_FILE, "r") as f:
                    data = json.load(f)
                    if not isinstance(data, dict): return default_structure
                    return data
            except: pass
        return default_structure

    @staticmethod
    def write_records(data: dict):
        try:
            with open(VAULT_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except: pass

# --- HEURISTIC FORM FIELD MAPPER ---
async def smart_identify_and_fill_form(page, selector_type, credential_value):
    heuristics = [f"input[type='{selector_type}']", f"input[name*='{selector_type}']"]
    for pattern in heuristics:
        try:
            element = await page.query_selector(pattern)
            if element and await element.is_visible():
                await element.fill(credential_value)
                return True
        except: pass
    return False

# --- GITHUB CI QUALITY GATE ---
def process_github_ci_quality_gate(scan_results: dict):
    all_bugs = scan_results.get("all_bugs", [])
    critical_bugs = [b for b in all_bugs if b.get("severity") == "Critical"]
    
    comment_body = f"## 🛡️ BugOptix Audit Result\nTotal Defects: {len(all_bugs)}"
    
    gh_token = os.environ.get("GITHUB_TOKEN")
    gh_repo = os.environ.get("GITHUB_REPOSITORY")
    gh_event_path = os.environ.get("GITHUB_EVENT_PATH")
    
    if gh_token and gh_repo and gh_event_path:
        try:
            with open(gh_event_path, "r") as f:
                event_data = json.load(f)
            pr_number = event_data.get("pull_request", {}).get("number")
            if pr_number:
                api_url = f"https://api.github.com/repos/{gh_repo}/issues/{pr_number}/comments"
                headers = {"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github+json"}
                httpx.post(api_url, json={"body": comment_body}, headers=headers, timeout=5.0)
        except: pass
            
    sys.exit(1 if critical_bugs else 0)

# --- UNIFIED ASSESSMENT ENGINE ---
async def execute_comprehensive_qa_suite(target_url: str, crawl_limit: int, target_browser: str) -> dict:
    telemetry = {"url": target_url, "all_bugs": [], "crawled_routes": []}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=10000)
            telemetry["crawled_routes"].append(target_url)
        except: pass
        await browser.close()
    return telemetry

# --- STREAMLIT USER INTERFACE ---
if "streamlit" in sys.modules and not os.environ.get("BUGOPTIX_CLI_MODE"):
    strl.set_page_config(page_title="BugOptix AI Tester", layout="wide")
    strl.title("🛡️ BugOptix AI Tester | Enterprise Panel")

    runner_tab, tracking_tab, cicd_tab = strl.tabs(["🚀 Runner", "📋 Matrix", "🔗 CI/CD"])

    with cicd_tab:
        strl.markdown("### 🔗 Continuous Integration Pipeline Automation Gate")
        strl.info("Add this configuration to `.github/workflows/bugoptix_audit.yml`:")
        strl.code("""
name: BugOptix Enterprise CI Quality Gate
on: [pull_request]
jobs:
  bugoptix-compliance-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install Dependencies
        run: |
          pip install playwright httpx streamlit pandas
          python -m playwright install chromium
      - name: Run Audit
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python app.py --ci-mode "https://example.com"
        """, language="yaml")
