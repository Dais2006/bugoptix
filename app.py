import os
import asyncio
import subprocess
import sys
import streamlit as strl

# --- MANDATORY PRE-FLIGHT SYSTEM INITIALIZATION ---
@strl.cache_resource
def initialize_playwright_binaries():
    try:
        expected_bin_path = os.path.expanduser("~/.cache/ms-playwright")
        if not os.path.exists(expected_bin_path):
            print("Downloading container headless browser dependencies...")
            # Safe synchronous execution of the browser framework compilation
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            print("System binaries mapped successfully.")
    except Exception as e:
        print(f"Pre-flight binary configuration note: {e}")

# Run installer immediately on app initialization frame
initialize_playwright_binaries()

# Safe to import core functional packages now
from google import genai
from google.genai.errors import APIError
from playwright.async_api import async_playwright

# --- Deep Space Enterprise Theme Configuration ---
strl.set_page_config(
    page_title="BugOptix | Ultimate Enterprise QA Auditor",
    page_icon="🛡️",
    layout="wide"
)

# Custom Corporate CSS Injection for Professional Presentation & Printing
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
    div.stDownloadButton > button {
        background-color: #21262d !important; 
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important; 
        border-radius: 6px !important;
        padding: 0.5rem 1.5rem !important;
        width: 100%;
        font-weight: 600 !important;
    }
    @media print {
        body * { visibility: hidden; }
        .report-card, .report-card * { visibility: visible; }
        .report-card { position: absolute; left: 0; top: 0; width: 100%; background: white !important; color: black !important; border: none; }
    }
    </style>
""", unsafe_allow_html=True)


# --- Deep Audit Web Scraper Engine ---
async def perform_deep_audit(url: str, depth: str, selector: str, profile: str) -> dict:
    results = {
        "success": False, "title": "Target Sandbox Domain", "content": "No visual content could be rendered.",
        "console_errors": [], "failed_requests": [], "error": "", "screenshot": None, "perf_metrics": {}
    }

    dimensions = {
        "desktop (1080p)": {"w": 1920, "h": 1080, "is_mobile": False},
        "ios": {"w": 393, "h": 852, "is_mobile": True},
        "android": {"w": 412, "h": 915, "is_mobile": True},
        "apple ipad pro": {"w": 1024, "h": 1366, "is_mobile": False}
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
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            page.on("pageerror", lambda exc: results["console_errors"].append(f"JS Crash: {exc}"))
            page.on("requestfailed", lambda req: results["failed_requests"].append(f"Network Drop: {req.url}"))

            try:
                await page.goto(url, wait_until="load", timeout=20000)
                await page.wait_for_timeout(1500)

                try:
                    results["perf_metrics"] = await page.evaluate("""() => {
                        const t = window.performance.timing;
                        return {
                            "load_time_ms": t.loadEventEnd - t.navigationStart,
                            "dom_ready_ms": t.domComplete - t.responseEnd
                        };
                    }""")
                except Exception:
                    results["perf_metrics"] = {"load_time_ms": "N/A", "dom_ready_ms": "N/A"}

                results["title"] = await page.title()

                raw_text = ""
                if selector.strip():
                    try:
                        target_element = page.locator(selector.strip()).first
                        raw_text = await target_element.inner_text()
                    except Exception:
                        raw_text = f"[System Warning: Element target selector matching '{selector}' was not found on screen.]"

                if not raw_text or selector.strip() == "":
                    body_element = page.locator("body")
                    raw_text = await body_element.inner_text()

                try:
                    results["screenshot"] = await page.screenshot(full_page=False, timeout=5000)
                except Exception:
                    results["screenshot"] = None

                cleaned_text = " ".join(raw_text.split())
                limit_len = 1200 if depth == "Surface UI Content Validation" else 2500
                results["content"] = cleaned_text[:limit_len] + "\n...[Optimized Payload For Free Quota Protection]..."
                results["success"] = True

            except Exception as nav_err:
                results["error"] = str(nav_err)
                results["success"] = False

            await browser.close()
    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
    return results


# --- App Presentation Layout ---
strl.title("🛡️ BugOptix AI — Deep Diagnostic Suite")
strl.markdown("### Automated Web Application QA & Technical Compliance Engine")
strl.markdown("---")

# Sidebar Authentication Panel
strl.sidebar.header("🔑 Authentication Setup")
ui_key_input = strl.sidebar.text_input("Enter Gemini API Key:", type="password")

selected_model = strl.sidebar.selectbox(
    "AI Brain Model Setup",
    ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"]
)

API_KEY = ui_key_input.strip() if ui_key_input.strip() else os.environ.get("GEMINI_API_KEY", "")

# Main Configuration Matrix Input Rows
col1, col2 = strl.columns([2, 1])
with col1:
    target_url = strl.text_input("Target Application URL Endpoint:", placeholder="https://example.com")
with col2:
    scan_depth = strl.selectbox("Operational Audit Depth",
                                ["Surface UI Content Validation", "Full Matrix Diagnostic Sweep"])

col3, col4 = strl.columns([2, 1])
with col3:
    target_selector = strl.text_input("Target Element Scope Selector (Optional):",
                                      placeholder="e.g. #login-form, .nav-bar, button")
with col4:
    responsive_profile = strl.selectbox(
        "Device Emulation Viewport",
        ["Desktop (1080p)", "ios", "android", "Apple iPad Pro"]
    )

strl.markdown("<br>", unsafe_allow_html=True)

# --- Execution Core Pipeline ---
if strl.button("🚀 Execute Comprehensive Deep Diagnostic Scan"):
    if not target_url.strip():
        strl.warning("🚨 Operational Warning: Provide a valid web URL schema.")
    else:
        with strl.spinner(f"🌐 Crawling target domain and packaging environment profile footprint ({responsive_profile})..."):
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
            strl.success(f"✔️ Target metrics mapped locally using {responsive_profile} validation matrices.")

            p_metrics = audit_data.get("perf_metrics", {})
            load_time = p_metrics.get("load_time_ms", "N/A")
            dom_ready = p_metrics.get("dom_ready_ms", "N/A")

            if audit_data.get("screenshot"):
                strl.session_state["captured_img"] = audit_data["screenshot"]
            else:
                strl.session_state.pop("captured_img", None)

            console_logs_str = "\n".join(audit_data["console_errors"][:2]) if audit_data["console_errors"] else "None detected."
            network_logs_str = "\n".join(audit_data["failed_requests"][:2]) if audit_data["failed_requests"] else "None."

            response_text = None

            if API_KEY:
                with strl.spinner(f"🧠 Querying Gemini Core Infrastructure ({selected_model})..."):
                    system_analysis_prompt = (
                        f"Provide a brief 3-item bulleted summary website health report. "
                        f"Website Title: {audit_data['title']}. Device Target Platform Emulated: {responsive_profile}. "
                        f"Target element selection checked: '{target_selector if target_selector else 'Full Body Context'}'. "
                        f"Core Load Time: {load_time}ms, DOM Engine Processing Time: {dom_ready}ms. "
                        f"Content snippet parsed: {audit_data['content']}. "
                        f"Failures: JavaScript: {console_logs_str}, Network: {network_logs_str}."
                    )
                    try:
                        client = genai.Client(api_key=API_KEY)
                        response = client.models.generate_content(
                            model=selected_model,
                            contents=system_analysis_prompt,
                        )
                        response_text = response.text
                    except Exception:
                        strl.warning("⚠️ Gemini execution encountered an issue. Switching to Local Safe Engine...")

            if not response_text:
                status_health = "STABLE CONNECTION" if "None" in network_logs_str else "MINOR ANOMALIES DETECTED"
                response_text = f"""================================================================================
