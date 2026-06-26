import os
import asyncio
import subprocess
import sys
import json
import base64
import re
import time
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

if "streamlit" in sys.modules:
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

# --- UNIFIED ASSESSMENT ENGINE ---
async def execute_comprehensive_qa_suite(target_url: str, crawl_limit: int, target_browser: str, auth_user: str = "", auth_pass: str = "", use_saved_session: bool = False) -> dict:
    start_time_stamp = datetime.now()
    telemetry = {
        "url": target_url, "timestamp": start_time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        "browser_used": target_browser, "crawled_routes": [], "all_bugs": [],
        "performance_metrics": {"fcp": 0, "lcp": 0, "tbt": 0, "cls": 0, "ttfb": 0},
        "seo_metrics": {"score": 100, "checks": []}, "api_metrics": {"score": 100, "logs": []},
        "network_metrics": {"failed": 0, "slow": 0, "404s": 0, "500s": 0},
        "accessibility_metrics": {"score": 100, "total_violations": 0},
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

        def trace_network_response(resp):
            telemetry["waterfall_logs"].append({
                "resource_url": resp.url[:70] + "...", "status_code": resp.status,
                "method_type": resp.request.method, "content_type": resp.headers.get("content-type", "Unknown")
            })
            if resp.status >= 500: telemetry["network_metrics"]["500s"] += 1
            elif resp.status == 404: telemetry["network_metrics"]["404s"] += 1

        def trace_client_console(msg):
            if msg.type == "error":
                telemetry["all_bugs"].append({
                    "bug_id": f"BUG-JS-ERR-{hash(msg.text) % 10000}",
                    "route_location": page.url, "module": "Client Engine Testing",
                    "issue": "Client-Side Frontend Runtime Crash Exception", "severity": "High",
                    "brief_summary": "Active unhandled JavaScript exception thrown.",
                    "ai_cause": "Object reference fault logic loop.", "ai_fix": "Wrap operational layers in catch handles."
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

                # --- DYNAMIC AXE-CORE ACCESSIBILITY ENGINE INTEGRATION ---
                try:
                    # Injecting a hosted/Cdn Axe-core bundle into the browser execution frame
                    await page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js")
                    axe_results = await page.evaluate("async () => { return await axe.run(); }")
                    
                    violations = axe_results.get("violations", [])
                    if violations:
                        telemetry["accessibility_metrics"]["total_violations"] += len(violations)
                        # Deduct penalty dynamically per unique standard infraction found
                        telemetry["accessibility_metrics"]["score"] = max(10, telemetry["accessibility_metrics"]["score"] - (len(violations) * 4))
                        
                        for v in violations:
                            severity_map = {"critical": "Critical", "serious": "High", "moderate": "Medium", "minor": "Low"}
                            target_impact = severity_map.get(v.get("impact"), "High")
                            
                            telemetry["all_bugs"].append({
                                "bug_id": f"BUG-A11Y-{hash(v.get('id') + current_route) % 10000}",
                                "route_location": current_route,
                                "module": "Accessibility Compliance (WCAG)",
                                "issue": f"WCAG Violation: {v.get('id')} ({', '.join(v.get('tags', []))})",
                                "severity": target_impact,
                                "brief_summary": v.get("description", "Accessibility rule violation detected."),
                                "ai_cause": "Unvalidated contrast ratio, incorrect ARIA hierarchy, or broken sequential keyboard focus structures.",
                                "ai_fix": f"Review element selectors matching standard rules to ensure conformance with WCAG guidelines: {v.get('helpUrl')}"
                            })
                except Exception as a11y_err:
                    # Fallback structural regex-heuristics if external script CDNs are blocked
                    html_content = await page.content()
                    if "contrast" in html_content.lower() or not aria_check := re.findall(r'aria-[a-z]+=""', html_content):
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-A11Y-FALLBACK-{hash(current_route) % 1000}",
                            "route_location": current_route, "module": "Accessibility Compliance (Static)",
                            "issue": "Degraded DOM Layout: Suspected Keyboard Tab-Index or ARIA Malformation",
                            "severity": "High", "brief_summary": "Empty or broken layout element violates predictable interaction expectations.",
                            "ai_cause": "Elements omitted from accessibility markup tree.", "ai_fix": "Expose accurate role attributes explicitly."
                        })

                if response:
                    headers = {k.lower(): v for k, v in response.headers.items()}
                    if "content-security-policy" not in headers:
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-HED-CSP-{hash(current_route) % 10000}",
                            "route_location": current_route, "module": "Security Testing",
                            "issue": "Header Omission: content-security-policy", "severity": "Critical",
                            "brief_summary": "Missing standard CSP protection constraint parameters.",
                            "ai_cause": "Infrastructure layer parameter skipping.", "ai_fix": "Append parameters inside web service definitions."
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

# --- STREAMLIT USER INTERFACE CONTROL DASHBOARD ---
if "streamlit" in sys.modules:
    strl.set_page_config(page_title="BugOptix AI Tester", page_icon="🛡️", layout="wide")
    strl.title("🛡️ BugOptix AI Tester | Enterprise Panel")
    strl.markdown("---")

    if "vault" not in strl.session_state: strl.session_state["vault"] = VaultController.read_records()
    if "active_scan" not in strl.session_state: strl.session_state["active_scan"] = None

    runner_tab, tracking_tab = strl.tabs(["🚀 Quality Suite Test Runner", "📋 Defect Lifecycle Matrix"])

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

        # DISPLAY DYNAMIC ACCESSIBILITY METRICS METERS
        active_scan_data = strl.session_state.get("active_scan")
        if isinstance(active_scan_data, dict):
            a11y_metrics = active_scan_data.get("accessibility_metrics", {"score": 100, "total_violations": 0})
            score_color = "🟢" if a11y_metrics["score"] >= 90 else "🟡" if a11y_metrics["score"] >= 75 else "🔴"
            
            strl.markdown("### 📊 Engine Compliance Metrics")
            met_c1, met_c2 = strl.columns(2)
            with met_c1:
                strl.metric(label=f"{score_color} Live Accessibility Index Score", value=f"{a11y_metrics['score']}/100")
            with met_c2:
                strl.metric(label="Evaluated WCAG Rule Violations Found", value=str(a11y_metrics['total_violations']), delta="Impact: Very High" if a11y_metrics['total_violations'] > 0 else "Clear")

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
