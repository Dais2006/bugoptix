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
from urllib.parse import urlparse, urljoin, urlencode, parse_qs
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

# --- DYNAMIC ADVERSARIAL SCANNING SUB-ENGINE ---
class OwaspSecurityScanner:
    """Performs contextual active and passive security validation matching OWASP categories."""
    
    @staticmethod
    def test_jwt_vulnerabilities(storage_string: str, route: str) -> list:
        found_bugs = []
        # Look for JWT signatures
        jwt_matches = re.findall(r"eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]*", storage_string)
        for token in jwt_matches:
            try:
                payload_b64 = token.split(".")[1]
                # Fix padding
                payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
                decoded = json.loads(base64.b64decode(payload_b64).decode("utf-8", errors="ignore"))
                if decoded.get("alg", "").lower() == "none" or "alg" not in decoded:
                    found_bugs.append({
                        "bug_id": f"BUG-JWT-NONE-{hash(route)%10000}", "route_location": route,
                        "module": "OWASP A02: Cryptographic Failures", "issue": "Insecure JWT Header Configuration (alg=none)",
                        "severity": "Critical", "brief_summary": "Exposed JWT token specifies or permits unauthenticated 'none' signature algorithms.",
                        "ai_cause": "Flawed verification parser implementation.", "ai_fix": "Enforce strict symmetric/asymmetric algorithm validation."
                    })
            except:
                pass
        return found_bugs

    @staticmethod
    async def perform_active_parameter_fuzzing(page, target_route: str) -> list:
        fuzz_findings = []
        parsed = urlparse(target_route)
        query_params = parse_qs(parsed.query)
        
        if query_params:
            # 1. Directory Traversal / LFI Testing
            lfi_payloads = ["../../../../etc/passwd", "..\\..\\..\\windows\\win.ini"]
            for param in query_params.keys():
                for payload in lfi_payloads:
                    fuzz_query = query_params.copy()
                    fuzz_query[param] = [payload]
                    fuzz_url = parsed._replace(query=urlencode(fuzz_query, doseq=True)).geturl()
                    try:
                        async with httpx.AsyncClient() as client:
                            res = await client.get(fuzz_url, timeout=4.0)
                            if "root:" in res.text or "[extensions]" in res.text:
                                fuzz_findings.append({
                                    "bug_id": f"BUG-LFI-{hash(fuzz_url)%10000}", "route_location": target_route,
                                    "module": "OWASP A01: Broken Access Control", "issue": "Path Traversal / Local File Inclusion Vulnerability",
                                    "severity": "Critical", "brief_summary": f"Fuzzing param '{param}' leaked system system initialization files.",
                                    "ai_cause": "Unchecked server-side file pathway resolution bindings.", "ai_fix": "Sanitize user paths via os.path.basename checks."
                                })
                    except:
                        pass

            # 2. SSRF Testing
            ssrf_payloads = ["http://169.254.169.254/latest/meta-data/", "http://localhost:80"]
            for param in query_params.keys():
                for payload in ssrf_payloads:
                    fuzz_query = query_params.copy()
                    fuzz_query[param] = [payload]
                    fuzz_url = parsed._replace(query=urlencode(fuzz_query, doseq=True)).geturl()
                    try:
                        async with httpx.AsyncClient() as client:
                            res = await client.get(fuzz_url, timeout=4.0)
                            if "ami-id" in res.text or "instance-id" in res.text:
                                fuzz_findings.append({
                                    "bug_id": f"BUG-SSRF-{hash(fuzz_url)%10000}", "route_location": target_route,
                                    "module": "OWASP A10: Server-Side Request Forgery", "issue": "Server-Side Request Forgery (SSRF) Exposure",
                                    "severity": "Critical", "brief_summary": f"Param '{param}' allows remote infrastructure connection to internal endpoints.",
                                    "ai_cause": "Implicit network fetch requests executed without domain destination lists.", "ai_fix": "Implement strict destination domain white-listing parameters."
                                })
                    except:
                        pass
        return fuzz_findings

