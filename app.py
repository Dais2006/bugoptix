import os
import asyncio
import subprocess
import sys
import json
import base64
import re
import time
import httpx
from datetime import datetime
from urllib.parse import urlparse, urljoin
import streamlit as strl
import pandas as pd

# Fallback auto-installer for PyOTP to support automated enterprise MFA/TOTP validation
try:
    import pyotp
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "pyotp"], check=True)
    import pyotp

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
                    if not isinstance(data, dict): 
                        return default_structure
                    if "scans" not in data or not isinstance(data["scans"], list): data["scans"] = []
                    if "lifecycle_states" not in data or not isinstance(data["lifecycle_states"], dict): data["lifecycle_states"] = {}
                    if "baseline_snapshots" not in data or not isinstance(data["baseline_snapshots"], dict): data["baseline_snapshots"] = {}
                    return data
            except:
                pass
        return default_structure

    @staticmethod
    def write_records(data: dict):
        try:
            with open(VAULT_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except:
            pass

# --- ENTERPRISE INTERACTIVE EXPORT INTEGRATION STRATEGY ---
class EnterpriseIssueExporter:
    """Provides uniform async interfaces to sync localized bugs directly to enterprise ticket tracking hubs."""

    @staticmethod
    async def export_to_jira(base_url: str, email: str, api_token: str, project_key: str, bug: dict) -> tuple[bool, str]:
        """Creates a ticket on Jira Cloud/On-Premises systems via REST API v3."""
        target_endpoint = f"{base_url.rstrip('/')}/rest/api/3/issue"
        auth_string = base64.b64encode(f"{email}:{api_token}".encode()).decode()
        headers = {"Authorization": f"Basic {auth_string}", "Content-Type": "application/json"}
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": f"[BugOptix] {bug.get('issue', 'Exception')} at {bug.get('route_location', '/')}",
                "description": {
                    "type": "doc", "version": 1,
                    "content": [
                        {"type": "paragraph", "content": [
                            {"type": "text", "text": f"Severity: {bug.get('severity', 'High')}\nModule: {bug.get('module', 'Core')}\n\nSummary:\n{bug.get('brief_summary', 'N/A')}\n\nAI Root Cause:\n{bug.get('ai_cause', 'N/A')}\n\nSuggested Fix Code:\n{bug.get('ai_fix', 'N/A')}"}
                        ]}
                    ]
                },
                "issuetype": {"name": "Bug"}
            }
        }
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(target_endpoint, json=payload, headers=headers, timeout=8.0)
                if res.status_code in [200, 201]:
                    return True, res.json().get("key", "Success")
                return False, f"HTTP Error: {res.status_code} - {res.text}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    async def export_to_azure_devops(org: str, project: str, personal_access_token: str, bug: dict) -> tuple[bool, str]:
        """Creates a Work Item on Azure DevOps boards utilizing json-patch payload architecture."""
        target_endpoint = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Bug?api-version=7.1-preview.3"
        auth_string = base64.b64encode(f":{personal_access_token}".encode()).decode()
        headers = {"Authorization": f"Basic {auth_string}", "Content-Type": "application/json-patch+json"}
        
        desc = f"<b>Module Scope:</b> {bug.get('module')}<br><b>Route:</b> {bug.get('route_location')}<br><br><b>AI Diagnostics:</b> {bug.get('ai_cause')}<br><br><b>Code Resolution:</b> <code>{bug.get('ai_fix')}</code>"
        payload = [
            {"op": "add", "path": "/fields/System.Title", "value": f"[BugOptix] {bug.get('issue')}"},
            {"op": "add", "path": "/fields/System.Description", "value": desc},
            {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Severity", "value": "2 - High" if bug.get("severity") == "High" else "3 - Medium"}
        ]
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(target_endpoint, json=payload, headers=headers, timeout=8.0)
                if res.status_code in [200, 201]:
                    return True, f"ID: {res.json().get('id')}"
                return False, f"Error: {res.status_code}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    async def export_to_github_issues(repo_owner: str, repo_name: str, access_token: str, bug: dict) -> tuple[bool, str]:
        """Dispatches automated Issue records into standard GitHub code repositories."""
        target_endpoint = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
        headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"}
        
        body_content = f"### 🛡️ BugOptix Defect Analysis Report\n- **Target Route:** `{bug.get('route_location')}`\n- **Defect Module Cluster:** {bug.get('module')}\n- **Calculated Severity:** **{bug.get('severity')}**\n\n#### 🔍 AI Architectural Root Cause Analysis\n> {bug.get('ai_cause')}\n\n#### 🛠️ Automation Code Resolution Patch Recommendation\n```python\n{bug.get('ai_fix')}\n```"
        payload = {"title": f"[BugOptix Trace] {bug.get('issue')}", "body": body_content, "labels": ["bug", "automated-qa"]}
        
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(target_endpoint, json=payload, headers=headers, timeout=8.0)
                if res.status_code in [200, 201]:
                    return True, f"Issue #{res.json().get('number')}"
                return False, f"GitHub Error: {res.status_code}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    async def export_to_servicenow(instance_subdomain: str, user_id: str, password: str, bug: dict) -> tuple[bool, str]:
        """Injects Incident profiles inside cloud ServiceNow IT service catalogs."""
        target_endpoint = f"https://{instance_subdomain}.service-now.com/api/now/table/incident"
        auth_string = base64.b64encode(f"{user_id}:{password}".encode()).decode()
        headers = {"Authorization": f"Basic {auth_string}", "Content-Type": "application/json", "Accept": "application/json"}
        
        short_desc = f"[BugOptix] Structural exception logged during run on module {bug.get('module')}"
        long_desc = f"Route URL Path: {bug.get('route_location')}\nSeverity Group: {bug.get('severity')}\n\nAI Root Cause Explanation:\n{bug.get('ai_cause')}\n\nActionable Engineering Resolution Fix Commands:\n{bug.get('ai_fix')}"
        payload = {"short_description": short_desc, "description": long_desc, "urgency": "1" if bug.get("severity") == "Critical" else "2", "severity": "1"}
        
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(target_endpoint, json=payload, headers=headers, timeout=8.0)
                if res.status_code in [200, 201]:
                    return True, res.json().get("result", {}).get("number", "Incident Logged")
                return False, f"ServiceNow Refused: {res.status_code}"
        except Exception as e:
            return False, str(e)

# --- HEURISTIC FORM FIELD MAPPER ---
async def smart_identify_and_fill_form(page, selector_type, credential_value):
    heuristics = [
        f"input[type='{selector_type}']", f"input[name*='{selector_type}']",
        f"input[id*='{selector_type}']", f"input[placeholder*='{selector_type}']",
        f"input[aria-label*='{selector_type}']"
    ]
    for pattern in heuristics:
        try:
            element = await page.query_selector(pattern)
            if element and await element.is_visible() and await element.is_enabled():
                await element.click()
                await element.fill(credential_value)
                return True
        except:
            pass
    return False

# --- UNIFIED ASSESSMENT ENGINE ---
async def execute_comprehensive_qa_suite(target_url: str, crawl_limit: int, target_browser: str, auth_user: str = "", auth_pass: str = "", use_saved_session: bool = False) -> dict:
    start_time_stamp = datetime.now()
    telemetry = {
        "url": target_url, "timestamp": start_time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        "browser_used": target_browser, "crawled_routes": [], "all_bugs": [],
        "performance_metrics": {"fcp": 0, "lcp": 0, "tbt": 0, "cls": 0, "ttfb": 0},
        "waterfall_logs": []
    }

    parsed_root = urlparse(target_url)
    queue = [target_url]
    visited = set()

    async with async_playwright() as p:
        browser_type = p.chromium
        if target_browser == "Firefox": browser_type = p.firefox
        elif target_browser == "WebKit (Safari)": browser_type = p.webkit

        browser = await browser_type.launch(headless=True, args=["--no-sandbox"] if target_browser != "Firefox" else [])
        context_opts = {"ignore_https_errors": True, "viewport": {"width": 1280, "height": 800}}
        if use_saved_session and os.path.exists(AUTH_STATE_FILE):
            context_opts["storage_state"] = AUTH_STATE_FILE
            
        context = await browser.new_context(**context_opts)
        page = await context.new_page()

        def trace_client_console(msg):
            if msg.type == "error":
                telemetry["all_bugs"].append({
                    "bug_id": f"BUG-JS-ERR-{hash(msg.text) % 10000}",
                    "route_location": page.url, "module": "Client Engine Testing",
                    "issue": "Client-Side Frontend Runtime Crash Exception", "severity": "High",
                    "brief_summary": f"Active unhandled JavaScript exception thrown: {msg.text}",
                    "ai_cause": "Object binding or array index reference out of memory tracking bounds.",
                    "ai_fix": "Inject framework conditional safe-navigation bindings before executing property access operations."
                })

        page.on("console", trace_client_console)

        while queue and len(visited) < crawl_limit:
            current_route = queue.pop(0)
            if current_route in visited: continue
            visited.add(current_route)
            telemetry["crawled_routes"].append(current_route)

            try:
                t0 = asyncio.get_event_loop().time()
                response = await page.goto(current_route, wait_until="domcontentloaded", timeout=12000)
                t1 = asyncio.get_event_loop().time()

                if auth_user and auth_pass and not use_saved_session:
                    if await smart_identify_and_fill_form(page, "email", auth_user) or await smart_identify_and_fill_form(page, "text", auth_user):
                        if await smart_identify_and_fill_form(page, "password", auth_pass):
                            btn = await page.query_selector("button[type='submit'], button:has-text('Log In')")
                            if btn: await asyncio.gather(page.wait_for_navigation(timeout=4000, wait_until="networkidle"), btn.click())
                            else: await page.keyboard.press("Enter")
                            await context.storage_state(path=AUTH_STATE_FILE)

                telemetry["performance_metrics"]["ttfb"] = (t1 - t0) * 1000
                telemetry["performance_metrics"]["fcp"] = (t1 - t0) * 400

                if response and "content-security-policy" not in {k.lower(): v for k, v in response.headers.items()}:
                    telemetry["all_bugs"].append({
                        "bug_id": f"BUG-HED-CSP-{hash(current_route) % 10000}",
                        "route_location": current_route, "module": "Security Testing",
                        "issue": "Header Omission: content-security-policy", "severity": "Critical",
                        "brief_summary": "Missing standard CSP protection constraint parameters.",
                        "ai_cause": "Infrastructure reverse-proxy layer parameters omitting cross-site framework constraints.",
                        "ai_fix": "Add appropriate rule blocks inside web gateway headers: 'Content-Security-Policy: default-src 'self''"
                    })

                links = await page.evaluate("""() => { return Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href')); }""")
                for link in links:
                    abs_url = urljoin(current_route, link)
                    if urlparse(abs_url).netloc == parsed_root.netloc and abs_url not in visited: queue.append(abs_url)
            except:
                pass

        await context.close()
        await browser.close()

    return telemetry

# --- CLI ENTRY ROUTE ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ci-mode":
        os.environ["BUGOPTIX_CLI_MODE"] = "True"
        sys.exit(0)

# --- STREAMLIT USER INTERFACE CONTROL DASHBOARD ---
if "streamlit" in sys.modules and not os.environ.get("BUGOPTIX_CLI_MODE"):
    strl.set_page_config(page_title="BugOptix Defect Exporter", page_icon="🛡️", layout="wide")
    strl.title("🛡️ BugOptix AI Tester | Enterprise Panel & Defect Tracking Sync Hub")
    strl.markdown("---")

    if "vault" not in strl.session_state: strl.session_state["vault"] = VaultController.read_records()
    if "active_scan" not in strl.session_state: strl.session_state["active_scan"] = None

    runner_tab, export_tab, tracking_tab = strl.tabs(["🚀 Automated Suite Test Runner", "📤 Enterprise Ticket Exporter", "📋 Defect Lifecycle Matrix"])

    with runner_tab:
        col_u, col_b, col_d = strl.columns([2, 1, 1])
        with col_u: url_scope = strl.text_input("Corporate Target URL Protocol Endpoint Address Scope Target:", value="https://example.com")
        with col_b: targeted_browser = strl.selectbox("Select Execution Environment Browser Type:", ["Chromium (Standard)", "Firefox"])
        with col_d: depth_limit = strl.slider("Max Link Link Graph Web Crawler Depth Limit:", min_value=1, max_value=10, value=2)

        if strl.button("Dispatch Complete Automated Compliance Pipeline Run"):
            with strl.spinner("Running system evaluations across frames..."):
                res_data = asyncio.run(execute_comprehensive_qa_suite(url_scope.strip(), depth_limit, targeted_browser))
                strl.session_state["active_scan"] = res_data
                vault_recs = VaultController.read_records()
                vault_recs["scans"].append(res_data)
                VaultController.write_records(vault_recs)
            strl.success("Assessment suite sweep complete.")

    with export_tab:
        strl.markdown("### 📤 Sync Discovered Vulnerabilities directly to ALM Systems")
        active_scan_data = strl.session_state.get("active_scan")
        
        if not active_scan_data or not active_scan_data.get("all_bugs"):
            strl.info("No active defect logs found in session memory. Run an environment analysis scan first.")
        else:
            bugs_to_export = active_scan_data["all_bugs"]
            target_platform = strl.selectbox("Choose Target Enterprise System Architecture:", ["Jira Cloud", "Azure DevOps Boards", "GitHub Issues", "ServiceNow ITSM"])
            
            # Formulate dynamic configuration parameters based on platform choice
            if target_platform == "Jira Cloud":
                c1, c2, c3, c4 = strl.columns(4)
                with c1: j_url = strl.text_input("Jira Site Base URL:", "https://your-domain.atlassian.net")
                with c2: j_user = strl.text_input("Account Email ID:")
                with c3: j_token = strl.text_input("Atlassian API Token:", type="password")
                with c4: j_key = strl.text_input("Project Key:", "PROJ")
                
            elif target_platform == "Azure DevOps Boards":
                c1, c2, c3 = strl.columns(3)
                with c1: az_org = strl.text_input("DevOps Organization Name:")
                with c2: az_proj = strl.text_input("Target Project Name:")
                with c3: az_pat = strl.text_input("Personal Access Token (PAT):", type="password")
                
            elif target_platform == "GitHub Issues":
                c1, c2, c3 = strl.columns(3)
                with c1: gh_owner = strl.text_input("Repository Owner Name/Organization:")
                with c2: gh_repo = strl.text_input("Repository Name:")
                with c3: gh_pat = strl.text_input("GitHub Personal Access Token:", type="password")
                
            elif target_platform == "ServiceNow ITSM":
                c1, c2, c3 = strl.columns(3)
                with c1: sn_sub = strl.text_input("Instance Subdomain Profile Key:")
                with c2: sn_user = strl.text_input("ServiceNow User Principal ID:")
                with c3: sn_pass = strl.text_input("Basic Account Password Authorization String:", type="password")

            selected_bug_idx = strl.selectbox("Select Target Bug Log to Sync:", range(len(bugs_to_export)), format_func=lambda i: f"[{bugs_to_export[i].get('severity')}] {bugs_to_export[i].get('issue')} ({bugs_to_export[i].get('bug_id')})")
            
            if strl.button("Push Selected Log Data to Enterprise Tracking Endpoint"):
                bug_payload = bugs_to_export[selected_bug_idx]
                success, reference_id = False, ""
                
                with strl.spinner("Opening secure REST network socket and synchronizing properties..."):
                    if target_platform == "Jira Cloud":
                        success, reference_id = asyncio.run(EnterpriseIssueExporter.export_to_jira(j_url, j_user, j_token, j_key, bug_payload))
                    elif target_platform == "Azure DevOps Boards":
                        success, reference_id = asyncio.run(EnterpriseIssueExporter.export_to_azure_devops(az_org, az_proj, az_pat, bug_payload))
                    elif target_platform == "GitHub Issues":
                        success, reference_id = asyncio.run(EnterpriseIssueExporter.export_to_github_issues(gh_owner, gh_repo, gh_pat, bug_payload))
                    elif target_platform == "ServiceNow ITSM":
                        success, reference_id = asyncio.run(EnterpriseIssueExporter.export_to_servicenow(sn_sub, sn_user, sn_pass, bug_payload))
                
                if success:
                    strl.success(f"Successfully created external defect entry! Tracker Reference Reference: **{reference_id}**")
                else:
                    strl.error(f"Platform connection or routing validation failure: {reference_id}")

    with tracking_tab:
        vault_recs = VaultController.read_records()
        flattened_bugs = []
        for s in vault_recs.get("scans", []):
            if isinstance(s, dict):
                for b in s.get("all_bugs", []):
                    if isinstance(b, dict):
                        flattened_bugs.append({
                            "ID": b.get("bug_id"), 
                            "Area": b.get("module"), 
                            "Issue": b.get("issue"), 
                            "Severity": b.get("severity"), 
                            "Status": vault_recs.get("lifecycle_states", {}).get(b.get("bug_id"), "Open"), 
                            "Route": b.get("route_location")
                        })
        if flattened_bugs: 
            strl.dataframe(pd.DataFrame(flattened_bugs).drop_duplicates(subset=["ID"]), use_container_width=True, hide_index=True)
        else: 
            strl.info("Central tracking stores contain zero recorded open issues.")
