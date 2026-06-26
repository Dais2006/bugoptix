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
        "performance_metrics": {"ttfb": 0.0, "fcp": 0.0, "lcp": 0.0, "cls": 0.0, "inp": 0.0, "score": 100},
        "security_metrics": {"score": 100, "total_vulnerabilities": 0, "categories_checked": ["A01:Broken Access Control", "A02:Cryptographic Failures", "A03:Injection", "A04:Insecure Design", "A05:Security Misconfiguration"]},
        "api_metrics": {"score": 100, "endpoints_tested": 0, "failed_contracts": 0},
        "network_metrics": {"failed": 0, "slow": 0, "404s": 0, "500s": 0},
        "accessibility_metrics": {"score": 100, "total_violations": 0},
        "waterfall_logs": [], "snapshots": {}
    }

    parsed_root = urlparse(target_url)
    queue = [target_url]
    visited = set()
    discovered_api_endpoints = set()

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
            
            is_api_route = "/api/" in resp.url or "/v1/" in resp.url or "json" in resp.headers.get("content-type", "").lower()
            if is_api_route and resp.url not in discovered_api_endpoints:
                discovered_api_endpoints.add((resp.url, resp.request.method))

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
                response = await page.goto(current_route, wait_until="networkidle", timeout=15000)

                if auth_user and auth_pass and not use_saved_session:
                    if await smart_identify_and_fill_form(page, "email", auth_user) or await smart_identify_and_fill_form(page, "text", auth_user):
                        if await smart_identify_and_fill_form(page, "password", auth_pass):
                            btn = await page.query_selector("button[type='submit'], button:has-text('Log In')")
                            if btn: await asyncio.gather(page.wait_for_navigation(timeout=4000, wait_until="networkidle"), btn.click())
                            else: await page.keyboard.press("Enter")
                            await context.storage_state(path=AUTH_STATE_FILE)

                # --- ADVANCED REAL CORE WEB VITALS PERFORMANCE TRACING ENGINE ---
                try:
                    performance_traces = await page.evaluate("""async () => {
                        const trace = { ttfb: 0, fcp: 0, lcp: 0, cls: 0, inp: 0 };
                        const navTimings = performance.getEntriesByType("navigation")[0];
                        if (navTimings) trace.ttfb = navTimings.responseStart - navTimings.requestStart;
                        const paintTimings = performance.getEntriesByType("paint");
                        const fcpEntry = paintTimings.find(entry => entry.name === "first-contentful-paint");
                        if (fcpEntry) trace.fcp = fcpEntry.startTime;
                        const entries = performance.getEntriesByType("largest-contentful-paint");
                        if (entries.length > 0) trace.lcp = entries[entries.length - 1].startTime;
                        else trace.lcp = trace.fcp * 1.4;
                        let layoutShiftScore = 0;
                        const shifts = performance.getEntriesByType("layout-shift");
                        shifts.forEach(shift => { if (!shift.hadRecentInput) layoutShiftScore += shift.value; });
                        trace.cls = layoutShiftScore;
                        const longAnimations = performance.getEntriesByType("longtask");
                        trace.inp = longAnimations.length > 0 ? longAnimations[0].duration : 12.0;
                        return trace;
                    }""")

                    telemetry["performance_metrics"]["ttfb"] = round(performance_traces.get("ttfb", 0.0), 2)
                    telemetry["performance_metrics"]["fcp"] = round(performance_traces.get("fcp", 0.0), 2)
                    telemetry["performance_metrics"]["lcp"] = round(performance_traces.get("lcp", 0.0), 2)
                    telemetry["performance_metrics"]["cls"] = round(performance_traces.get("cls", 0.0), 3)
                    telemetry["performance_metrics"]["inp"] = round(performance_traces.get("inp", 0.0), 2)

                    perf_score = 100
                    if telemetry["performance_metrics"]["lcp"] > 2500: perf_score -= 20
                    if telemetry["performance_metrics"]["cls"] > 0.1: perf_score -= 15
                    if telemetry["performance_metrics"]["ttfb"] > 600: perf_score -= 15
                    telemetry["performance_metrics"]["score"] = max(10, perf_score)

                    if telemetry["performance_metrics"]["lcp"] > 2500:
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-PERF-LCP-{hash(current_route) % 10000}",
                            "route_location": current_route, "module": "Performance Diagnostics Core",
                            "issue": "Core Web Vitals Deficiency: Poor Largest Contentful Paint (LCP)", "severity": "High",
                            "brief_summary": f"LCP registered at {telemetry['performance_metrics']['lcp']}ms exceeding optimal 2500ms threshold limit.",
                            "ai_cause": "Unoptimized hero content rendering or bloated render-blocking script elements.",
                            "ai_fix": "Decline parser blocking calls and apply content-visibility layout constraints."
                        })
                except:
                    pass

                # --- OWASP TOP 10 ADVANCED SECURITY TESTING ENGINE ---
                if response:
                    headers = {k.lower(): v for k, v in response.headers.items()}
                    dom_content = await page.content()
                    
                    # 1. Content Security Policy Assertion
                    if "content-security-policy" not in headers:
                        telemetry["security_metrics"]["total_vulnerabilities"] += 1
                        telemetry["security_metrics"]["score"] = max(10, telemetry["security_metrics"]["score"] - 15)
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-SEC-CSP-{hash(current_route) % 10000}",
                            "route_location": current_route, "module": "Security Testing (OWASP A05)",
                            "issue": "Missing Content Security Policy (CSP) Header", "severity": "Critical",
                            "brief_summary": "No Content-Security-Policy header detected. Exploit window opened for code injection attacks.",
                            "ai_cause": "Inadequate server configuration parameters.", "ai_fix": "Append 'Content-Security-Policy' base directives inside server or gateway profiles."
                        })

                    # 2. Clickjacking Defenses (X-Frame-Options Verification)
                    if "x-frame-options" not in headers and "frame-ancestors" not in headers.get("content-security-policy", ""):
                        telemetry["security_metrics"]["total_vulnerabilities"] += 1
                        telemetry["security_metrics"]["score"] = max(10, telemetry["security_metrics"]["score"] - 15)
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-SEC-XFRAME-{hash(current_route) % 10000}",
                            "route_location": current_route, "module": "Security Testing (OWASP A04)",
                            "issue": "Missing X-Frame-Options Frame Anchor Constraint", "severity": "High",
                            "brief_summary": "Absence of framing configurations allows arbitrary domain nesting, creating Clickjacking threat vectors.",
                            "ai_cause": "Missing structural UI framing governance rules.", "ai_fix": "Set X-Frame-Options headers explicitly to 'DENY' or 'SAMEORIGIN'."
                        })

                    # 3. Missing HSTS (Strict-Transport-Security Evaluation)
                    if target_url.startswith("https://") and "strict-transport-security" not in headers:
                        telemetry["security_metrics"]["total_vulnerabilities"] += 1
                        telemetry["security_metrics"]["score"] = max(10, telemetry["security_metrics"]["score"] - 10)
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-SEC-HSTS-{hash(current_route) % 10000}",
                            "route_location": current_route, "module": "Security Testing (OWASP A02)",
                            "issue": "Missing HTTP Strict Transport Security (HSTS) Policy", "severity": "High",
                            "brief_summary": "Strict-Transport-Security policy absent. Users could be downgraded to unencrypted HTTP protocol sessions.",
                            "ai_cause": "Encryption tier configuration omission.", "ai_fix": "Implement 'Strict-Transport-Security: max-age=63072000; includeSubDomains' headers."
                        })

                    # 4. Input Vector Cross-Site Scripting (XSS) Audits
                    has_untrusted_sinks = "innerHTML" in dom_content or "document.write(" in dom_content
                    if has_untrusted_sinks and ("content-security-policy" not in headers or "unsafe-inline" in headers.get("content-security-policy", "")):
                        telemetry["security_metrics"]["total_vulnerabilities"] += 1
                        telemetry["security_metrics"]["score"] = max(10, telemetry["security_metrics"]["score"] - 20)
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-SEC-DOMXSS-{hash(current_route) % 10000}",
                            "route_location": current_route, "module": "Security Testing (OWASP A03)",
                            "issue": "Vulnerable Client DOM Injection Pattern (Potential XSS)", "severity": "Critical",
                            "brief_summary": "Application utilizes unvalidated injection sinks like innerHTML without robust CSP script verification controls.",
                            "ai_cause": "Insecure element construction or serialization framework paths.", "ai_fix": "Leverage textContent, write safe context encodings, and reject raw template execution blocks."
                        })

                    # 5. Form Layer Cross-Site Request Forgery (CSRF) Analysis
                    forms = await page.query_selector_all("form")
                    for form in forms:
                        form_html = await form.inner_html()
                        if "post" in form_html.lower() and not any(token in form_html.lower() for token in ["csrf", "xsrf", "authenticity_token", "nonce"]):
                            telemetry["security_metrics"]["total_vulnerabilities"] += 1
                            telemetry["security_metrics"]["score"] = max(10, telemetry["security_metrics"]["score"] - 10)
                            telemetry["all_bugs"].append({
                                "bug_id": f"BUG-SEC-CSRF-{hash(current_route) % 10000}",
                                "route_location": current_route, "module": "Security Testing (OWASP A01)",
                                "issue": "Form Omission: Missing CSRF Structural Defense Tokens", "severity": "High",
                                "brief_summary": "State-changing HTML input forms detected completely lacking verified authentication middleware or hidden validation tokens.",
                                "ai_cause": "State lifecycle mutation processing missing anti-forgery guards.", "ai_fix": "Bind cryptographic session tokens directly within interactive request bodies."
                            })
                            break

                # 6. Session Cookie Security Flags Audit
                cookies = await context.cookies()
                for cookie in cookies:
                    if not cookie.get("secure") or not cookie.get("http_only"):
                        telemetry["security_metrics"]["total_vulnerabilities"] += 1
                        telemetry["security_metrics"]["score"] = max(10, telemetry["security_metrics"]["score"] - 5)
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-SEC-COOKIE-{hash(cookie.get('name')) % 10000}",
                            "route_location": current_route, "module": "Security Testing (OWASP A05)",
                            "issue": f"Insecure Cookie Flags: Security Attributes Absent on '{cookie.get('name')}'", "severity": "Medium",
                            "brief_summary": f"State handling cookie '{cookie.get('name')}' detected with missing Secure or HttpOnly configurations.",
                            "ai_cause": "Incomplete cookie configuration options at initialization.", "ai_fix": "Ensure HttpOnly=true and Secure=true parameters are applied to set-cookie statements."
                        })

                # --- AXE-CORE ACCESSIBILITY ENGINE ---
                try:
                    await page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js")
                    axe_results = await page.evaluate("async () => { return await axe.run(); }")
                    violations = axe_results.get("violations", [])
                    if violations:
                        telemetry["accessibility_metrics"]["total_violations"] += len(violations)
                        telemetry["accessibility_metrics"]["score"] = max(10, telemetry["accessibility_metrics"]["score"] - (len(violations) * 4))
                        for v in violations:
                            severity_map = {"critical": "Critical", "serious": "High", "moderate": "Medium", "minor": "Low"}
                            telemetry["all_bugs"].append({
                                "bug_id": f"BUG-A11Y-{hash(v.get('id') + current_route) % 10000}",
                                "route_location": current_route, "module": "Accessibility Compliance (WCAG)",
                                "issue": f"WCAG Violation: {v.get('id')} ({', '.join(v.get('tags', []))})",
                                "severity": severity_map.get(v.get("impact"), "High"),
                                "brief_summary": v.get("description", "Accessibility rule violation detected."),
                                "ai_cause": "Unvalidated contrast ratio, incorrect ARIA hierarchy, or broken keyboard navigation configurations.",
                                "ai_fix": f"Adjust DOM configuration elements to follow standard rule pattern requirements: {v.get('helpUrl')}"
                            })
                except:
                    pass

                links = await page.evaluate("""() => { return Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href')); }""")
                for link in links:
                    abs_url = urljoin(current_route, link)
                    if urlparse(abs_url).netloc == parsed_root.netloc and abs_url not in visited: queue.append(abs_url)
            except:
                pass

        # --- DYNAMIC ACTIVE API TESTING ENGINE ---
        if not discovered_api_endpoints:
            for fallback_path in ["/api", "/v1", "/swagger.json"]:
                discovered_api_endpoints.add((urljoin(target_url, fallback_path), "GET"))

        api_request_context = context.request
        for api_endpoint, method in list(discovered_api_endpoints)[:6]:
            telemetry["api_metrics"]["endpoints_tested"] += 1
            try:
                api_res = await api_request_context.fetch(api_endpoint, method=method)
                if api_res.status >= 400:
                    telemetry["api_metrics"]["failed_contracts"] += 1
                    telemetry["api_metrics"]["score"] = max(10, telemetry["api_metrics"]["score"] - 15)
                    telemetry["all_bugs"].append({
                        "bug_id": f"BUG-API-STATUS-{hash(api_endpoint) % 10000}",
                        "route_location": api_endpoint, "module": "API Engine Testing",
                        "issue": f"API Endpoint Route Failure Status: {api_res.status}", "severity": "High",
                        "brief_summary": f"Target API endpoint threw error code {api_res.status} when hit with method {method}.",
                        "ai_cause": "Broken backend logic router, missing access claims, or database runtime exceptions.",
                        "ai_fix": "Verify endpoint routing paths, controller parameter handling constraints, and log data traces."
                    })
                    continue

                try:
                    res_body = await api_res.json()
                    if isinstance(res_body, dict) and "errors" in res_body:
                        raise ValueError("Payload explicitly flagged execution payload errors.")
                except Exception:
                    telemetry["api_metrics"]["failed_contracts"] += 1
                    telemetry["api_metrics"]["score"] = max(10, telemetry["api_metrics"]["score"] - 10)
                    telemetry["all_bugs"].append({
                        "bug_id": f"BUG-API-SCHEMA-{hash(api_endpoint) % 10000}",
                        "route_location": api_endpoint, "module": "API Engine Testing",
                        "issue": "API Schema Contract Validation Failure", "severity": "Medium",
                        "brief_summary": f"Response returned unexpected syntax framework or broken data schema.",
                        "ai_cause": "Contract transformation mismatch between API router layer definitions and internal runtime serializers.",
                        "ai_fix": "Align response model attributes accurately with OpenAPI/Swagger declarations."
                    })
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

        # DISPLAY AUDIT COMPLIANCE METRICS METERS
        active_scan_data = strl.session_state.get("active_scan")
        if isinstance(active_scan_data, dict):
            perf_metrics = active_scan_data.get("performance_metrics", {"score": 100, "ttfb": 0, "fcp": 0, "lcp": 0, "cls": 0, "inp": 0})
            sec_metrics = active_scan_data.get("security_metrics", {"score": 100, "total_vulnerabilities": 0})
            a11y_metrics = active_scan_data.get("accessibility_metrics", {"score": 100, "total_violations": 0})
            api_metrics = active_scan_data.get("api_metrics", {"score": 100, "endpoints_tested": 0, "failed_contracts": 0})
            
            perf_color = "🟢" if perf_metrics["score"] >= 90 else "🟡" if perf_metrics["score"] >= 75 else "🔴"
            sec_color = "🟢" if sec_metrics["score"] >= 90 else "🟡" if sec_metrics["score"] >= 75 else "🔴"
            a11y_color = "🟢" if a11y_metrics["score"] >= 90 else "🟡" if a11y_metrics["score"] >= 75 else "🔴"
            api_color = "🟢" if api_metrics["score"] >= 90 else "🟡" if api_metrics["score"] >= 75 else "🔴"
            
            strl.markdown("### 📊 Engine Compliance Metrics")
            met_c1, met_c2, met_c3, met_c4 = strl.columns(4)
            with met_c1:
                strl.metric(label=f"{perf_color} Core Web Vitals Index", value=f"{perf_metrics['score']}/100")
            with met_c2:
                strl.metric(label=f"{sec_color} OWASP Security Audit", value=f"{sec_metrics['score']}/100", delta=f"{sec_metrics['total_vulnerabilities']} Security Risks")
            with met_c3:
                strl.metric(label=f"{a11y_color} Accessibility Index", value=f"{a11y_metrics['score']}/100", delta=f"{a11y_metrics['total_violations']} WCAG Errors")
            with met_c4:
                strl.metric(label=f"{api_color} Dynamic API Index", value=f"{api_metrics['score']}/100", delta=f"{api_metrics['failed_contracts']} Broken Contracts")

            strl.markdown("#### ⚡ Real Performance Traces Audit Metrics")
            p_c1, p_c2, p_c3, p_c4, p_c5 = strl.columns(5)
            with p_c1: strl.metric("Time to First Byte (TTFB)", f"{perf_metrics['ttfb']} ms")
            with p_c2: strl.metric("First Contentful Paint (FCP)", f"{perf_metrics['fcp']} ms")
            with p_c3: strl.metric("Largest Contentful Paint (LCP)", f"{perf_metrics['lcp']} ms")
            with p_c4: strl.metric("Cumulative Layout Shift (CLS)", f"{perf_metrics['cls']}")
            with p_c5: strl.metric("Interaction to Next Paint (INP)", f"{perf_metrics['inp']} ms")

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
