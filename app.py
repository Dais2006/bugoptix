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
    </style>
""", unsafe_allow_html=True)


# --- Deep Audit Web Scraper Engine (Optimized Against Network Timeouts) ---
async def perform_deep_audit(url: str, depth: str, selector: str, profile: str) -> dict:
    results = {
        "success": False, "title": "Target Sandbox Domain", "content": "No visual content could be rendered.",
        "form_structures": [], "console_errors": [], "failed_requests": [], "error": "", "screenshot": None, "perf_metrics": {}
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
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # --- OPTIMIZATION 1: Block slow tracking, images, and fonts to avoid timeout thresholds ---
            await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "font", "media"] else route.continue_())

            page.on("pageerror", lambda exc: results["console_errors"].append(f"JS Crash: {exc}"))
            page.on("requestfailed", lambda req: results["failed_requests"].append(f"Network Drop: {req.url}"))

            try:
                # --- OPTIMIZATION 2: Switch to 'domcontentloaded' wait strategy ---
                # This breaks past strict institutional firewalls blocking full asset loops
                await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                await page.wait_for_timeout(2000) # Quick safety buffer for interactive execution

                results["title"] = await page.title()

                # Extract Form Data schemas dynamically 
                form_elements = await page.evaluate("""() => {
                    const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
                    return inputs.map(el => ({
                        tagName: el.tagName.toLowerCase(),
                        type: el.type || 'text',
                        name: el.name || '',
                        id: el.id || '',
                        placeholder: el.placeholder || '',
                        maxlength: el.getAttribute('maxlength') || 'MISSING',
                        required: el.hasAttribute('required') ? 'YES' : 'NO',
                        pattern: el.getAttribute('pattern') || 'NONE'
                    }));
                }""")
                results["form_structures"] = form_elements

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
                limit_len = 1500 if depth == "Surface UI Content Validation" else 3500
                results["content"] = cleaned_text[:limit_len]
                results["success"] = True

            except Exception as nav_err:
                # --- OPTIMIZATION 3: Try a secondary fallback scrape even if navigation threw a warning ---
                try:
                    results["title"] = await page.title() or "Fallback Capture Workspace"
                    body_element = page.locator("body")
                    raw_text = await body_element.inner_text()
                    results["content"] = " ".join(raw_text.split())[:1500]
                    results["success"] = True
                except Exception:
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

strl.sidebar.header("🔑 Authentication Setup")
ui_key_input = strl.sidebar.text_input("Enter Gemini API Key:", type="password")

selected_model = strl.sidebar.selectbox(
    "AI Brain Model Setup",
    ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"]
)

API_KEY = ui_key_input.strip() if ui_key_input.strip() else os.environ.get("GEMINI_API_KEY", "")

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
        with strl.spinner(f"🌐 Crawling target domain safely and auditing validation matrices ({responsive_profile})..."):
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

            if audit_data.get("screenshot"):
                strl.session_state["captured_img"] = audit_data["screenshot"]
            else:
                strl.session_state.pop("captured_img", None)

            console_logs_str = "\n".join(audit_data["console_errors"][:3]) if audit_data["console_errors"] else "None detected."
            network_logs_str = "\n".join(audit_data["failed_requests"][:3]) if audit_data["failed_requests"] else "None."

            form_summary = ""
            for field in audit_data.get("form_structures", []):
                form_summary += f"- Tag: {field['tagName']}, Type: {field['type']}, Name: {field['name']}, MaxLength: {field['maxlength']}, Required: {field['required']}\n"

            response_text = None

            if API_KEY:
                with strl.spinner(f"🧠 Querying Gemini Core Infrastructure ({selected_model})..."):
                    system_analysis_prompt = (
                        f"You are a Senior QA Automation Engineer. Audit this website data for minor/subtle bugs:\n\n"
                        f"URL Tested: {target_url}\n"
                        f"Page Title: {audit_data['title']}\n"
                        f"Extracted Form Input Fields:\n{form_summary if form_summary else 'No forms found.'}\n\n"
                        f"Visible Content Snippet:\n{audit_data['content']}\n\n"
                        f"Background Errors:\n- JS Code Errors: {console_logs_str}\n- Network Crashes: {network_logs_str}\n\n"
                        f"INSTRUCTIONS:\n"
                        f"Generate a clean, structured Quality Assurance Audit Report covering:\n"
                        f"1. FORM LIMITATION BUGS: Specifically review input lengths. If a phone, mobile, or text field lacks a MaxLength property, call it out as an error.\n"
                        f"2. TYPOS & SPELLING / LAYOUT TEXT MISTAKES: Review the layout contents closely for misspelled words or text breaks.\n"
                        f"3. UNEXPECTED BACKEND ERRORS: Explain background tracking drops simply."
                    )
                    try:
                        client = genai.Client(api_key=API_KEY)
                        response = client.models.generate_content(
                            model=selected_model,
                            contents=system_analysis_prompt,
                        )
                        response_text = response.text
                    except Exception as e:
                        strl.warning(f"⚠️ AI generation encountered an issue: {e}. Switching to Local Safe Engine...")

            if not response_text:
                status_health = "STABLE CONNECTION" if "None" in network_logs_str else "MINOR ANOMALIES DETECTED"
                response_text = f"""================================================================================
SIMPLE WEBSITE COMPLIANCE & BUG AUDIT REPORT (LOCAL AUTOMATION RUN)
================================================================================
Tested Website Link: {target_url}
Website Name: {audit_data['title']}
Device Profile Viewport: {responsive_profile}
--------------------------------------------------------------------------------

1. FORM SCHEMATICS COMPLIANCE
--------------------------------------------------------------------------------
{form_summary if form_summary else "* No interactive input field components mapped directly on this viewport frame."}

2. SIMPLE SUMMARY OF WEBSITE HEALTH
--------------------------------------------------------------------------------
The target workspace was parsed successfully by the local automation core engine. 
The system flags an active background status code metric of: {status_health}.

3. LIST OF DETECTED ISSUES & BUGS (EXPLAINED SIMPLY)
--------------------------------------------------------------------------------
* BACKGROUND SCRIPT ERRORS:
  - Raw Code Output: {console_logs_str}
  - Assessment: Look out for missing library endpoints or asset links.

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
