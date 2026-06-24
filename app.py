import os
import time
import asyncio
import streamlit as strl
from google import genai
from google.genai.errors import APIError
from playwright.async_api import async_playwright

# Deep Space Enterprise Theme Configuration
strl.set_page_config(
    page_title="BugOptix | Ultimate Enterprise QA Auditor",
    page_icon="🛡️",
    layout="wide"
)

# Custom Corporate CSS Injection for Professional Presentation
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
    div.stDownloadButton > button:hover {
        background-color: #30363d !important;
        border-color: #8b949e !important;
    }
    </style>
""", unsafe_allow_html=True)


# Deep Audit Web Scraper Engine (With Active Pipeline Error Interception)
async def perform_deep_audit(url: str) -> dict:
    results = {
        "success": False, "title": "Target Sandbox Domain", "content": "No visual content could be rendered.",
        "console_errors": [], "failed_requests": [], "error": ""
    }
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # LAYER 2 Listener: Catch background JavaScript Console Crashes
            page.on("pageerror", lambda exc: results["console_errors"].append(f"JS Crash Reference: {exc}"))
            page.on("console", lambda msg: results["console_errors"].append(
                f"Console Script Error: {msg.text}") if msg.type == "error" else None)

            # LAYER 3 Listener: Catch Network Request & API Gateway Failures
            page.on("requestfailed", lambda req: results["failed_requests"].append(f"Network Drop/Timeout: {req.url}"))
            page.on("response", lambda res: results["failed_requests"].append(
                f"API HTTP Error {res.status}: {res.url}") if res.status >= 400 else None)

            try:
                await page.goto(url, wait_until="load", timeout=20000)
                await page.wait_for_timeout(2000)

                results["title"] = await page.title()
                body_element = page.locator("body")
                results["content"] = await body_element.inner_text()
                results["success"] = True
            except Exception as nav_err:
                results["failed_requests"].append(f"CRITICAL PIPELINE DISRUPTION: {str(nav_err)}")
                results["error"] = str(nav_err)
                results["success"] = True

            await browser.close()
    except Exception as e:
        results["error"] = str(e)
    return results


# --- App Header Section ---
strl.title("🛡️ BugOptix AI — Deep Diagnostic Suite")
strl.markdown("### Automated Web Application QA & Technical Compliance Engine")
strl.markdown("---")

# --- Interactive Sidebar for Credentials ---
strl.sidebar.header("🔑 Authentication Setup")
ui_key_input = strl.sidebar.text_input("Enter Gemini API Key:", type="password",
                                       help="Get a free key from https://aistudio.google.com/")

# Resolve key prioritizing the UI input box
API_KEY = ui_key_input.strip() if ui_key_input.strip() else os.environ.get("GEMINI_API_KEY", "")

# --- Interface Layout Columns ---
col1, col2 = strl.columns([2, 1])
with col1:
    target_url = strl.text_input("Target Application URL Endpoint:", placeholder="https://your-student-app.com")
with col2:
    scan_depth = strl.selectbox("Operational Audit Depth",
                                ["Full Matrix Diagnostic Sweep", "Surface UI Content Validation"])

strl.markdown("<br>", unsafe_allow_html=True)

# --- Primary Analysis Pipeline ---
if strl.button("🚀 Execute Comprehensive Deep Diagnostic Scan"):
    if not API_KEY:
        strl.error(
            "🔑 Authentication Missing: Please paste your Gemini API Key into the password field on the left sidebar panel.")
    elif not target_url.strip():
        strl.warning("🚨 Operational Warning: Target routing parameter missing. Provide a valid web URL.")
    elif not target_url.startswith(("http://", "https://")):
        strl.error(
            "❌ Protocol Validation Refused: Target URL must explicitly begin with standard http:// or https:// schemas.")
    else:
        with strl.spinner("🌐 Provisioning sandboxed automation browser and hooking diagnostic listeners..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                audit_data = loop.run_until_complete(perform_deep_audit(target_url.strip()))
            except Exception as loop_err:
                audit_data = {"success": False, "error": str(loop_err)}
            finally:
                loop.close()

        if not audit_data.get("success"):
            strl.error(f"❌ Connection Pipeline Terminated: Handshake dropped. Details: {audit_data.get('error')}")
        else:
            strl.success("✔️ Target analysis matrices successfully mapped. Analyzing structural pathways...")

            with strl.spinner("🧠 Compiling data matrices. Querying Gemini Core models with traffic retry logic..."):

                console_logs_str = "\n".join(audit_data["console_errors"]) if audit_data[
                    "console_errors"] else "None detected."
                network_logs_str = "\n".join(audit_data["failed_requests"]) if audit_data[
                    "failed_requests"] else "All network requests returned status 200 OK."

                system_analysis_prompt = f"""
                You are a Lead QA Automation Engineer and Senior Core Infrastructure System Architect. 
                Perform a rigorous web evaluation across ALL vectors: UI plain text, background browser console traces, and raw network API logs.

                Target App Context URL: {target_url}
                Application Manifest Title: {audit_data['title']}

                [DIAGNOSTIC LAYER 1: VISUAL UI TEXT CONTENT]
                ---
                {audit_data['content']}
                ---

                [DIAGNOSTIC LAYER 2: BACKGROUND JAVASCRIPT CONSOLE ERRORS]
                ---
                {console_logs_str}
                ---

                [DIAGNOSTIC LAYER 3: FAILED NETWORK API REQUESTS]
                ---
                {network_logs_str}
                ---

                Generate a high-grade professional text engineering report using this EXACT plain text layout:

                ================================================================================
                                ENTERPRISE SOFTWARE QUALITY ASSURANCE AUDIT REPORT
                ================================================================================
                Generated Via: BugOptix AI Deep Suite Engine
                Target Environment URL: {target_url}
                Document Title Context: {audit_data['title']}
                --------------------------------------------------------------------------------

                1. EXECUTIVE SUMMARY & SYSTEM INTEGRITY OVERVIEW
                --------------------------------------------------------------------------------
                [Provide a comprehensive structural evaluation of the target interface status based on all 3 diagnostic layers]

                2. TOTAL COMPLIANCE MATRIX & ALL IDENTIFIED CRASHES/ERRORS
                --------------------------------------------------------------------------------
                [List every single error found across UI, Console, and Network paths. If none are present at all, print "NO CRITICAL SYSTEM ERRORS DETECTED"]

                * ISSUE ID: BUG-001
                  - Critical Level: [High/Medium/Low]
                  - Source Layer: [UI Text / Browser Console / Network Request]
                  - Error Signature: [The string error message, script line, or failing URL endpoint]
                  - Observed Flaw & Behaviour: [What failed and why it behaves this way]
                  - Strategic Mitigation Steps: [Clear, step-by-step developer remediation instructions]

                ================================================================================
                                        END OF VERIFICATION REPORT DOCUMENT
                ================================================================================
                """

                # --- Advanced Traffic Congestion (503 Bypass) Handler ---
                models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
                response_text = None
                execution_error = None

                client = genai.Client(api_key=API_KEY)

                for selected_model in models_to_try:
                    retries = 3
                    delay = 2  # Starting pause threshold in seconds

                    for attempt in range(retries):
                        try:
                            response = client.models.generate_content(
                                model=selected_model,
                                contents=system_analysis_prompt,
                            )
                            response_text = response.text
                            break  # Success! Break out of the retry loop
                        except APIError as api_err:
                            execution_error = api_err
                            if api_err.code == 503:
                                # High demand flag hit. Back off and wait before retrying.
                                time.sleep(delay)
                                delay *= 2  # Exponentially step up delay timeline
                            else:
                                break
                        except Exception as e:
                            execution_error = e
                            break

                    if response_text:
                        break  # Break out of the model selection loop if we got a response!

                if response_text:
                    strl.session_state["live_report"] = response_text
                else:
                    strl.error(
                        f"🛡️ Processing Core Exception (Traffic/Overload Error): The servers are currently completely maxed out across backup networks. System Details: {str(execution_error)}. Please hit the scan button again in a moment!")

# --- Presentation & Document Download Framework ---
if "live_report" in strl.session_state:
    strl.markdown("### 📊 Live System Audit Output Visualization")
    strl.markdown("<div class='report-card'>", unsafe_allow_html=True)
    strl.text(strl.session_state["live_report"])
    strl.markdown("</div>", unsafe_allow_html=True)

    strl.markdown("<br>", unsafe_allow_html=True)

    strl.download_button(
        label="📥 Download Formal Audit Artifact Document (.txt)",
        data=strl.session_state["live_report"],
        file_name="BugOptix_Deep_System_Audit.txt",
        mime="text/plain",
        use_container_width=True
    )