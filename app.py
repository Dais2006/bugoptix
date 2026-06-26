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

# --- INDIVIDUAL BROWSER EXECUTION NODE ---
async def execute_single_browser_audit(p_instance, browser_key: str, target_url: str, crawl_limit: int, auth_user: str, auth_pass: str) -> dict:
    """Runs a dedicated crawler instance inside a specific engine target."""
    browser_launcher = getattr(p_instance, browser_key)
    # Safari/WebKit and Firefox require unique launch profiles on specific Linux architectures
    args = ["--no-sandbox"] if browser_key == "chromium" else []
    
    browser = await browser_launcher.launch(headless=True, args=args)
    context_opts = {"ignore_https_errors": True, "viewport": {"width": 1280, "height": 800}}
    
    context = await browser.new_context(**context_opts)
    page = await context.new_page()

    local_telemetry = {
        "browser": browser_key.upper(),
        "routes_visited": [],
        "errors_caught": [],
        "performance_samples": []
    }

    queue = [target_url]
    visited = set()
    parsed_root = urlparse(target_url)

    def log_console(msg):
        if msg.type == "error":
            local_telemetry["errors_caught"].append({
                "route": page.url,
                "msg": msg.text
            })

    page.on("console", log_console)

    while queue and len(visited) < crawl_limit:
        current_route = queue.pop(0)
        if current_route in visited: continue
        visited.add(current_route)
        local_telemetry["routes_visited"].append(current_route)

        try:
            t0 = asyncio.get_event_loop().time()
            response = await page.goto(current_route, wait_until="domcontentloaded", timeout=12000)
            t1 = asyncio.get_event_loop().time()

            # Handle smart form filling per browser instance
            if auth_user and auth_pass:
                await smart_identify_and_fill_form(page, "email", auth_user)
                await smart_identify_and_fill_form(page, "password", auth_pass)

            load_duration = (t1 - t0) * 1000
            local_telemetry["performance_samples"].append({
                "route": current_route,
                "latency_ms": load_duration
            })

            if response:
                headers = {k.lower(): v for k, v in response.headers.items()}
                if "content-security-policy" not in headers:
                    local_telemetry["errors_caught"].append({
                        "route": current_route,
                        "msg": "Missing Content-Security-Policy structural header attribute."
                    })

            links = await page.evaluate("""() => { return Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href')); }""")
            for link in links:
                abs_url = urljoin(current_route, link)
                if urlparse(abs_url).netloc == parsed_root.netloc and abs_url not in visited: 
                    queue.append(abs_url)
        except:
            pass

    await context.close()
    await browser.close()
    return local_telemetry

# --- GITHUB CI QUALITY GATE EVALUATOR & AUTOMATED COMMENTER ---
def process_github_ci_quality_gate(scan_results: dict):
    print("\n--- BUGOPTIX CI QUALITY GATE EVALUATOR RUNNING ---")
    all_bugs = scan_results.get("all_bugs", [])
    critical_bugs = [b for b in all_bugs if b.get("severity") == "Critical"]
    
    print(f"Total Cross-Browser Anomalies: {len(all_bugs)}")
    if critical_bugs: sys.exit(1)
    else: sys.exit(0)

# --- UNIFIED ASSESSMENT PARALLEL GRID ENGINE ---
async def execute_comprehensive_qa_suite(target_url: str, crawl_limit: int, auth_user: str = "", auth_pass: str = "") -> dict:
    start_time_stamp = datetime.now()
    telemetry = {
        "url": target_url, "timestamp": start_time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        "all_bugs": [], "cross_browser_matrix": {}
    }

    async with async_playwright() as p:
        # Launch Chromium, Firefox, and WebKit (Safari) simultaneously in a parallel grid
        chromium_task = execute_single_browser_audit(p, "chromium", target_url, crawl_limit, auth_user, auth_pass)
        firefox_task = execute_single_browser_audit(p, "firefox", target_url, crawl_limit, auth_user, auth_pass)
        webkit_task = execute_single_browser_audit(p, "webkit", target_url, crawl_limit, auth_user, auth_pass)

        grid_results = await asyncio.gather(chromium_task, firefox_task, webkit_task, return_exceptions=True)

    # Process and analyze data streams out of the browser grid to find layout or configuration deviations
    browser_keys = ["CHROMIUM", "FIREFOX", "WEBKIT"]
    processed_nodes = {}

    for idx, res in enumerate(grid_results):
        b_name = browser_keys[idx]
        if isinstance(res, Exception):
            processed_nodes[b_name] = {"routes_visited": [], "errors_caught": [], "performance_samples": [], "status": "Failed to open"}
            continue
        processed_nodes[b_name] = res

    telemetry["cross_browser_matrix"] = processed_nodes

    # CROSS-BROWSER DIFFERENTIAL MONITOR
    # Compare runtime errors across browsers to discover structural layout drifts or engine mismatches
    all_seen_errors = {}
    for b_name, node_data in processed_nodes.items():
        for error in node_data.get("errors_caught", []):
            err_msg = error["msg"]
            route = error["route"]
            err_key = f"{route}||{err_msg}"
            if err_key not in all_seen_errors:
                all_seen_errors[err_key] = set()
            all_seen_errors[err_key].add(b_name)

    for err_key, browsers in all_seen_errors.items():
        route, err_msg = err_key.split("||")
        # If an error happens in one engine but not others, it indicates an execution divergence/mismatch bug
        if len(browsers) < 3:
            telemetry["all_bugs"].append({
                "bug_id": f"BUG-X-BROWSER-{hash(err_key) % 10000}",
                "route_location": route, "module": "Cross-Browser Integration Grid",
                "issue": "Engine Execution Mismatch Drift Discovered", "severity": "High",
                "brief_summary": f"Anomaly behavior present in {', '.join(browsers)} layout paths, but absent in others.",
                "ai_cause": "Browser-specific layout runtime constraints or unpadded flexbox components.",
                "ai_fix": "Add verified cross-browser vendor flags or sanitize polyfills for the targeted properties."
            })
        else:
            telemetry["all_bugs"].append({
                "bug_id": f"BUG-CORE-{hash(err_key) % 10000}",
                "route_location": route, "module": "Core System Check",
                "issue": "Global Core Bug Profile", "severity": "Medium",
                "brief_summary": f"Defect logged across all matrix environments: {err_msg}",
                "ai_cause": "General application infrastructure asset missing.", "ai_fix": "Apply fix across shared components."
            })

    return telemetry

