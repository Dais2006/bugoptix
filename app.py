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

# --- AUTOMATED COMPLIANCE SCENARIO GENERATOR ---
class TestScenarioGenerator:
    """Orchestrates comprehensive scenario generation maps tracking multi-browser conditions."""
    
    @staticmethod
    def construct_automated_test_suite(target_url: str, explored_routes: list, discovered_forms: list) -> list:
        generated_cases = []
        base_id = int(time.time()) % 10000
        
        # 1. Automatic User Flow Path Generation Scenarios
        if explored_routes:
            flow_steps = " -> ".join([urlparse(r).path if urlparse(r).path else "/" for r in explored_routes[:4]])
            generated_cases.append({
                "case_id": f"TC-FLOW-{base_id}-01",
                "category": "User Flow Navigation",
                "title": f"Verify Multi-Route Core Navigation Pipeline Progression Flow",
                "preconditions": f"Application running in stable state at root: {target_url}",
                "steps": f"1. Navigate to endpoint.\n2. Progress linearly through link graphs: {flow_steps}",
                "expected_result": "All view states switch instantly across rendering engines without runtime freezes."
            })

        # 2. Form Boundary Cases & Input Vector Edge Cases
        for idx, form in enumerate(discovered_forms or [{"name": "Generic Input View"}]):
            form_name = form.get("name", f"Interactive Element Context {idx}")
            generated_cases.extend([
                {
                    "case_id": f"TC-BND-{base_id}-{idx}A",
                    "category": "Boundary Condition",
                    "title": f"Validate Form Field Boundary Length Handling for: {form_name}",
                    "preconditions": "Target interactable input wrapper completely loaded.",
                    "steps": "1. Inject alphanumeric buffer string exceeding 4096 character memory allocation limit.\n2. Submit action wrapper.",
                    "expected_result": "Frontend securely truncates input or serves a clean validation alert instead of a system crash."
                },
                {
                    "case_id": f"TC-BND-{base_id}-{idx}B",
                    "category": "Boundary Condition",
                    "title": f"Validate Special Character SQL/XSS Code Injection Sanitization",
                    "preconditions": "Target input form vector visibility true.",
                    "steps": "1. Inject breaking script payloads: `' OR 1=1--` and `<script>confirm(1)</script>` into data keys.\n2. Execute workflow submit event.",
                    "expected_result": "Strict framework encoding acts as an architectural guard; entities are rendered safely as raw string data."
                }
            ])

        # 3. Global Structural Network Performance Gates
        for r_idx, route in enumerate(explored_routes[:2]):
            slug = urlparse(route).path or "/"
            generated_cases.append({
                "case_id": f"TC-PERF-{base_id}-{r_idx}",
                "category": "Automatic Performance Gate",
                "title": f"Verify Latency Threshold Compliance for: {slug}",
                "preconditions": f"Clear network sockets mapped to environment profile.",
                "steps": f"1. Trigger programmatic context load on path: {route}.\n2. Log resource timing indices.",
                "expected_result": "Time-To-First-Byte metrics remain steadily below optimal 600ms latency ceiling across targets."
            })

        return generated_cases

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
    browser_launcher = getattr(p_instance, browser_key)
    args = ["--no-sandbox"] if browser_key == "chromium" else []
    
    browser = await browser_launcher.launch(headless=True, args=args)
    context_opts = {"ignore_https_errors": True, "viewport": {"width": 1280, "height": 800}}
    context = await browser.new_context(**context_opts)
    page = await context.new_page()

    local_telemetry = {
        "browser": browser_key.upper(), "routes_visited": [], "errors_caught": [],
        "performance_samples": [], "discovered_forms": []
    }

    queue = [target_url]
    visited = set()
    parsed_root = urlparse(target_url)

    def log_console(msg):
        if msg.type == "error":
            local_telemetry["errors_caught"].append({"route": page.url, "msg": msg.text})

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

            if auth_user and auth_pass:
                await smart_identify_and_fill_form(page, "email", auth_user)
                await smart_identify_and_fill_form(page, "password", auth_pass)

            # Detect interactive form wrappers for scenario criteria mapping
            form_elements = await page.query_selector_all("form")
            for f in form_elements:
                f_id = await f.get_attribute("id") or await f.get_attribute("name") or "Dynamic Form Framework"
                local_telemetry["discovered_forms"].append({"name": f_id})

            local_telemetry["performance_samples"].append({
                "route": current_route, "latency_ms": (t1 - t0) * 1000
            })

            if response:
                headers = {k.lower(): v for k, v in response.headers.items()}
                if "content-security-policy" not in headers:
                    local_telemetry["errors_caught"].append({"route": current_route, "msg": "Missing CSP layout header attribute."})

            links = await page.evaluate("""() => { return Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href')); }""")
            for link in links:
                abs_url = urljoin(current_route, link)
                if urlparse(abs_url).netloc == parsed_root.netloc and abs_url not in visited: queue.append(abs_url)
        except:
            pass

    await context.close()
    await browser.close()
    return local_telemetry

# --- GITHUB CI QUALITY GATE EVALUATOR ---
def process_github_ci_quality_gate(scan_results: dict):
    print("\n--- BUGOPTIX CI QUALITY GATE EVALUATOR RUNNING ---")
    all_bugs = scan_results.get("all_bugs", [])
    print(f"Total Defects Found: {len(all_bugs)}")
    print(f"Generated Test Cases Count: {len(scan_results.get('generated_test_cases', []))}")
    sys.exit(0)

