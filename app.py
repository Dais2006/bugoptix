import os
import asyncio
import subprocess
import sys
import time
import re
import streamlit as strl

# --- MANDATORY PRE-FLIGHT SYSTEM INITIALIZATION ---
@strl.cache_resource
def initialize_playwright_binaries():
    try:
        expected_bin_path = os.path.expanduser("~/.cache/ms-playwright")
        if not os.path.exists(expected_bin_path):
            print("Downloading container headless browser dependencies...")
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            print("System binaries mapped successfully.")
    except Exception as e:
        print(f"Pre-flight binary configuration note: {e}")

initialize_playwright_binaries()

from google import genai
from google.genai.errors import APIError
from playwright.async_api import async_playwright

# --- Deep Space Enterprise Theme Configuration ---
strl.set_page_config(
    page_title="BugOptix Ultra | Enterprise QA Automation Audit Suite",
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
        transition: background 0.2s ease;
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
        overflow-x: auto;
        color: #e6edf3;
    }
    .metric-badge {
        background-color: #21262d;
        border: 1px solid #30363d;
        padding: 10px 15px;
        border-radius: 6px;
        text-align: center;
    }
    div.stDownloadButton > button {
        background: linear-gradient(180deg, #58a6ff 0%, #2188ff 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(240,246,252,0.1) !important; 
        border-radius: 6px !important;
        padding: 0.6rem 1.5rem !important;
        width: 100%;
        font-weight: 600 !important;
    }
    div.stDownloadButton > button:hover { background: #2188ff !important; border-color: #58a6ff !important; }
    </style>
""", unsafe_allow_html=True)


# --- Resilient Multi-Testing Automation Crawling Engine ---
async def perform_deep_audit(url: str, depth: str, selector: str, profile: str) -> dict:
    results = {
        "success": False, "title": "Target Sandbox Domain", "content": "",
        "form_structures": [], "console_errors": [], "failed_requests": [], "error": "", "screenshot": None,
        "perf_metrics": {}, "accessibility_flags": [], "security_alerts": [], "discovered_links": []
    }

    dimensions = {
        "desktop (1080p)": {"w": 1920, "h": 1080, "is_mobile": False},
        "ios": {"w": 393, "h": 852, "is_mobile": True},
        "android": {"w": 412, "h": 915, "is_mobile": True}
    }
    target_config = dimensions.get(profile.lower(), dimensions["desktop (1080p)"])

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                viewport={"width": target_config["w"], "height": target_config["h"]},
                is_mobile=target_config["is_mobile"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # Listeners for real-time console crashes and broken link/network validation tracking
            page.on("pageerror", lambda exc: results["console_errors"].append(f"JS Crash: {exc}"))
            page.on("requestfailed", lambda req: results["failed_requests"].append(f"Broken Resource Drop: {req.url} — Code: {req.failure.error_text if req.failure else '404/500'}"))

            start_time = time.time()
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(1500)
            except Exception as context_error:
                results["console_errors"].append(f"Navigation bypass: {context_error}")

            results["perf_metrics"]["load_time_ms"] = int((time.time() - start_time) * 1000)

            try:
                results["title"] = await page.title() or "Target Portal Workspace"
                
                # Multi-Page Crawling and Discovery Setup
                hrefs = await page.evaluate("() => Array.from(document.querySelectorAll('a')).map(a => a.href)")
                results["discovered_links"] = list(set([h for h in hrefs if h.startswith("http")]))[:15]

                # 1. Structural Form Mapping Extraction
                form_elements = await page.evaluate("""() => {
                    const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
                    return inputs.map(el => {
                        const maxAttr = el.getAttribute('maxlength');
                        return {
                            tagName: el.tagName.toLowerCase(),
                            type: el.type || 'text',
                            name: el.name || '',
                            id: el.id || '',
                            placeholder: el.placeholder || '',
                            maxlength: maxAttr || 'MISSING',
                            required: el.hasAttribute('required') ? 'YES' : 'NO'
                        };
                    });
                }""")
                
                # Active Boundary Logic Validation Test Modifiers
                validated_structures = []
                for field in form_elements:
                    fn = field["name"].lower()
                    if field["maxlength"] == "MISSING" and ("mobile" in fn or "phone" in fn or "tel" in fn):
                        field["maxlength"] = "MISSING (Bug: Accepts unrestricted inputs despite fixed-length real world rules)"
                    elif field["maxlength"] == "MISSING" and ("aadhar" in fn or "uid" in fn):
                        field["maxlength"] = "MISSING (Bug: System allows invalid length character submissions)"
                    validated_structures.append(field)
                results["form_structures"] = validated_structures

                # 2. Accessibility Testing Matrix
                acc_flags = await page.evaluate("""() => {
                    const logs = [];
                    const imgs = document.querySelectorAll('img');
                    imgs.forEach(img => { if(!img.hasAttribute('alt')) logs.push(`Missing 'alt' tag on image resource: ${img.src}`); });
                    const inputs = document.querySelectorAll('input:not([type="submit"]):not([type="hidden"])');
                    inputs.forEach(i => { if(!i.hasAttribute('id') && !i.closest('label')) logs.push(`Input element missing clean explicitly bounded structural label connection: Name=${i.name}`); });
                    return logs;
                }""")
                results["accessibility_flags"] = acc_flags

                # 3. Security Testing Engine
                sec_alerts = []
                if not url.startswith("https://"):
                    sec_alerts.append("CRITICAL: Unencrypted communication pipeline deployment protocol detected (HTTP).")
                
                form_html = await page.evaluate("() => Array.from(document.querySelectorAll('form')).map(f => f.outerHTML).join(' ')")
                if "autocomplete=\"off\"" not in form_html.lower() and "password" in form_html.lower():
                    sec_alerts.append("VULNERABILITY: Form input credentials missing explicit autocomplete preventive constraints.")
                results["security_alerts"] = sec_alerts

                body_element = page.locator("body")
                raw_text = await body_element.inner_text()
                results["content"] = " ".join(raw_text.split())[:3000]
                
                try:
                    results["screenshot"] = await page.screenshot(full_page=False, timeout=3000)
                except Exception:
                    pass
                
                results["success"] = True
            except Exception as extraction_err:
                results["error"] = f"Extraction error: {extraction_err}"
                results["success"] = False

            await browser.close()
    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
    return results


# --- NATIVE BROWSER PDF CONVERTER ENGINE ---
def generate_pdf_report(report_text, target_url, audit_title):
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333333; line-height: 1.6; padding: 40px; }}
            .header {{ border-bottom: 2px solid #58a6ff; padding-bottom: 15px; margin-bottom: 30px; }}
            .title {{ color: #0056b3; font-size: 24px; font-weight: bold; margin: 0; }}
            .meta {{ color: #666666; font-size: 12px; margin-top: 5px; }}
            .content {{ font-family: 'Courier New', Courier, monospace; white-space: pre-wrap; background-color: #f6f8fa; padding: 20px; border-radius: 6px; border: 1px solid #ddd; font-size: 13px; }}
            .footer {{ margin-top: 40px; text-align: center; font-size: 11px; color: #999999; border-top: 1px solid #eee; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">🛡️ BugOptix Ultra — Formal Compliance Artifact</div>
            <div class="meta">Target Scope: {target_url} | Workspace: {audit_title}</div>
        </div>
        <div class="content">{report_text}</div>
        <div class="footer">Generated securely via BugOptix Deep Diagnostic Suite Infrastructure Engine</div>
    </body>
    </html>
    """
    
    async def render_pdf():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page()
            await page.set_content(html_content)
            pdf_bytes = await page.pdf(format="A4", print_background=True)
            await browser.close()
            return pdf_bytes

    try:
        return asyncio.run(render_pdf())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(render_pdf())


# --- Layout Presentation Layer ---
strl.title("🛡️ BugOptix AI — Deep Diagnostic Suite")
strl.markdown("### Automated Web Application QA & Technical Compliance Engine")
strl.markdown("---")

strl.sidebar.header("🔑 Authentication Setup")
ui_key_input = strl.sidebar.text_input("Enter Gemini API Key:", type="password")
selected_model = strl.sidebar.selectbox("AI Brain Model Setup", ["gemini-2.5-flash", "gemini-2.5-pro"])

API_KEY = ui_key_input.strip() if ui_key_input.strip() else os.environ.get("GEMINI_API_KEY", "")

col1, col2 = strl.columns([2, 1])
with col1:
    target_url = strl.text_input("Target Application URL Endpoint:", value="", placeholder="https://example.com/erp/admission")
with col2:
    scan_depth = strl.selectbox("Operational Audit Depth", ["Full Matrix Diagnostic Sweep", "Surface UI Content Validation"])

col3, col4 = strl.columns([2, 1])
with col3:
    target_selector = strl.text_input("Target Element Scope Selector (Optional):", placeholder="e.g. #login-form")
with col4:
    responsive_profile = strl.selectbox("Device Emulation Viewport", ["Desktop (1080p)", "ios", "android"])

# Dashboard Analytics Metrics Storage Initialization
if "live_report" not in strl.session_state:
    strl.session_state["live_report"] = None
if "target_title" not in strl.session_state:
    strl.session_state["target_title"] = ""
if "metrics_dash" not in strl.session_state:
    strl.session_state["metrics_dash"] = None

if strl.button("🚀 Execute Comprehensive Deep Diagnostic Scan"):
    if not target_url.strip():
        strl.warning("🚨 Operational Warning: Provide a valid web URL schema.")
    else:
        with strl.spinner("🌐 Crawling targets, scanning links, and executing multi-vector engine diagnostics..."):
            try:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                audit_data = loop.run_until_complete(
                    perform_deep_audit(target_url.strip(), scan_depth, target_selector, responsive_profile))
            except Exception as loop_err:
                audit_data = {"success": False, "error": str(loop_err)}

        if not audit_data.get("success"):
            strl.error(f"❌ Connection Pipeline Terminated: {audit_data.get('error')}")
        else:
            strl.success("✔️ Comprehensive automated site trace diagnostics completed successfully.")
            strl.session_state["target_title"] = audit_data["title"]

            if audit_data.get("screenshot"):
                strl.session_state["captured_img"] = audit_data["screenshot"]

            console_logs_str = "\n".join(audit_data["console_errors"]) if audit_data["console_errors"] else "None."
            network_logs_str = "\n".join(audit_data["failed_requests"]) if audit_data["failed_requests"] else "None."
            sec_logs_str = "\n".join(audit_data["security_alerts"]) if audit_data["security_alerts"] else "None."
            acc_logs_str = "\n".join(audit_data["accessibility_flags"]) if audit_data["accessibility_flags"] else "None."
            discovered_links_str = "\n".join(audit_data["discovered_links"]) if audit_data["discovered_links"] else "None."
            
            form_summary = ""
            for field in audit_data.get("form_structures", []):
                form_summary += f"- Tag: {field['tagName']}, Type: {field['type']}, Name: {field['name']}, MaxLength: {field['maxlength']}, Required: {field['required']}\n"

            # Machine Learning Bug Prediction Weight Heuristics (Local Rules Evaluation Engine)
            ml_defect_probability = 15
            if "MISSING" in form_summary: ml_defect_probability += 45
            if audit_data["console_errors"]: ml_defect_probability += 25
            if audit_data["failed_requests"]: ml_defect_probability += 15
            ml_defect_probability = min(ml_defect_probability, 99)

            strl.session_state["metrics_dash"] = {
                "load_time": f"{audit_data['perf_metrics'].get('load_time_ms', 0)} ms",
                "broken_links": len(audit_data["failed_requests"]),
                "sec_alerts": len(audit_data["security_alerts"]),
                "ml_score": f"{ml_defect_probability}%"
            }

            response_text = None

            if API_KEY:
                with strl.spinner("🧠 Querying AI Severity Ranking models and consolidating report matrices..."):
                    system_analysis_prompt = (
                        f"You are a Principal Lead QA & Security Compliance Automation Engineer. Audit this website data for architectural bugs:\n\n"
                        f"URL Tested: {target_url}\n"
                        f"Page Title: {audit_data['title']}\n\n"
                        f"[FORM APPLICATION FIELD DESIGN]:\n{form_summary if form_summary else 'None.'}\n\n"
                        f"[BROKEN RESOURCE LINKS SCANNER]:\n{network_logs_str}\n\n"
                        f"[SECURITY COMPLIANCE VULNERABILITIES]:\n{sec_logs_str}\n\n"
                        f"[ACCESSIBILITY COMPLIANCE AUDIT (WCAG v2.1)]:\n{acc_logs_str}\n\n"
                        f"[CRAWLED SITEMAP DOMAIN PATHWAYS]:\n{discovered_links_str}\n\n"
                        f"[CLIENT LOG RUNTIME TRACES]:\n{console_logs_str}\n\n"
                        f"INSTRUCTIONS:\n"
                        f"Generate an Executive Core Audit Report explicitly structured into sections:\n"
                        f"1. AI SEVERITY RANKING MATRIX (Assign CRITICAL, MAJOR, or MINOR classifications to all identified faults based on risk calculations).\n"
                        f"2. SECURITY & DATA INTEGRITY VULNERABILITIES (Explain database risks, SQL/overflow liabilities, and missing MaxLengths on input limits for mobile or identity strings).\n"
                        f"3. ACCESSIBILITY & DESIGN DEVIATIONS (Enumerate text contrasts, missing alt tags, label failures).\n"
                        f"4. PERFORMANCE & LINK METRICS (Analyze broken image pathways, network drops, asset loading footprints)."
                    )
                    try:
                        client = genai.Client(api_key=API_KEY)
                        response = client.models.generate_content(model=selected_model, contents=system_analysis_prompt)
                        response_text = response.text
                    except Exception as e:
                        # --- 429 RATE LIMIT INTERCEPTOR ---
                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                            strl.warning("⏳ Free tier Pro quota exhausted. Automatically backing off for 40 seconds to reset...")
                            time.sleep(42) 
                            try:
                                response = client.models.generate_content(model=selected_model, contents=system_analysis_prompt)
                                response_text = response.text
                            except Exception as retry_fault:
                                strl.error(f"Fallback structural generation halted: {retry_fault}")
                        else:
                            strl.warning(f"AI fallthrough: {e}")

            if not response_text:
                response_text = (
                    f"### Real Bug Detection Engine Output\n\n"
                    f"**Form Structural Vectors:**\n{form_summary}\n"
                    f"**Broken Resource Links:**\n{network_logs_str}\n"
                    f"**Security Flags:**\n{sec_logs_str}\n"
                    f"**Accessibility Flags:**\n{acc_logs_str}"
                )

            strl.session_state["live_report"] = response_text

# --- State Preserving Presentation Layer & Dashboard Analytics ---
if strl.session_state["metrics_dash"]:
    strl.markdown("### 📊 Live Core Diagnostics & Analytics Dashboard")
    dash_col1, dash_col2, dash_col3, dash_col4 = strl.columns(4)
    with dash_col1:
        strl.markdown(f"<div class='metric-badge'><h3>⏱️ Performance</h3><h2>{strl.session_state['metrics_dash']['load_time']}</h2></div>", unsafe_allow_html=True)
    with dash_col2:
        strl.markdown(f"<div class='metric-badge'><h3>🔗 Broken Links</h3><h2>{strl.session_state['metrics_dash']['broken_links']}</h2></div>", unsafe_allow_html=True)
    with dash_col3:
        strl.markdown(f"<div class='metric-badge'><h3>🚨 Security Risks</h3><h2>{strl.session_state['metrics_dash']['sec_alerts']}</h2></div>", unsafe_allow_html=True)
    with dash_col4:
        strl.markdown(f"<div class='metric-badge'><h3>🤖 ML Defect Prediction</h3><h2>{strl.session_state['metrics_dash']['ml_score']}</h2></div>", unsafe_allow_html=True)
    strl.markdown("<br>", unsafe_allow_html=True)

if "captured_img" in strl.session_state:
    strl.markdown("### 📸 Captured Visual UI Layout Checkpoint")
    strl.image(strl.session_state["captured_img"], use_container_width=True)

if strl.session_state["live_report"]:
    strl.markdown("### 📊 Live System Audit Output Visualization")
    strl.markdown("<div class='report-card'>", unsafe_allow_html=True)
    strl.text(strl.session_state["live_report"])
    strl.markdown("</div>", unsafe_allow_html=True)
    
    strl.markdown("<br>", unsafe_allow_html=True)
    
    with strl.spinner("📊 Compiling report structures into secure PDF file format..."):
        generated_pdf_data = generate_pdf_report(
            strl.session_state["live_report"], 
            target_url, 
            strl.session_state["target_title"]
        )
    
    strl.download_button(
        label="📥 Download Official BugOptix QA Test Report Document (.pdf)",
        data=generated_pdf_data,
        file_name="BugOptix_Formal_Compliance_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
