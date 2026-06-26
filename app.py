import os
import asyncio
import subprocess
import sys
import time
import json
from datetime import datetime
import streamlit as strl

# --- MANDATORY PRE-FLIGHT SYSTEM INITIALIZATION ---
@strl.cache_resource
def initialize_playwright_binaries():
    try:
        expected_bin_path = os.path.expanduser("~/.cache/ms-playwright")
        if not os.path.exists(expected_bin_path):
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    except Exception as e:
        pass

initialize_playwright_binaries()

from google import genai
from google.genai.errors import APIError
from playwright.async_api import async_playwright

# --- Deep Space Enterprise Theme Configuration ---
strl.set_page_config(
    page_title="BugOptix Platform | Automated Compliance & Risk Suite",
    page_icon="🛡️",
    layout="wide"
)

strl.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    h1 { color: #58a6ff !important; font-family: 'Inter', sans-serif; font-weight: 700; letter-spacing: -0.5px; }
    h3 { color: #8b949e !important; }
    .stButton>button {
        background: linear-gradient(180deg, #2ea043 0%, #238636 100%) !important;
        color: #ffffff !important; 
        border-radius: 6px !important; 
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important; 
        width: 100%;
        border: 1px solid rgba(240,246,252,0.1) !important;
    }
    .stButton>button:hover { background: #2ea043 !important; border-color: #3fb950 !important; }
    .report-card {
        background-color: #161b22; 
        padding: 24px; 
        border-radius: 8px;
        border: 1px solid #30363d; 
        margin-top: 15px;
        font-family: monospace;
        white-space: pre-wrap;
        color: #e6edf3;
    }
    .metric-badge {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .risk-score-critical { color: #ff7b72; font-weight: bold; }
    .risk-score-major { color: #ffa657; font-weight: bold; }
    .risk-score-nominal { color: #56d364; font-weight: bold; }
    div.stDownloadButton > button {
        background: linear-gradient(180deg, #58a6ff 0%, #2188ff 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(240,246,252,0.1) !important; 
        border-radius: 6px !important;
        padding: 0.6rem 1.5rem !important;
        width: 100%;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Historical Performance Store Engine ---
HISTORICAL_LOG_FILE = "bugoptix_history_store.json"

def load_historical_metrics():
    if os.path.exists(HISTORICAL_LOG_FILE):
        try:
            with open(HISTORICAL_LOG_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_audit_to_history(url, title, score, issues_count):
    history = load_historical_metrics()
    history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
        "title": title,
        "executive_risk_score": score,
        "total_defects_discovered": issues_count
    })
    try:
        with open(HISTORICAL_LOG_FILE, "w") as f:
            json.dump(history[-10:], f, indent=4)
    except:
        pass

# --- Multi-Page Ingestion Core Engine ---
async def crawl_and_audit_node(base_url: str, max_crawl_pages: int, viewport_profile: str) -> dict:
    results = {
        "success": False, "title": "Enterprise Portal Scope", "crawled_pages": [],
        "form_structures": [], "console_errors": [], "failed_requests": [],
        "accessibility_violations": [], "security_vulnerabilities": [],
        "visual_regression_anomalies": [], "perf_footprint_ms": 0, "screenshot": None
    }
    
    dimensions = {
        "desktop (1080p)": {"w": 1920, "h": 1080, "is_mobile": False},
        "ios": {"w": 393, "h": 852, "is_mobile": True},
        "android": {"w": 412, "h": 915, "is_mobile": True}
    }
    cfg = dimensions.get(viewport_profile.lower(), dimensions["desktop (1080p)"])
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = await browser.new_context(
                viewport={"width": cfg["w"], "height": cfg["h"]},
                is_mobile=cfg["is_mobile"],
                user_agent="BugOptixPlatformEngine/4.0Enterprise"
            )
            page = await context.new_page()
            
            page.on("pageerror", lambda e: results["console_errors"].append(f"JS Error: {e}"))
            page.on("requestfailed", lambda r: results["failed_requests"].append(f"Broken Pathway: {r.url}"))
            
            start_time = time.time()
            try:
                await page.goto(base_url, wait_until="domcontentloaded", timeout=15000)
                results["crawled_pages"].append(base_url)
                results["title"] = await page.title() or "Workspace Scope"
            except Exception as e:
                results["console_errors"].append(f"Base navigation timeout: {e}")

            discovered_links = await page.evaluate("""() => 
                Array.from(document.querySelectorAll('a')).map(a => a.href).filter(h => h.startsWith(window.location.origin))
            """)
            unique_targets = list(set(discovered_links))[:max_crawl_pages]
            
            for sub_url in unique_targets:
                if sub_url not in results["crawled_pages"]:
                    try:
                        await page.goto(sub_url, wait_until="domcontentloaded", timeout=10000)
                        results["crawled_pages"].append(sub_url)
                    except:
                        results["failed_requests"].append(f"Crawling link drop: {sub_url}")

            results["perf_footprint_ms"] = int((time.time() - start_time) * 1000)
            
            if results["crawled_pages"]:
                try: await page.goto(base_url, wait_until="domcontentloaded", timeout=10000)
                except: pass

            if not base_url.startswith("https://"):
                results["security_vulnerabilities"].append("CRITICAL: Asset exchange data transmitted over unencrypted HTTP cleartext.")
            
            forms_payload = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('input, textarea, select')).map(el => ({
                    tagName: el.tagName.toLowerCase(),
                    type: el.type || 'text',
                    name: el.name || '',
                    id: el.id || '',
                    maxlength: el.getAttribute('maxlength') || 'MISSING',
                    required: el.hasAttribute('required') ? 'YES' : 'NO'
                }));
            }""")
            
            for field in forms_payload:
                fn = field["name"].lower()
                if field["maxlength"] == "MISSING" and any(k in fn for k in ["mobile", "phone", "tel"]):
                    field["maxlength"] = "MISSING (Defect: Unbounded length validation for mobile variables)"
                elif field["maxlength"] == "MISSING" and any(k in fn for k in ["aadhar", "uid"]):
                    field["maxlength"] = "MISSING (Defect: Unbounded length verification for compliance strings)"
                results["form_structures"].append(field)

            acc_logs = await page.evaluate("""() => {
                const audit = [];
                document.querySelectorAll('img').forEach(img => { if(!img.hasAttribute('alt')) audit.push(`Missing 'alt' data trait on asset: ${img.src}`); });
                document.querySelectorAll('input:not([type="hidden"])').forEach(i => { if(!i.hasAttribute('id') && !i.closest('label')) audit.push(`Input missing explicit programmatic connection: Name=${i.name}`); });
                return audit;
            }""")
            results["accessibility_violations"] = acc_logs

            visual_shifts = await page.evaluate("""() => {
                const anomalies = [];
                document.querySelectorAll('*').forEach(el => {
                    const style = window.getComputedStyle(el);
                    if (style.overflow === 'hidden' && (el.scrollWidth > el.clientWidth || el.scrollHeight > el.clientHeight)) {
                        anomalies.push(`Layout Regression: Content cutoff layout overflow detected inside element: ${el.tagName.toLowerCase()}`);
                    }
                });
                return anomalies;
            }""")
            results["visual_regression_anomalies"] = visual_shifts[:5]

            try: results["screenshot"] = await page.screenshot(full_page=False, timeout=3000)
            except: pass
            
            results["success"] = True
            await browser.close()
    except Exception as general_fault:
        results["error"] = str(general_fault)
    return results

# --- REPORT CONVERTER COMPILER ENGINE ---
def generate_pdf_report(report_text, target_url, audit_title):
    html_content = f"""
    <html><head><style>body {{ font-family: sans-serif; padding: 40px; color: #333; }} .header {{ border-bottom: 2px solid #58a6ff; }} .content {{ font-family: monospace; white-space: pre-wrap; background: #f6f8fa; padding: 20px; }}</style></head>
    <body><div class="header"><h2>🛡️ BugOptix Platform Core Report</h2><h4>Scope: {target_url}</h4></div><div class="content">{report_text}</div></body></html>
    """
    async def render_pdf():
        async with async_playwright() as p:
            b = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await b.new_page()
            await page.set_content(html_content)
            pdf = await page.pdf(format="A4", print_background=True)
            await b.close()
            return pdf
    try: return asyncio.run(render_pdf())
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(render_pdf())

# --- Core Control Center UI Presentation Layer ---
strl.title("🛡️ BugOptix Platform — Unified Compliance Suite")
strl.markdown("### Continuous Quality Engineering, Risk Analysis & Multi-Page Compliance Audit Dashboard")
strl.markdown("---")

strl.sidebar.header("🔑 Operational Credentials")
ui_key_input = strl.sidebar.text_input("Gemini API Key Keyhole:", type="password")
selected_model = strl.sidebar.selectbox("Brain Execution Optimization Engine", ["gemini-2.5-flash", "gemini-2.5-pro"])
API_KEY = ui_key_input.strip() if ui_key_input.strip() else os.environ.get("GEMINI_API_KEY", "")

col1, col2 = strl.columns([2, 1])
with col1:
    target_url = strl.text_input("Target Application URL Endpoint:", value="", placeholder="https://example.com/erp/admission")
with col2:
    crawl_depth = strl.slider("Multi-Page Crawling Scope Cap (Unique Links)", min_value=1, max_value=10, value=3)

col3, col4 = strl.columns([2, 1])
with col3:
    target_selector = strl.text_input("Target Area Scope Selector (Optional):", placeholder="e.g. #login-form")
with col4:
    responsive_profile = strl.selectbox("Device Emulation Workspace Profile", ["Desktop (1080p)", "ios", "android"])

if "platform_report" not in strl.session_state: strl.session_state["platform_report"] = None
if "meta_title" not in strl.session_state: strl.session_state["meta_title"] = ""
if "executive_risk_score" not in strl.session_state: strl.session_state["executive_risk_score"] = 0
if "defect_density" not in strl.session_state: strl.session_state["defect_density"] = {}

if strl.button("🚀 Run Enterprise Automation Sweep"):
    if not target_url.strip():
        strl.warning("🚨 Operational Configuration Alert: Provide a valid domain URL.")
    else:
        with strl.spinner("🌐 Activating Crawlers, verifying WCAG elements..."):
            try:
                try: loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                audit_dataset = loop.run_until_complete(crawl_and_audit_node(target_url.strip(), crawl_depth, responsive_profile))
            except Exception as loop_fault:
                audit_dataset = {"success": False, "error": str(loop_fault)}

        if not audit_dataset.get("success"):
            strl.error(f"❌ Execution Core Fault: {audit_dataset.get('error')}")
        else:
            strl.success("✔️ Complete multi-vector evaluation run completed.")
            strl.session_state["meta_title"] = audit_dataset["title"]
            if audit_dataset.get("screenshot"): strl.session_state["platform_img"] = audit_dataset["screenshot"]

            vulnerabilities_total = (
                len(audit_dataset["console_errors"]) + len(audit_dataset["failed_requests"]) +
                len(audit_dataset["accessibility_violations"]) + len(audit_dataset["security_vulnerabilities"])
            )
            raw_risk_score = 100 - (vulnerabilities_total * 8)
            calculated_executive_score = max(5, min(raw_risk_score, 100))
            strl.session_state["executive_risk_score"] = calculated_executive_score

            strl.session_state["defect_density"] = {
                "pages_crawled": len(audit_dataset["crawled_pages"]),
                "broken_links": len(audit_dataset["failed_requests"]),
                "sec_alerts": len(audit_dataset["security_vulnerabilities"]),
                "acc_issues": len(audit_dataset["accessibility_violations"])
            }

            save_audit_to_history(target_url, audit_dataset["title"], calculated_executive_score, vulnerabilities_total)

            form_logs_txt = ""
            for field in audit_dataset.get("form_structures", []):
                form_logs_txt += f"- Element: {field['tagName']}, Type: {field['type']}, Name: {field['name']}, MaxLength: {field['maxlength']}, Required: {field['required']}\n"

            response_text = None
            if API_KEY:
                with strl.spinner("🧠 Consolidating Metrics via AI Processing Framework..."):
                    # SYSTEM FIX: Separated string concatenation completely from multi-line structures to eliminate unescaped tokens
                    system_analysis_prompt = (
                        "Audit this platform mapping payload:\n\n"
                        "URL Reference Target: " + str(target_url) + "\n"
                        "Discovered Footprint: " + ", ".join(audit_dataset["crawled_pages"]) + "\n\n"
                        "Form Config Metrics:\n" + str(form_logs_txt) + "\n\n"
                        "Provide an evaluation matrix breaking down Security, Input MaxLength overflows, and WCAG errors."
                    )
                    try:
                        client = genai.Client(api_key=API_KEY)
                        response = client.models.generate_content(model=selected_model, contents=system_analysis_prompt)
                        response_text = response.text
                    except Exception as e:
                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                            time.sleep(42)
                            try:
                                response = client.models.generate_content(model=selected_model, contents=system_analysis_prompt)
                                response_text = response.text
                            except: pass

            if not response_text:
                response_text = f"Audit Run Completed.\n\nForm Map Configuration:\n{form_logs_txt}"
            strl.session_state["platform_report"] = response_text

# --- Present Dashboard Interfaces ---
if strl.session_state["defect_density"]:
    strl.markdown("### 📊 Live Core Diagnostics & Analytics Dashboard")
    d_col1, d_col2, d_col3, d_col4 = strl.columns(4)
    
    score_label = "risk-score-nominal"
    if strl.session_state["executive_risk_score"] < 50: score_label = "risk-score-critical"
    elif strl.session_state["executive_risk_score"] < 80: score_label = "risk-score-major"
    
    with d_col1:
        strl.markdown(f"<div class='metric-badge'><h3>🛡️ Executive Risk Score</h3><h2 class='{score_label}'>{strl.session_state['executive_risk_score']}/100</h2></div>", unsafe_allow_html=True)
    with d_col2:
        strl.markdown(f"<div class='metric-badge'><h3>🕸️ Map Nodes Discovered</h3><h2>{strl.session_state['defect_density']['pages_crawled']} Pages</h2></div>", unsafe_allow_html=True)
    with d_col3:
        strl.markdown(f"<div class='metric-badge'><h3>⚠️ WCAG Failures</h3><h2>{strl.session_state['defect_density']['acc_issues']} Flags</h2></div>", unsafe_allow_html=True)
    with d_col4:
        strl.markdown(f"<div class='metric-badge'><h3>🚨 Security Liabilities</h3><h2>{strl.session_state['defect_density']['sec_alerts']} Findings</h2></div>", unsafe_allow_html=True)

strl.markdown("---")
dash_left, dash_right = strl.columns([2, 1])

with dash_left:
    if strl.session_state["platform_report"]:
        strl.markdown("### 📝 Live Diagnostic Artifact Output View")
        strl.markdown("<div class='report-card'>", unsafe_allow_html=True)
        strl.text(strl.session_state["platform_report"])
        strl.markdown("</div>", unsafe_allow_html=True)
        
        pdf_binary_package = generate_pdf_report(strl.session_state["platform_report"], target_url, strl.session_state["meta_title"])
        strl.download_button(
            label="📥 Download Official BugOptix QA Test Report Document (.pdf)",
            data=pdf_binary_package, file_name="BugOptix_Platform_Audit_Artifact.pdf", mime="application/pdf", use_container_width=True
        )

with dash_right:
    strl.markdown("### ⏳ Historical Analytics Logs")
    history_records = load_historical_metrics()
    if history_records:
        for item in reversed(history_records):
            strl.info(f"📅 **{item['timestamp']}**\n* Scope: `{item['url']}`\n* Risk Score: **{item['executive_risk_score']}/100**")
    else:
        strl.markdown("_No data metrics registered in workspace logs yet._")
        
    strl.markdown("### ⚙️ CI/CD Deployment Integration Engine")
    with strl.expander("🔗 View Webhook Pipeline Trigger Configuration"):
        strl.code(f"curl -X POST https://your-bugoptix-instance.streamlit.app/ -d \"url={target_url}\"", language="bash")

if "platform_img" in strl.session_state:
    strl.markdown("### 📸 Captured Visual UI Layout Checkpoint")
    strl.image(strl.session_state["platform_img"], use_container_width=True)