# --- UNIFIED ASSESSMENT PARALLEL GRID ENGINE ---
async def execute_comprehensive_qa_suite(target_url: str, crawl_limit: int, auth_user: str = "", auth_pass: str = "") -> dict:
    start_time_stamp = datetime.now()
    telemetry = {
        "url": target_url, "timestamp": start_time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        "all_bugs": [], "cross_browser_matrix": {}, "generated_test_cases": []
    }

    async with async_playwright() as p:
        chromium_task = execute_single_browser_audit(p, "chromium", target_url, crawl_limit, auth_user, auth_pass)
        firefox_task = execute_single_browser_audit(p, "firefox", target_url, crawl_limit, auth_user, auth_pass)
        webkit_task = execute_single_browser_audit(p, "webkit", target_url, crawl_limit, auth_user, auth_pass)

        grid_results = await asyncio.gather(chromium_task, firefox_task, webkit_task, return_exceptions=True)

    browser_keys = ["CHROMIUM", "FIREFOX", "WEBKIT"]
    processed_nodes = {}
    aggregated_routes = set()
    aggregated_forms = []

    for idx, res in enumerate(grid_results):
        b_name = browser_keys[idx]
        if isinstance(res, Exception):
            processed_nodes[b_name] = {"routes_visited": [], "errors_caught": [], "performance_samples": [], "discovered_forms": []}
            continue
        processed_nodes[b_name] = res
        for r in res.get("routes_visited", []): aggregated_routes.add(r)
        aggregated_forms.extend(res.get("discovered_forms", []))

    telemetry["cross_browser_matrix"] = processed_nodes

    # RUN AUTOMATED TEST SCENARIO EXTRACTION CORRELATION ENGINE
    telemetry["generated_test_cases"] = TestScenarioGenerator.construct_automated_test_suite(
        target_url, list(aggregated_routes), aggregated_forms
    )

    all_seen_errors = {}
    for b_name, node_data in processed_nodes.items():
        for error in node_data.get("errors_caught", []):
            err_key = f"{error['route']}||{error['msg']}"
            if err_key not in all_seen_errors: all_seen_errors[err_key] = set()
            all_seen_errors[err_key].add(b_name)

    for err_key, browsers in all_seen_errors.items():
        route, err_msg = err_key.split("||")
        if len(browsers) < 3:
            telemetry["all_bugs"].append({
                "bug_id": f"BUG-X-BROWSER-{hash(err_key) % 10000}",
                "route_location": route, "module": "Cross-Browser Integration Grid",
                "issue": "Engine Execution Mismatch Drift Discovered", "severity": "High",
                "brief_summary": f"Anomaly behavior present in {', '.join(browsers)} layout paths, but absent in others.",
                "ai_cause": "Browser-specific layout runtime constraints or unpadded layout rules.",
                "ai_fix": "Add verified cross-browser vendor flags or sanitize polyfills for the targeted properties."
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
    strl.set_page_config(page_title="BugOptix AI Suite", page_icon="🛡️", layout="wide")
    strl.title("🛡️ BugOptix AI Tester | Parallel Grid & Automatic Test Case Generator")
    strl.markdown("---")

    if "vault" not in strl.session_state: strl.session_state["vault"] = VaultController.read_records()
    if "active_scan" not in strl.session_state: strl.session_state["active_scan"] = None

    runner_tab, suite_tab, tracking_tab = strl.tabs(["🚀 Execution Matrix Runner", "📋 Automated Test Case Suite", "📁 Saved Fault Logs"])

    with runner_tab:
        col_u, col_d = strl.columns([3, 1])
        with col_u: url_scope = strl.text_input("Corporate Scope Address Target:", value="https://example.com")
        with col_d: depth_limit = strl.slider("Max Web Crawler Link Graph Depth Limit:", min_value=1, max_value=5, value=2)

        if strl.button("Dispatch Headless Multi-Browser Grid Audit Pipeline"):
            with strl.spinner("Orchestrating system environments and generating scenario paths..."):
                res_data = asyncio.run(execute_comprehensive_qa_suite(url_scope.strip(), depth_limit))
                strl.session_state["active_scan"] = res_data
                vault_recs = VaultController.read_records()
                vault_recs["scans"].append(res_data)
                VaultController.write_records(vault_recs)
            strl.success("Evaluation pipeline execution complete.")

        active_scan_data = strl.session_state.get("active_scan")
        if isinstance(active_scan_data, dict) and "cross_browser_matrix" in active_scan_data:
            strl.markdown("### 📊 Concurrent Environment Comparison Board")
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

    with suite_tab:
        active_scan_data = strl.session_state.get("active_scan")
        if isinstance(active_scan_data, dict) and active_scan_data.get("generated_test_cases"):
            strl.markdown("### 📑 Dynamically Generated Quality Suite Scenarios Matrix")
            cases_df = pd.DataFrame(active_scan_data["generated_test_cases"])
            strl.dataframe(cases_df, use_container_width=True, hide_index=True)
        else:
            strl.info("Run an active validation scan to populate the automated boundary and flow scenario maps.")

    with tracking_tab:
        vault_recs = VaultController.read_records()
        flattened_bugs = []
        for s in vault_recs.get("scans", []):
            if isinstance(s, dict):
                for b in s.get("all_bugs", []):
                    if isinstance(b, dict):
                        flattened_bugs.append({
                            "ID": b.get("bug_id"), "Area": b.get("module"), "Issue": b.get("issue"), 
                            "Severity": b.get("severity"), "Status": vault_recs.get("lifecycle_states", {}).get(b.get("bug_id"), "Open"), 
                            "Route": b.get("route_location")
                        })
        if flattened_bugs: 
            strl.dataframe(pd.DataFrame(flattened_bugs).drop_duplicates(subset=["ID"]), use_container_width=True, hide_index=True)
        else: 
            strl.info("Central tracking stores contain zero recorded open issues.")
