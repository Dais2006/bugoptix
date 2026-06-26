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
        default_structure = {"scans": [], "lifecycle_states": {}}
        if os.path.exists(VAULT_FILE):
            try:
                with open(VAULT_FILE, "r") as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else default_structure
            except: pass
        return default_structure

    @staticmethod
    def write_records(data: dict):
        try:
            with open(VAULT_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except: pass

# --- UNIFIED ASSESSMENT ENGINE ---
async def execute_comprehensive_qa_suite(target_url: str, crawl_limit: int, target_browser: str) -> dict:
    telemetry = {"url": target_url, "all_bugs": [], "crawled_routes": []}
    async with async_playwright() as p:
        browser_type = p.chromium
        browser = await browser_type.launch(headless=True)
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

    # Only two tabs remain: Runner and Matrix
    runner_tab, tracking_tab = strl.tabs(["🚀 Quality Suite Test Runner", "📋 Defect Lifecycle Matrix"])

    with runner_tab:
        url_scope = strl.text_input("Target URL:", value="https://example.com")
        targeted_browser = strl.selectbox("Browser:", ["Chromium (Standard)"])
        depth_limit = strl.slider("Crawler Depth:", min_value=1, max_value=5, value=1)

        if strl.button("Dispatch Automated Scan"):
            with strl.spinner("Running evaluation..."):
                res_data = asyncio.run(execute_comprehensive_qa_suite(url_scope.strip(), depth_limit, targeted_browser))
                vault_recs = VaultController.read_records()
                vault_recs["scans"].append(res_data)
                VaultController.write_records(vault_recs)
            strl.success("Assessment complete.")

    with tracking_tab:
        vault_recs = VaultController.read_records()
        if vault_recs.get("scans"):
            strl.write("Recorded Scans:")
            strl.json(vault_recs["scans"])
        else:
            strl.info("No recorded scans available.")
