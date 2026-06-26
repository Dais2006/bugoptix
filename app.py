import os
import asyncio
import subprocess
import sys
import json
import base64
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

# --- MNC PLATFORM DESIGN MATRIX ---
strl.set_page_config(
    page_title="BugOptix Ultra Engine | MNC Compliance Core",
    page_icon="🛡️",
    layout="wide"
)

strl.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Inter', sans-serif; }
    .stButton>button {
        background: linear-gradient(180deg, #2ea043 0%, #238636 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        width: 100%;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }
    .score-high { color: #56d364; font-size: 28px; font-weight: bold; }
    .score-mid { color: #e3b341; font-size: 28px; font-weight: bold; }
    .score-low { color: #ff7b72; font-size: 28px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- PERSISTENT ENTERPRISE VAULT FACTORY ---
VAULT_FILE = "bugoptix_mnc_vault.json"

class VaultController:
    @staticmethod
    def read_records() -> dict:
        if os.path.exists(VAULT_FILE):
            try:
                with open(VAULT_FILE, "r") as f: return json.load(f)
            except: pass
        return {"scans": [], "tickets": []}

    @staticmethod
    def write_records(data: dict):
        try:
            with open(VAULT_FILE, "w") as f: json.dump(data, f, indent=4)
        except: pass

if "vault" not in strl.session_state:
    strl.session_state["vault"] = VaultController.read_records()

# --- DETERMINISTIC CORE EVALUATION ENGINE ---
async def execute_enterprise_core_sweep(target_url: str, crawl_depth: int, responsive_viewports: list) -> dict:
    """
    Executes live spidering, multi-viewport layout validation, transport stream header auditing,
    and missing accessibility property scanning across dynamic internal routes.
    """
    telemetry = {
        "url": target_url, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawled_routes": [], "security_alerts": [], "accessibility_flaws": [], "ui_layout_bugs": [],
        "metrics": {"security": 100, "accessibility": 100, "ui_ux": 100}, "snapshots": {}
    }
    
    parsed_root = urlparse(target_url)
    crawl_queue = [target_url]
    visited_routes = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        
        # 1. LIVE LINK SPIDER AND CRAWLER ENGINE
        while crawl_queue and len(visited_routes) < crawl_depth:
            current_route = crawl_queue.pop(0)
            if current_route in visited_routes:
                continue
                
            visited_routes.add(current_route)
            telemetry["crawled_routes"].append(current_route)
            
            # Create contextual workspace profile
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()
            
            try:
                response = await page.goto(current_route, wait_until="domcontentloaded", timeout=15000)
                
                # 2. DETERMINISTIC SECURITY HEADERS & COOKIE TRANSPORT AUDIT
                if response:
                    headers = {k.lower(): v for k, v in response.headers.items()}
                    
                    # Content Security Policy (CSP) Analysis
                    if "content-security-policy" not in headers:
                        telemetry["security_alerts"].append({
                            "route": current_route, "type": "Missing CSP", 
                            "desc": "The application lacks a Content-Security-Policy header, leaving it vulnerable to XSS injection."
                        })
                    
                    # HTTP Strict Transport Security (HSTS) Audit
                    if "strict-transport-security" not in headers:
                        telemetry["security_alerts"].append({
                            "route": current_route, "type": "Missing HSTS", 
                            "desc": "Transport layer does not enforce strict HTTPS redirection rules."
                        })
                        
                    # Mixed Content & Resource Protocol Detection
                    insecure_assets = await page.evaluate("""() => {
                        return Array.from(document.querySelectorAll('img, script, link'))
                                    .map(el => el.src || el.href)
                                    .filter(src => src && src.startsWith('http://'));
                    }""")
                    for asset in insecure_assets:
                        telemetry["security_alerts"].append({
                            "route": current_route, "type": "Mixed Content Ingestion",
                            "desc": f"Insecure cleartext resource protocol link detected: {asset}"
                        })

                # Cookie Cryptographic Scoping Checks
                server_cookies = await context.cookies()
                for cookie in server_cookies:
                    if not cookie.get("httpOnly") or not cookie.get("secure"):
                        telemetry["security_alerts"].append({
                            "route": current_route, "type": "Insecure Session Cookie Configuration",
                            "desc": f"Cookie allocation tokens for state identifier '{cookie['name']}' do not enforce HttpOnly/Secure flags."
                        })

                # 3. DETERMINISTIC CORE ACCESSIBILITY AUDIT MODULE
                accessibility_anomalies = await page.evaluate("""() => {
                    let flaws = [];
                    // Missing Image Alternative Text Attributes
                    document.querySelectorAll('img:not([alt])').forEach(el => {
                        flaws.push({type: "Missing Alt Attribute", tag: el.outerHTML.substring(0, 100)});
                    });
                    // Structural Form Fields Missing Associated Labels
                    document.querySelectorAll('input:not([id]), select:not([id])').forEach(el => {
                        flaws.push({type: "Missing Input Labelling Schema", tag: el.outerHTML.substring(0, 100)});
                    });
                    return flaws;
                }""")
                for flaw in accessibility_anomalies:
                    telemetry["accessibility_flaws"].append({"route": current_route, **flaw})

                # 4. MULTI-VIEWPORT RESPONSIVE AND VIEWPORT OVERLAP ENGINE
                for viewport_config in responsive_viewports:
                    w, h = viewport_config["width"], viewport_config["height"]
                    await page.set_viewport_size({"width": w, "height": h})
                    await page.wait_for_timeout(500) # Stabilize DOM render metrics
                    
                    # Live Bounding-Box Overlay Math Collision Check
                    layout_collisions = await page.evaluate("""() => {
                        let issues = [];
                        let targets = Array.from(document.querySelectorAll('button, input, a, div.card'));
                        for(let i=0; i<Math.min(targets.length, 15); i++) {
                            let r1 = targets[i].getBoundingClientRect();
                            if (r1.width === 0 || r1.height === 0) continue;
                            for(let j=i+1; j<Math.min(targets.length, 15); j++) {
                                let r2 = targets[j].getBoundingClientRect();
                                if (r2.width === 0 || r2.height === 0) continue;
                                
                                if (!(r1.right <= r2.left || r1.left >= r2.right || r1.bottom <= r2.top || r1.top >= r2.bottom)) {
                                    issues.push(`Overlapping layout collision found between structural components.`);
                                    break;
                                }
                            }
                            if(issues.length > 0) break;
                        }
                        return issues;
                    }""")
                    
                    if layout_collisions:
                        telemetry["ui_layout_bugs"].append({
                            "route": current_route, "viewport": f"{w}x{h} ({viewport_config['name']})",
                            "desc": "Overlapping interactive components detected within current layout boundary parameters."
                        })

                    # Capture snapshot verification artifact for the baseline index root URL
                    if current_route == target_url and viewport_config["name"] == "Desktop standard":
                        img_bytes = await page.screenshot(full_page=False)
                        telemetry["snapshots"]["desktop_root"] = base64.b64encode(img_bytes).decode("utf-8")

                # Map out undiscovered internal path nodes
                internal_links = await page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href'));
                }""")
                for link in internal_links:
                    absolute_link = urljoin(current_route, link)
                    if urlparse(absolute_link).netloc == parsed_root.netloc and absolute_link not in visited_routes:
                        crawl_queue.append(absolute_link)

            except Exception as e:
                telemetry["security_alerts"].append({"route": current_route, "type": "Network Failure", "desc": str(e)})
            finally:
                await context.close()
                
        await browser.close()
    
    # 5. DYNAMIC MATHEMATICAL PENALTY SCORING
    telemetry["metrics"]["security"] = max(5, 100 - (len(telemetry["security_alerts"]) * 15))
    telemetry["metrics"]["accessibility"] = max(5, 100 - (len(telemetry["accessibility_flaws"]) * 10))
    telemetry["metrics"]["ui_ux"] = max(5, 100 - (len(telemetry["ui_layout_bugs"]) * 20))
    
    return telemetry

# --- INTERACTIVE ENGINEERING COMMAND INTERFACE ---
strl.title("🛡️ BugOptix Ultra Engine | Enterprise Core Suite")
strl.markdown("---")

runner_tab, metrics_tab = strl.tabs(["🚀 Core Automation Runner", "📊 Enterprise System Metrics Dashboard"])

with runner_tab:
    left_ui, right_ui = strl.columns([2, 1])
    with left_ui:
        url_input = strl.text_input("Corporate Target URL Protocol Endpoint Address:", value="https://example.com")
    with right_ui:
        spider_limit = strl.slider("Max Link Graph Automated Spider Limits (Web Crawler Limits):", min_value=1, max_value=10, value=3)

    viewport_matrix = [
        {"name": "Desktop standard", "width": 1280, "height": 800},
        {"name": "Tablet adaptive", "width": 768, "height": 1024},
        {"name": "Mobile responsive", "width": 375, "height": 667}
    ]

    if strl.button("Dispatch Production Quality Gate Task Block"):
        with strl.spinner("Running deterministic MNC compliance engine sweeps across infrastructure nodes..."):
            audit_result = asyncio.run(execute_enterprise_core_sweep(url_input.strip(), spider_limit, viewport_matrix))
            
            # Persist real findings to storage ledger
            vault_records = VaultController.read_records()
            vault_records["scans"].append(audit_result)
            VaultController.write_records(vault_records)
            strl.session_state["vault"] = vault_records
            
        strl.success("Assessment engine sweep complete. Real-time telemetry compiled below.")
        
        # Display Live Actionable Results Layout
        sec_col, acc_col, ui_col = strl.columns(3)
        with sec_col:
            score = audit_result["metrics"]["security"]
            cls = "score-high" if score > 80 else ("score-mid" if score > 50 else "score-low")
            strl.markdown(f"<div class='metric-card'><h4>Security Score</h4><p class='{cls}'>{score}/100</p></div>", unsafe_allow_html=True)
        with acc_col:
            score = audit_result["metrics"]["accessibility"]
            cls = "score-high" if score > 80 else ("score-mid" if score > 50 else "score-low")
            strl.markdown(f"<div class='metric-badge metric-card'><h4>Accessibility Score</h4><p class='{cls}'>{score}/100</p></div>", unsafe_allow_html=True)
        with ui_col:
            score = audit_result["metrics"]["ui_ux"]
            cls = "score-high" if score > 80 else ("score-mid" if score > 50 else "score-low")
            strl.markdown(f"<div class='metric-badge metric-card'><h4>UI/UX Layout Score</h4><p class='{cls}'>{score}/100</p></div>", unsafe_allow_html=True)

        # Print live finding lists
        if audit_result["security_alerts"]:
            strl.error("⚠️ Real Security Compliance Threats Identified:")
            strl.dataframe(pd.DataFrame(audit_result["security_alerts"]), use_container_width=True)
        else:
            strl.success("✔️ 0 Security Transport Flaws Detected across crawled routes.")

        if audit_result["accessibility_flaws"]:
            strl.warning("♿ Real Accessibility Compliance Violations Logged:")
            strl.dataframe(pd.DataFrame(audit_result["accessibility_flaws"]), use_container_width=True)

        if audit_result["snapshots"].get("desktop_root"):
            strl.markdown("### 📸 Captured Visual Validation Checkpoint View (Desktop Root Node)")
            strl.image(base64.b64decode(audit_result["snapshots"]["desktop_root"]), use_container_width=True)

with metrics_tab:
    history_logs = strl.session_state["vault"]["scans"]
    if not history_logs:
        strl.info("Enterprise storage vault contains no testing records under this node yet.")
    else:
        strl.markdown("### ⏳ Production Historical Audit Ledger")
        summary_builder = []
        for index, log in enumerate(history_logs):
            summary_builder.append({
                "Build ID": f"MNC-0{index+501}",
                "Execution Time": log["timestamp"],
                "Inspected URI": log["url"],
                "Security Vulnerabilities Found": len(log["security_alerts"]),
                "Accessibility Faults Found": len(log["accessibility_flaws"]),
                "Responsive UI Overlaps Found": len(log["ui_layout_bugs"]),
                "Routes Covered": len(log["crawled_routes"])
            })
        strl.dataframe(pd.DataFrame(summary_builder), use_container_width=True)
