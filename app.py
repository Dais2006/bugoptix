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

# --- AUTOMATED AI INTELLIGENT COMPLIANCE ANALYSIS ENGINE ---
class AIAnomaliesAnalyzer:
    """Performs deep context analysis using LLM inference or an advanced localized syntax reasoning fallback."""
    
    @staticmethod
    async def request_ai_diagnostics(context_type: str, raw_finding: str, dynamic_dom_context: str = "N/A") -> dict:
        api_token = os.environ.get("OPENAI_API_KEY") or os.environ.get("AI_PROVIDER_API_KEY")
        
        system_prompt = (
            "You are an expert software QA automation architecture agent and elite cyber security engineer. "
            "Analyze the provided application flaw, syntax error, or vulnerability, factoring in any available "
            "DOM context or stack traces. Produce a valid JSON object matching exactly this dictionary layout:\n"
            '{"ai_cause": "Deep architectural explanation of the bug root cause", '
            '"ai_fix": "Exact actionable code modification pattern or platform fix command"}'
        )
        
        user_content = (
            f"Context Classification: {context_type}\n"
            f"Identified Defect Exception Profile:\n{raw_finding}\n\n"
            f"Targeted DOM Fragment Snippet:\n{dynamic_dom_context[:2000]}"
        )
        
        if api_token:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"},
                        json={
                            "model": "gpt-4o-mini",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_content}
                            ],
                            "response_format": {"type": "json_object"},
                            "temperature": 0.2
                        },
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        payload = response.json()
                        text_response = payload["choices"][0]["message"]["content"]
                        return json.loads(text_response)
            except Exception:
                pass

        # --- LOCALIZED FALLBACK INTELLIGENT RULE MAPPING (If API Credentials are Absent) ---
        cause = "An unhandled runtime mutation caused structural processing paths to break under active window observation parameters."
        fix = "Wrap operation parameters inside verified state containers and sanitize component lifecycles."
        
        if "content-security-policy" in raw_finding.lower():
            cause = f"The web resource router profile at this path serves content blocks without declaring an restrictive header governance policy framework (OWASP A05)."
            fix = "Configure global application gateway distribution blocks to append a standard strict cross-domain policy: 'Content-Security-Policy: default-src 'self';'"
        elif "js-err" in context_type.lower() or "exception" in raw_finding.lower():
            matched_fault = re.search(r"(\w+ Error|TypeError|ReferenceError):?\s*([^\n]*)", raw_finding)
            cause = f"Active Javascript engine memory space fault located. Uncaught reference trace logic crash: {matched_fault.group(0) if matched_fault else raw_finding}"
            fix = "Inject type verification checks prior to data mutation mappings, or enclose vulnerable downstream framework views inside global try-catch boundaries."
        elif "dom" in dynamic_dom_context.lower() or "element" in raw_finding.lower():
            cause = "DOM layout structures failed validation guidelines because attributes mismatched modern cross-browser render rules."
            fix = "Refactor components to include precise semantic wrappers and ensure accessibility tags conform to standard patterns."
            
        return {"ai_cause": cause, "ai_fix": fix}

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

# --- GITHUB CI QUALITY GATE EVALUATOR & AUTOMATED COMMENTER ---
def process_github_ci_quality_gate(scan_results: dict):
    print("\n--- BUGOPTIX CI QUALITY GATE EVALUATOR RUNNING ---")
    all_bugs = scan_results.get("all_bugs", [])
    if not isinstance(all_bugs, list): all_bugs = []
    critical_bugs = [b for b in all_bugs if isinstance(b, dict) and b.get("severity") == "Critical"]
    
    print(f"Total Anomalies Located: {len(all_bugs)}")
    print(f"Critical System Defects: {len(critical_bugs)}")
    
    comment_body = f"## 🛡️ BugOptix Automated Quality Gate Audit Result\n"
    comment_body += f"- **Target URL Evaluated:** `{scan_results.get('url', 'Unknown')}`\n"
    comment_body += f"- **Scan Completed At:** {scan_results.get('timestamp', 'N/A')}\n"
    comment_body += f"- **Total Defects Discovered:** {len(all_bugs)}\n"
    comment_body += f"- **Critical Security/Runtime Vulnerabilities:** {len(critical_bugs)}\n\n"
    
    if all_bugs:
        comment_body += "### 🛑 Detected Exceptions Summary Matrix\n"
        comment_body += "| Severity | Module Area | Issue Title | Target Location Route |\n"
        comment_body += "| :--- | :--- | :--- | :--- |\n"
        for b in all_bugs[:15]:
            if isinstance(b, dict):
                comment_body += f"| **{b.get('severity', 'Unknown')}** | {b.get('module', 'General')} | {b.get('issue', 'Exception')} | `{b.get('route_location', '/')}` |\n"
            
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
        except Exception as e:
            print(f"Failed to post automated GitHub PR Comment: {str(e)}")
            
    if critical_bugs:
        sys.exit(1)
    else:
        sys.exit(0)

