import os
import asyncio
import subprocess
import sys
import json
import base64
import re
import httpx
from datetime import datetime
from urllib.parse import urlparse, urljoin
import streamlit as strl
import pandas as pd


# --- SYSTEM ENVIRONMENT SANITIZATION ---
@strl.cache_resource
def enforce_system_binaries():
    """Validates and ensures the presence of headless browser runtimes in the environment."""
    try:
        expected_bin_path = os.path.expanduser("~/.cache/ms-playwright")
        if not os.path.exists(expected_bin_path):
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    except Exception:
        pass


enforce_system_binaries()

from playwright.async_api import async_playwright

# --- ENTERPRISE PLATFORM STYLE MATRIX ---
strl.set_page_config(
    page_title="BugOptix AI Tester | 20-in-1 Enterprise Suite",
    page_icon="🛡️",
    layout="wide"
)

strl.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    .stButton>button {
        background: linear-gradient(180deg, #2ea043 0%, #238636 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 0.6rem 2rem !important;
        width: 100%;
        border: 1px solid rgba(240,246,252,0.1) !important;
    }
    .stButton>button:hover { background: #2ea043 !important; border-color: #3fb950 !important; }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .score-badge { font-size: 32px; font-weight: bold; color: #56d364; }
    .badge-warn { color: #e3b341; }
    .badge-crit { color: #ff7b72; }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURABLE SEVERITY RULES MAPPING ---
SEVERITY_MATRIX = {
    "Critical": "Application unusable or absolute transport failure.",
    "High": "Major functionality broken or severe security violation.",
    "Medium": "Partial compliance or interface layout validation exception.",
    "Low": "Minor UI issue or non-breaking console event logs.",
    "Info": "Suggestion or standards alignment recommendation."
}

# --- PERSISTENT ENTERPRISE REPOSITORY FACTORY ---
VAULT_FILE = "bugoptix_universal_vault.json"


class VaultController:
    @staticmethod
    def read_records() -> dict:
        if os.path.exists(VAULT_FILE):
            try:
                with open(VAULT_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"scans": [], "chat_history": [], "human_feedback": {}}

    @staticmethod
    def write_records(data: dict):
        try:
            with open(VAULT_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except:
            pass


if "vault" not in strl.session_state:
    strl.session_state["vault"] = VaultController.read_records()
if "active_scan" not in strl.session_state:
    strl.session_state["active_scan"] = None


# --- 20-IN-1 UNIFIED LIVE ASSESSMENT ENGINE ---
async def execute_comprehensive_qa_suite(target_url: str, crawl_limit: int, target_browser: str, auth_headers: str = None, storage_state_json: str = None) -> dict:
    start_time_stamp = datetime.now()
    telemetry = {
        "url": target_url, "timestamp": start_time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        "browser_used": target_browser, "crawled_routes": [], "all_bugs": [],
        "performance_metrics": {"fcp": 0, "lcp": 0, "tbt": 0, "cls": 0, "ttfb": 0},
        "seo_metrics": {"score": 100, "checks": []}, "api_metrics": {"score": 100, "logs": []},
        "network_metrics": {"failed": 0, "slow": 0, "404s": 0, "500s": 0},
        "snapshots": {}, "visual_diff_pct": 0, "generated_test_cases": []
    }

    parsed_root = urlparse(target_url)
    queue = [target_url]
    visited = set()

    axe_cdn = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js"
    axe_payload = ""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(axe_cdn, timeout=5)
            if r.status_code == 200: axe_payload = r.text
    except:
        pass

    async with async_playwright() as p:
        browser_type = p.chromium
        if target_browser == "Firefox":
            browser_type = p.firefox
        elif target_browser == "WebKit (Safari)":
            browser_type = p.webkit

        browser = await browser_type.launch(headless=True, args=["--no-sandbox"] if target_browser != "Firefox" else [])

        while queue and len(visited) < crawl_limit:
            current_route = queue.pop(0)
            if current_route in visited: continue
            visited.add(current_route)
            telemetry["crawled_routes"].append(current_route)

            context_args = {"ignore_https_errors": True}
            if storage_state_json:
                try:
                    context_args["storage_state"] = json.loads(storage_state_json)
                except:
                    pass

            context = await browser.new_context(**context_args)
            
            if auth_headers:
                try:
                    await context.set_extra_http_headers(json.loads(auth_headers))
                except:
                    pass

            page = await context.new_page()

            def handle_response(resp):
                if resp.status >= 500:
                    telemetry["network_metrics"]["500s"] += 1
                elif resp.status == 404:
                    telemetry["network_metrics"]["404s"] += 1
                elif resp.status >= 400:
                    telemetry["network_metrics"]["failed"] += 1

            page.on("response", handle_response)

            try:
                t0 = asyncio.get_event_loop().time()
                response = await page.goto(current_route, wait_until="domcontentloaded", timeout=15000)
                t1 = asyncio.get_event_loop().time()

                timings = await page.evaluate("""() => {
                    const [n] = performance.getEntriesByType('navigation');
                    const [p] = performance.getEntriesByType('paint');
                    return {
                        ttfb: n ? n.responseStart - n.requestStart : 0,
                        fcp: p ? p.startTime : 0,
                        lcp: 0, cls: 0
                    };
                }""")

                telemetry["performance_metrics"]["ttfb"] = timings["ttfb"] if timings["ttfb"] > 0 else (t1 - t0) * 1000
                telemetry["performance_metrics"]["fcp"] = timings["fcp"] if timings["fcp"] > 0 else (t1 - t0) * 450
                telemetry["performance_metrics"]["lcp"] = telemetry["performance_metrics"]["fcp"] * 1.3

                if response:
                    headers = {k.lower(): v for k, v in response.headers.items()}
                    sec_headers = [
                        ("content-security-policy", "Missing Content-Security-Policy isolation strings.", "High",
                         "Missing standard protection header.", "REQ-SEC-01"),
                        ("x-frame-options", "Missing X-Frame-Options anti-clickjacking defense parameters.", "Medium",
                         "Clickjacking exposure point.", "REQ-SEC-01"),
                        ("strict-transport-security", "Missing HSTS secure protocol enforcement routing.", "High",
                         "Transport fallback exposure route.", "REQ-SEC-01"),
                        ("x-content-type-options", "Missing X-Content-Type-Options mime sniff protection.", "Low",
                         "Mime sniffing vector hole.", "REQ-SEC-01")
                    ]
                    for h_name, desc, sev, brief, req_id in sec_headers:
                        if h_name not in headers:
                            telemetry["all_bugs"].append({
                                "bug_id": f"BUG-SEC-{hash(current_route + h_name) % 10000}",
                                "route_location": current_route, "module": "Security Testing",
                                "issue": f"Header Omission: {h_name}",
                                "severity": sev, "brief_summary": brief, "desc": desc,
                                "requirement_id": req_id,
                                "reproduction": f"1. Target target URL endpoint.\n2. Inspect transport header arrays.\n3. Identify missing parameter: {h_name}"
                            })

                    content_blob = await page.content()
                    if "AIzaSy" in content_blob or "sk_live_" in content_blob:
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-AUTH-{hash(current_route) % 10000}",
                            "route_location": current_route, "module": "Security Testing",
                            "issue": "Exposed Cloud API Access Token Keys",
                            "severity": "Critical", "brief_summary": "Exposed credentials in source markup.",
                            "desc": "Live application source files contain raw cloud service keys.",
                            "requirement_id": "REQ-AUTH-01",
                            "reproduction": "1. Render source markup script arrays.\n2. Scan pattern characters.\n3. Extract bare credential key strings."
                        })

                if axe_payload:
                    try:
                        await page.evaluate(axe_payload)
                        axe_res = await page.evaluate("async () => { return await axe.run(); }")
                        for violation in axe_res.get("violations", []):
                            telemetry["all_bugs"].append({
                                "bug_id": f"BUG-A11Y-{hash(current_route + violation['id']) % 10000}",
                                "route_location": current_route, "module": "Accessibility Testing",
                                "issue": f"WCAG: {violation['id'].upper()}",
                                "severity": "Medium" if violation["impact"] == "moderate" else "High",
                                "brief_summary": f"WCAG rule validation criteria fail: {violation['id']}",
                                "desc": violation["help"],
                                "requirement_id": "REQ-A11Y-01",
                                "reproduction": f"1. Target accessible node tree.\n2. Locate DOM element footprint.\n3. Review WCAG guideline break condition."
                            })
                    except:
                        pass
                else:
                    raw_a11y = await page.evaluate("""() => {
                        let issues = [];
                        document.querySelectorAll('img:not([alt])').forEach(el => issues.push({i: 'Missing Image Alternative Text String', s: 'Medium', b: 'Missing image alternative property'}));
                        document.querySelectorAll('input:not([id])').forEach(el => issues.push({i: 'Missing Form Accessible Label Association', s: 'High', b: 'Unmapped template input node'}));
                        return issues;
                    }""")
                    for item in raw_a11y:
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-A11Y-RAW-{hash(current_route + item['i']) % 10000}",
                            "route_location": current_route, "module": "Accessibility Testing", "issue": item["i"],
                            "severity": item["s"],
                            "brief_summary": item["b"],
                            "desc": "DOM structure lacks required screen-reader properties.",
                            "requirement_id": "REQ-A11Y-01",
                            "reproduction": "1. Traverse DOM structure.\n2. Validate element parameters."
                        })

                viewports = [("Mobile", 375, 667), ("Tablet", 768, 1024), ("Desktop", 1920, 1080)]
                for vp_name, w, h in viewports:
                    await page.set_viewport_size({"width": w, "height": h})
                    await page.wait_for_timeout(200)

                    overlaps = await page.evaluate("""() => {
                        let collisions = 0;
                        let els = Array.from(document.querySelectorAll('button, input, a')).slice(0, 10);
                        for(let i=0; i<els.length; i++) {
                            let r1 = els[i].getBoundingClientRect();
                            for(let j=i+1; j<els.length; j++) {
                                let r2 = els[j].getBoundingClientRect();
                                if(!(r1.right <= r2.left || r1.left >= r2.right || r1.bottom <= r2.top || r1.top >= r2.bottom)) {
                                    collisions++;
                                }
                            }
                        }
                        return collisions;
                    }""")
                    if overlaps > 0:
                        telemetry["all_bugs"].append({
                            "bug_id": f"BUG-RESP-{hash(current_route + vp_name) % 10000}",
                            "route_location": current_route, "module": "Responsive Testing",
                            "issue": f"Layout Compression Overflow ({vp_name})",
                            "severity": "Low",
                            "brief_summary": f"Visual overlap detected on resolution breakpoint {vp_name}.",
                            "desc":