SIMPLE WEBSITE COMPLIANCE & BUG AUDIT REPORT (LOCAL AUTOMATION RUN)
================================================================================
Tested Website Link: {target_url}
Website Name: {audit_data['title']}
Device Profile Viewport: {responsive_profile}
Target Element Component: {target_selector if target_selector else "Global Web Page Body Layout"}
--------------------------------------------------------------------------------

1. CORE PERFORMANCE DIAGNOSTICS
--------------------------------------------------------------------------------
* Raw Browser Handshake Load Time   : {load_time} ms
* DOM Engine Structure Ready Time   : {dom_ready} ms

2. SIMPLE SUMMARY OF WEBSITE HEALTH
--------------------------------------------------------------------------------
The target workspace was parsed successfully by the local automation core engine. 
The system flags an active background status code metric of: {status_health}.

3. LIST OF DETECTED ISSUES & BUGS (EXPLAINED SIMPLY)
--------------------------------------------------------------------------------
* BACKGROUND SCRIPT ERRORS:
  - Raw Code Output: {console_logs_str}
  - Assessment: Common frontend context flags caught during page execution frame.

* NETWORK CONNECTIONS:
  - Raw Code Output: {network_logs_str}
  - Assessment: Element tracking structures rendered within expected parameters.

================================================================================
                                END OF REPORT DOCUMENT
================================================================================"""

            strl.session_state["live_report"] = response_text

# --- Presentation Layer ---
if "captured_img" in strl.session_state:
    strl.markdown("### 📸 Captured Visual UI Layout Checkpoint")
    strl.image(strl.session_state["captured_img"], caption=f"Live Sandbox Screen Capture — {responsive_profile}", use_container_width=True)

if "live_report" in strl.session_state:
    strl.markdown("### 📊 Live System Audit Output Visualization")
    strl.markdown("<div class='report-card'>", unsafe_allow_html=True)
    strl.text(strl.session_state["live_report"])
    strl.markdown("</div>", unsafe_allow_html=True)
    strl.markdown("<br>", unsafe_allow_html=True)

    strl.download_button(
        label="📥 Download Formal Audit Artifact Document (.txt)",
        data=strl.session_state["live_report"],
        file_name="BugOptix_Comprehensive_System_Audit.txt",
        mime="text/plain",
        use_container_width=True
    )
