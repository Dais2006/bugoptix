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

initialize_playwright_binaries()

from google import genai
from google.genai.errors import APIError
from playwright.async_api import async_playwright

# --- Deep Space Enterprise Theme Configuration ---
strl.set_page_config(
    page_title="BugOptix | Ultimate Enterprise QA Auditor",
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
    </style>
""", unsafe_allow_html=True)


# --- Fallback Resilient Scraping Engine ---
async def perform_deep_audit(url: str, depth: str, selector: str, profile: str) -> dict:
    results = {
        "success": False, "title": "Target Sandbox Domain", "content": "No visual content could be rendered.",
        "form_structures": [], "console_errors": [], "failed_requests": [], "error": "", "screenshot": None
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

            # Speed up loading processing by blocking heavy resources
            await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "font", "media"] else route.continue_())

            page.on("pageerror", lambda exc: results["console_errors"].append(f"JS Crash: {exc}"))
            page.on("requestfailed", lambda req: results["failed_requests"].append(f"Network Drop: {req.url}"))

            try:
                # Core navigation block with strict load restrictions bypassed
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(1500)
            except Exception as context_error:
                # CODE SOLUTION: If timeout occurs, print log warning and proceed to force parsing instead of crashing!
                results["console_errors"].append(f"Navigation warning caught (Handling via code pipeline bypass): {context_error}")

            # --- FORCED EXTRACTION PHASE (Runs even if network handshake timed out) ---
            try:
                results["title"] = await page.title() or "Target Portal Workspace"
                
                # Pull whatever elements exist in the page body structure
                form_elements = await page.evaluate("""() => {
                    const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
                    return inputs.map(el => ({
                        tagName: el.tagName.toLowerCase(),
                        type: el.type || 'text',
                        name: el.name || '',
                        id: el.id || '',
                        placeholder: el.placeholder || '',
                        maxlength: el.getAttribute('maxlength') || 'MISSING',
                        required: el.hasAttribute('required') ? 'YES' : 'NO'
                    }));
                }""")
                results["form_structures"] = form_elements

                body_element = page.locator("body")
                raw_text = await body_element.inner_text()
                results["content"] = " ".join(raw_text.split())[:3000]
                
                try:
                    results["screenshot"] = await page.screenshot(full_page=False, timeout=3000)
                except Exception:
                    pass
                
                results["success"] = True
            except Exception as extraction_err:
                results["error"] = f"Extraction completely blocked by hosting provider firewall rules: {extraction_err}"
                results["success"] = False

            await browser.close()
    except Exception as e:
        results["error"] = str(e)
        results["success"] = False
    return results


# --- Layout Interface Matrix ---
strl.title("🛡️ BugOptix AI — Deep Diagnostic Suite")
strl.markdown("### Automated Web Application QA & Technical Compliance Engine")
strl.markdown("---")

strl.sidebar.header("🔑 Authentication Setup")
ui_key_input = strl.sidebar.text_input("Enter Gemini API Key:", type="password")
selected_model = strl.sidebar.selectbox("AI Brain Model Setup", ["gemini-2.5-flash", "gemini-2.5-pro"])

API_KEY = ui_key_input.strip() if ui_key_input.strip() else os.environ.get("GEMINI_API_KEY", "")

col1, col2 = strl.columns([2, 1])
with col1:
    target_url = strl.text_input("Target Application URL Endpoint:", value="https://zgcollege.wakinedu.com/erp/admission")
with col2:
    scan_depth = strl.selectbox("Operational Audit Depth", ["Surface UI Content Validation", "Full Matrix Diagnostic Sweep"])

col3, col4 = strl.columns([2, 1])
with col3:
    target_selector = strl.text_input("Target Element Scope Selector (Optional):", placeholder="e.g. #login-form")
with col4:
    responsive_profile = strl.selectbox("Device Emulation Viewport", ["Desktop (1080p)", "ios", "android"])

if strl.button("🚀 Execute Comprehensive Deep Diagnostic Scan"):
    if not target_url.strip():
        strl.warning("🚨 Operational Warning: Provide a valid web URL schema.")
    else:
        with strl.spinner("🌐 Bypassing page assets and executing extraction routines..."):
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
            strl.success("✔️ UI Components and Form Fields successfully mapped to local memory matrix.")

            if audit_data.get("screenshot"):
                strl.session_state["captured_img"] = audit_data["screenshot"]

            console_logs_str = "\n".join(audit_data["console_errors"][:3]) if audit_data["console_errors"] else "None."
            network_logs_str = "\n".join(audit_data["failed_requests"][:3]) if audit_data["failed_requests"] else "None."
            
            form_summary = ""
            for field in audit_data.get("form_structures", []):
                form_summary += f"- Tag: {field['tagName']}, Type: {field['type']}, Name: {field['name']}, MaxLength: {field['maxlength']}, Required: {field['required']}\n"

            response_text = None

            if API_KEY:
                with strl.spinner("🧠 Generating Smart QA Analysis Summary Report..."):
                    system_analysis_prompt = (
                        f"You are a Senior QA Automation Engineer. Audit this website data for minor/subtle bugs:\n\n"
                        f"URL Tested: {target_url}\n"
                        f"Page Title: {audit_data['title']}\n"
                        f"Extracted Form Input Fields:\n{form_summary if form_summary else 'No forms discovered.'}\n\n"
                        f"Visible Content Snippet:\n{audit_data['content']}\n\n"
                        f"Background Errors:\n- JS: {console_logs_str}\n- Network: {network_logs_str}\n\n"
                        f"INSTRUCTIONS:\n"
                        f"Generate an Audit Report highlighting these specific checks:\n"
                        f"1. FORM LIMITATION BUGS: Look closely at input fields. If fields like mobile, phone, name or text lack a MaxLength property, call it out as a bug.\n"
                        f"2. TYPOS & SPELLING: Identify any broken language or cut-off text strings.\n"
                        f"3. UNEXPECTED ERRORS: Review background asset warnings or drops simply."
                    )
                    try:
                        client = genai.Client(api_key=API_KEY)
                        response = client.models.generate_content(model=selected_model, contents=system_analysis_prompt)
                        response_text = response.text
                    except Exception as e:
                        strl.warning(f"Gemini processing bypass note: {e}")

            if not response_text:
                response_text = f"Analysis completed.\n\nForm Parameters Scraped:\n{form_summary if form_summary else 'None.'}\n\nNetwork Traces:\n{network_logs_str}"

            strl.session_state["live_report"] = response_text

# --- Presentation Layer ---
if "captured_img" in strl.session_state:
    strl.markdown("### 📸 Captured Visual UI Layout Checkpoint")
    strl.image(strl.session_state["captured_img"], use_container_width=True)

if "live_report" in strl.session_state:
    strl.markdown("### 📊 Live System Audit Output Visualization")
    strl.markdown("<div class='report-card'>", unsafe_allow_html=True)
    strl.text(strl.session_state["live_report"])
    strl.markdown("</div>", unsafe_allow_html=True)