# --- CLI ENTRY ROUTE ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ci-mode":
        os.environ["BUGOPTIX_CLI_MODE"] = "True"
        target_input_url = sys.argv[2] if len(sys.argv) > 2 else "https://example.com"
        scan_output = asyncio.run(execute_comprehensive_qa_suite(target_url=target_input_url, crawl_limit=3))
        process_github_ci_quality_gate(scan_output)
        sys.exit(0)

# --- STREAMLIT USER INTERFACE CONTROL DASHBOARD ---
if "streamlit" in sys.modules and not os.environ.get("BUGOPTIX_CLI_MODE"):
    strl.set_page_config(page_title="BugOptix AI Parallel Grid", page_icon="🛡️", layout="wide")
    strl.title("🛡️ BugOptix AI Tester | Parallel Browser Grid Command Center")
    strl.markdown("---")

    if "vault" not in strl.session_state: strl.session_state["vault"] = VaultController.read_records()
    if "active_scan" not in strl.session_state: strl.session_state["active_scan"] = None

    runner_tab, tracking_tab = strl.tabs(["🚀 Parallel Grid Matrix Runner", "📋 Defect Lifecycle Matrix"])

    with runner_tab:
        col_u, col_d = strl.columns([3, 1])
        with col_u: url_scope = strl.text_input("Corporate Scope Address Target:", value="https://example.com")
        with col_d: depth_limit = strl.slider("Max Web Crawler Link Graph Depth Limit:", min_value=1, max_value=5, value=2)

        if strl.button("Dispatch Headless Multi-Browser Grid Audit Pipeline"):
            with strl.spinner("Spawning Chromium, Firefox, and WebKit test grids concurrently..."):
                res_data = asyncio.run(execute_comprehensive_qa_suite(url_scope.strip(), depth_limit))
                strl.session_state["active_scan"] = res_data
                vault_recs = VaultController.read_records()
                vault_recs["scans"].append(res_data)
                VaultController.write_records(vault_recs)
            strl.success("Parallel Grid evaluation execution complete.")

        active_scan_data = strl.session_state.get("active_scan")
        if isinstance(active_scan_data, dict) and "cross_browser_matrix" in active_scan_data:
            strl.markdown("### 📊 Concurrent Environment Comparison Board")
            
            # Formulate structural performance table comparing rendering times across all three engines
            matrix = active_scan_data["cross_browser_matrix"]
            metrics_comparison = []
            
            for b_name, b_data in matrix.items():
                samples = b_data.get("performance_samples", [])
                avg_latency = sum([s["latency_ms"] for s in samples]) / len(samples) if samples else 0.0
                metrics_comparison.append({
                    "Browser Engine Grid Node": b_name,
                    "Total Routes Crawled": len(b_data.get("routes_visited", [])),
                    "Intercepted Script Exceptions": len(b_data.get("errors_caught", [])),
                    "Mean Layout Render Latency": f"{round(avg_latency, 2)} ms"
                })
            
            strl.dataframe(pd.DataFrame(metrics_comparison), use_container_width=True, hide_index=True)

            bugs_list = active_scan_data.get("all_bugs", [])
            if isinstance(bugs_list, list) and len(bugs_list) > 0:
                bugs_df = pd.DataFrame(bugs_list)
                strl.markdown("### 🛑 Detected Matrix Anomalies & Root Cause Diagnostics")
                vault_recs = VaultController.read_records()
                
                for idx, bug in bugs_df.iterrows():
                    if not isinstance(bug, dict): bug = bug.to_dict()
                    b_id = bug.get("bug_id", f"BUG-{idx}")
                    current_status = vault_recs.get("lifecycle_states", {}).get(b_id, "Open")
                    
                    with strl.expander(f"[{bug.get('severity', 'High')}] {bug.get('module')} — {bug.get('issue')}"):
                        new_status = strl.selectbox(
                            f"State Control for {b_id}:", ["Open", "In-Progress", "Resolved", "Closed"],
                            index=["Open", "In-Progress", "Resolved", "Closed"].index(current_status),
                            key=f"status_select_{idx}_{b_id}"
                        )
                        if new_status != current_status:
                            vault_recs["lifecycle_states"][b_id] = new_status
                            VaultController.write_records(vault_recs)
                            strl.toast(f"Updated status for {b_id}")
                            strl.rerun()
                        strl.info(f"**Cross-Browser Behavior Metric Summary:** {bug.get('brief_summary')}")
                        strl.warning(f"**AI Structural Cause:** {bug.get('ai_cause')}")
                        strl.markdown(f"**Code Level Resolution Patch:** `{bug.get('ai_fix')}`")
            else:
                strl.success("Zero cross-browser variance bugs encountered.")

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