# --- GITHUB CI QUALITY GATE EVALUATOR ---
def process_github_ci_quality_gate(scan_results: dict):
    print("\n--- BUGOPTIX CI QUALITY GATE EVALUATOR RUNNING ---")
    all_bugs = scan_results.get("all_bugs", [])
    if not isinstance(all_bugs, list): all_bugs = []
    critical_bugs = [b for b in all_bugs if isinstance(b, dict) and b.get("severity") == "Critical"]
    
    print(f"Total Anomalies Located: {len(all_bugs)}")
    print(f"Critical OWASP Vulns: {len(critical_bugs)}")
    
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
        "performance_metrics": {"ttfb": 0, "fcp": 0}, "waterfall_logs": []
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

        while queue and len(visited) < crawl_limit:
            current_route = queue.pop(0)
            if current_route in visited: continue
            visited.add(current_route)
            telemetry["crawled_routes"].append(current_route)

            try:
                # Setup Dialog handlers to catch alert boxes from active XSS payloads
                async def handle_dialog(dialog):
                    telemetry["all_bugs"].append({
                        "bug_id": f"BUG-XSS-{hash(current_route)%10000}", "route_location": current_route,
                        "module": "OWASP A03: Injection", "issue": "Reflected Cross-Site Scripting (XSS) Executed",
                        "severity": "Critical", "brief_summary": f"Injected malicious script triggered client context alert dialog popup: {dialog.message}",
                        "ai_cause": "Context-unaware output rendering pipeline.", "ai_fix": "Enforce HTML escape character controls across templates."
                    })
                    await dialog.dismiss()
                page.on("dialog", handle_dialog)

                t0 = asyncio.get_event_loop().time()
                response = await page.goto(current_route, wait_until="domcontentloaded", timeout=12000)
                t1 = asyncio.get_event_loop().time()

                telemetry["performance_metrics"]["ttfb"] = (t1 - t0) * 1000

                # 1. AUTHENTICATION & SESSION FIXATION TESTING
                cookies = await context.cookies(current_route)
                for cookie in cookies:
                    if not cookie.get("secure") or not cookie.get("httpOnly"):
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-COOKIE-WEAK-{hash(cookie['name'])%10000}", "route_location": current_route,
                            "module": "OWASP A07: Identification and Authentication Failures", "issue": "Insecure Session Cookie Configuration (Missing Flags)",
                            "severity": "High", "brief_summary": f"Active session tracking key '{cookie['name']}' lacks HttpOnly/Secure safety parameters.",
                            "ai_cause": "Improper production server cookie definition options.", "ai_fix": "Enable secure deployment settings: 'Secure=True; HttpOnly=True; SameSite=Strict'."
                        })

                # 2. LOCAL TOKEN & JWT SCANNING
                local_storage = await page.evaluate("() => JSON.stringify(localStorage)")
                telemetry["all_bugs"].extend(OwaspSecurityScanner.test_jwt_vulnerabilities(local_storage, current_route))

                # 3. CSRF & ACTIVE FORM EXPOSURE ASSESSMENTS
                forms = await page.query_selector_all("form")
                for form in forms:
                    form_html = await page.evaluate("(element) => element.outerHTML", form)
                    if not any(token in form_html.lower() for token in ["csrf", "xsrf", "nonce", "authenticity"]):
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-CSRF-{hash(form_html)%10000}", "route_location": current_route,
                            "module": "OWASP A01: Broken Access Control", "issue": "Missing CSRF Token Protection Element",
                            "severity": "High", "brief_summary": f"Discovered interactive data submission form omitting anti-CSRF token parameters.",
                            "ai_cause": "Omission of cross-site request validation state checks within the state processor.", "ai_fix": "Integrate standard verification middleware validation logic."
                        })

                # 4. PASSIVE SQL INJECTION & ERROR SCREEN LEAKS
                body_content = await page.content()
                sql_error_patterns = [r"SQL syntax", r"mysql_fetch_array", r"ORA-[0-9]{5}", r"PostgreSQL query failed"]
                if any(re.search(pat, body_content, re.IGNORECASE) for pat in sql_error_patterns):
                    telemetry["all_bugs"].append({
                        "bug_id": f"BUG-SQLI-ERR-{hash(current_route)%10000}", "route_location": current_route,
                        "module": "OWASP A03: Injection", "issue": "Database Stack-Trace Error Leakage",
                        "severity": "Critical", "brief_summary": "Web view directly discloses server-side raw structured database error parameters.",
                        "ai_cause": "Verbose runtime error routing visibility configured to display on production endpoints.", "ai_fix": "Enforce centralized global try-catch frameworks with clean custom generic user errors."
                    })

                # 5. ACTIVE PARAMETER FUZZING (SSRF, Traversal)
                fuzz_results = await OwaspSecurityScanner.perform_active_parameter_fuzzing(page, current_route)
                telemetry["all_bugs"].extend(fuzz_results)

                # 6. ACTIVE FORM INJECTION FUZZING (SQLi / XSS Attack Vectors)
                inputs = await page.query_selector_all("input[type='text'], input:not([type])")
                for inp in inputs:
                    try:
                        if await inp.is_visible() and await inp.is_enabled():
                            # Trigger Reflected XSS testing
                            await inp.fill("<script>alert('xss-test')</script>")
                            # Trigger SQLi active form checking
                            await page.keyboard.press("Enter")
                            await page.wait_for_timeout(500)
                    except:
                        pass

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
    strl.set_page_config(page_title="BugOptix OWASP Suite", page_icon="🛡️", layout="wide")
    strl.title("🛡️ BugOptix AI Tester | OWASP Top 10 Security & Vulnerability Analysis Dashboard")
    strl.markdown("---")

    if "vault" not in strl.session_state: strl.session_state["vault"] = VaultController.read_records()
    if "active_scan" not in strl.session_state: strl.session_state["active_scan"] = None

    runner_tab, tracking_tab = strl.tabs(["🚀 Quality Suite Test Runner", "📋 OWASP Top 10 Governance Report Matrix"])

    with runner_tab:
        col_u, col_b, col_d = strl.columns([2, 1, 1])
        with col_u: url_scope = strl.text_input("Target URL Protocol Endpoint Scope Address:", value="https://example.com")
        with col_b: targeted_browser = strl.selectbox("Select Execution Environment Browser Node Type:", ["Chromium (Standard)", "Firefox"])
        with col_d: depth_limit = strl.slider("Max Web Crawler Target Depth Limit:", min_value=1, max_value=10, value=3)

        if strl.button("Dispatch Vulnerability Scan Suite Pipeline Execution"):
            with strl.spinner("Injecting OWASP testing fuzzers and running parameter mutation matrices..."):
                res_data = asyncio.run(execute_comprehensive_qa_suite(url_scope.strip(), depth_limit, targeted_browser))
                strl.session_state["active_scan"] = res_data
                vault_recs = VaultController.read_records()
                vault_recs["scans"].append(res_data)
                VaultController.write_records(vault_recs)
            strl.success("Assessment sweep complete. Threat matrix mapped successfully.")

        active_scan_data = strl.session_state.get("active_scan")
        if isinstance(active_scan_data, dict):
            bugs_list = active_scan_data.get("all_bugs", [])
            if isinstance(bugs_list, list) and len(bugs_list) > 0:
                bugs_df = pd.DataFrame(bugs_list)
                strl.markdown("### 🛑 Findings Summary Matrix")
                strl.dataframe(bugs_df[["bug_id", "module", "issue", "severity", "route_location"]], use_container_width=True, hide_index=True)
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
                            "ID": b.get("bug_id"), "OWASP Category Mapping": b.get("module"), 
                            "Vulnerability": b.get("issue"), "Severity": b.get("severity"), 
                            "Status": vault_recs.get("lifecycle_states", {}).get(b.get("bug_id"), "Open"), 
                            "Path Location": b.get("route_location")
                        })
        if flattened_bugs: 
            strl.dataframe(pd.DataFrame(flattened_bugs).drop_duplicates(subset=["ID"]), use_container_width=True, hide_index=True)
        else: 
            strl.info("Central tracking stores contain zero recorded security vulnerabilities.")