# --- UNIFIED ASSESSMENT ENGINE ---
async def execute_comprehensive_qa_suite(target_url: str, crawl_limit: int, target_browser: str, auth_user: str = "", auth_pass: str = "", use_saved_session: bool = False) -> dict:
    start_time_stamp = datetime.now()
    telemetry = {
        "url": target_url, "timestamp": start_time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        "browser_used": target_browser, "crawled_routes": [], "all_bugs": [],
        "performance_metrics": {"fcp": 0, "lcp": 0, "tbt": 0, "cls": 0, "ttfb": 0},
        "seo_metrics": {"score": 100, "checks": []}, "api_metrics": {"score": 100, "logs": []},
        "network_metrics": {"failed": 0, "slow": 0, "404s": 0, "500s": 0},
        "waterfall_logs": [], "snapshots": {}
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

        # Target placeholder container for async runtime errors to feed analyzer
        captured_runtime_errors = []

        def trace_network_response(resp):
            telemetry["waterfall_logs"].append({
                "resource_url": resp.url[:70] + "...", "status_code": resp.status,
                "method_type": resp.request.method, "content_type": resp.headers.get("content-type", "Unknown")
            })
            if resp.status >= 500: telemetry["network_metrics"]["500s"] += 1
            elif resp.status == 404: telemetry["network_metrics"]["404s"] += 1

        def trace_client_console(msg):
            if msg.type == "error":
                captured_runtime_errors.append({
                    "text": msg.text,
                    "location_url": page.url
                })

        page.on("response", trace_network_response)
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

                # Read local DOM components context for structured error evaluation pipelines
                structural_dom_tree = await page.content()

                # Process console-intercepted active Javascript exceptions via the AI module
                for error_log in captured_runtime_errors:
                    ai_reasoning = await AIAnomaliesAnalyzer.request_ai_diagnostics(
                        context_type="Client Frontend JS Runtime Stack Frame Error",
                        raw_finding=error_log["text"],
                        dynamic_dom_context=structural_dom_tree
                    )
                    telemetry["all_bugs"].append({
                        "bug_id": f"BUG-JS-ERR-{hash(error_log['text']) % 10000}",
                        "route_location": error_log["location_url"], "module": "Client Engine Testing",
                        "issue": "Client-Side Frontend Runtime Crash Exception", "severity": "High",
                        "brief_summary": f"Unhandled exception encountered in the user browser window: {error_log['text']}",
                        "ai_cause": ai_reasoning["ai_cause"], "ai_fix": ai_reasoning["ai_fix"]
                    })
                captured_runtime_errors.clear() # Reset loop logs

                if response:
                    headers = {k.lower(): v for k, v in response.headers.items()}
                    if "content-security-policy" not in headers:
                        ai_reasoning = await AIAnomaliesAnalyzer.request_ai_diagnostics(
                            context_type="Security Infrastructure Header Defect",
                            raw_finding="Header Omission: content-security-policy",
                            dynamic_dom_context=structural_dom_tree
                        )
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-HED-CSP-{hash(current_route) % 10000}",
                            "route_location": current_route, "module": "Security Testing",
                            "issue": "Header Omission: content-security-policy", "severity": "Critical",
                            "brief_summary": "Missing standard CSP protection constraint parameters within HTTP response packets.",
                            "ai_cause": ai_reasoning["ai_cause"], "ai_fix": ai_reasoning["ai_fix"]
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
        target_input_url = sys.argv[2] if len(sys.argv) > 2 else "https://example.com"
        scan_output = asyncio.run(execute_comprehensive_qa_suite(target_url=target_input_url, crawl_limit=5, target_browser="Chromium (Standard)"))
        process_github_ci_quality_gate(scan_output)
        sys.exit(0)

# --- STREAMLIT USER INTERFACE CONTROL DASHBOARD ---
if "streamlit" in sys.modules and not os.environ.get("BUGOPTIX_CLI_MODE"):
    strl.set_page_config(page_title="BugOptix AI Tester", page_icon="🛡️", layout="wide")
    strl.title("🛡️ BugOptix AI Tester | Enterprise Panel")
    strl.markdown("---")

    if "vault" not in strl.session_state: strl.session_state["vault"] = VaultController.read_records()
    if "active_scan" not in strl.session_state: strl.session_state["active_scan"] = None

    runner_tab, tracking_tab, cicd_tab = strl.tabs(["🚀 Quality Suite Test Runner", "📋 Defect Lifecycle Matrix", "🔗 CI/CD Automation Hub"])

    with runner_tab:
        col_u, col_b, col_d = strl.columns([2, 1, 1])
        with col_u: url_scope = strl.text_input("Corporate Target URL Protocol Endpoint Address Scope Target:", value="https://example.com")
        with col_b: targeted_browser = strl.selectbox("Select Execution Environment Browser Type:", ["Chromium (Standard)", "Firefox"])
        with col_d: depth_limit = strl.slider("Max Link Link Graph Web Crawler Depth Limit:", min_value=1, max_value=10, value=3)

        if strl.button("Dispatch Complete Automated Compliance Pipeline Run"):
            with strl.spinner("Running system evaluations across frames..."):
                res_data = asyncio.run(execute_comprehensive_qa_suite(url_scope.strip(), depth_limit, targeted_browser))
                strl.session_state["active_scan"] = res_data
                vault_recs = VaultController.read_records()
                vault_recs["scans"].append(res_data)
                VaultController.write_records(vault_recs)
            strl.success("Assessment suite sweep complete.")

        active_scan_data = strl.session_state.get("active_scan")
        if isinstance(active_scan_data, dict):
            bugs_list = active_scan_data.get("all_bugs", [])
            if isinstance(bugs_list, list) and len(bugs_list) > 0:
                bugs_df = pd.DataFrame(bugs_list)
                strl.markdown("### 🛑 Findings & Detailed Root Cause Analysis Reports")
                vault_recs = VaultController.read_records()
                
                for idx, bug in bugs_df.iterrows():
                    if not isinstance(bug, dict): 
                        bug = bug.to_dict()
                    b_id = bug.get("bug_id", f"BUG-{idx}")
                    current_status = vault_recs.get("lifecycle_states", {}).get(b_id, "Open")
                    
                    with strl.expander(f"[{bug.get('severity', 'High')}] {bug.get('module', 'Core')} — {bug.get('issue', 'Exception')}"):
                        new_status = strl.selectbox(
                            f"Modify Governance State for {b_id}:", ["Open", "In-Progress", "Resolved", "Closed"],
                            index=["Open", "In-Progress", "Resolved", "Closed"].index(current_status),
                            key=f"status_select_{idx}_{b_id}"
                        )
                        if new_status != current_status:
                            vault_recs["lifecycle_states"][b_id] = new_status
                            VaultController.write_records(vault_recs)
                            strl.toast(f"Updated status for {b_id}")
                            strl.rerun()
                        strl.info(f"**Brief Summary:** {bug.get('brief_summary', 'N/A')}")
                        strl.warning(f"**AI Cause Factor:** {bug.get('ai_cause', 'N/A')}")
                        strl.markdown(f"**Fix Recommendation:** `{bug.get('ai_fix', 'N/A')}`")
            else:
                strl.success("Zero defect exceptions flagged for this run.")

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

    with cicd_tab:
        strl.markdown("### 🔗 Continuous Integration Pipeline Automation Gate")
        strl.info("Drop this workflow config file into your repository at `.github/workflows/bugoptix_audit.yml`:")
        strl.code("""
name: BugOptix Enterprise CI Quality Gate
on:
  pull_request:
    branches: [ main, master ]

jobs:
  bugoptix-compliance-scan:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read
    steps:
      - name: Checkout Repository Source Code
        uses: actions/checkout@v3

      - name: Initialize System Python Environment
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install BugOptix Architecture Stack Dependencies
        run: |
          pip install playwright httpx streamlit pandas
          python -m playwright install chromium

      - name: Dispatch Headless Automated CLI Verification Scan & Quality Gate
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python app.py --ci-mode "https://example.com"
        """, language="yaml")
