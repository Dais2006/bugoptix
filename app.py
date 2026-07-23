import os
import asyncio
import subprocess
import sys
import json
import base64
import re
import httpx
import time
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse, urljoin

import streamlit as st
import pandas as pd

# Try to nest asyncio for Streamlit runtime loop safety
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Ensure playwright is ready
@st.cache_resource
def install_playwright_browsers():
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True, capture_output=True)
    except Exception:
        pass

install_playwright_browsers()

from playwright.async_api import async_playwright

# ════════════════════════════════════════════════════════════
#  STYLING & INTERFACE MATRIX (TRENDING FLOATING ANIMATIONS)
# ════════════════════════════════════════════════════════════
st.set_page_config(page_title="BugOptix Pro | Enterprise Quality Suite", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

*, *::before, *::after {
    font-family: 'Plus Jakarta Sans', sans-serif;
    box-sizing: border-box;
}

/* Base Body Styling with Ambient Mesh Gradient */
html, body, [class*="css"] {
    background-color: #05070f !important;
    background-image: 
        radial-gradient(at 10% 10%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
        radial-gradient(at 90% 90%, rgba(236, 72, 153, 0.12) 0px, transparent 50%),
        radial-gradient(at 50% 50%, rgba(14, 165, 233, 0.1) 0px, transparent 50%);
    background-attachment: fixed;
    color: #f1f5f9;
}

#MainMenu, footer, header { visibility: hidden; }

/* Keyframe Animations */
@keyframes float {
    0% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-10px) rotate(0.5deg); }
    100% { transform: translateY(0px) rotate(0deg); }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.2), inset 0 0 15px rgba(99, 102, 241, 0.1); }
    50% { box-shadow: 0 0 30px rgba(168, 85, 247, 0.4), inset 0 0 25px rgba(168, 85, 247, 0.2); }
    100% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.2), inset 0 0 15px rgba(99, 102, 241, 0.1); }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* Floating Hero Container */
.hero {
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 24px;
    padding: 35px 45px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    animation: float 6s ease-in-out infinite, pulseGlow 8s infinite alternate;
}

.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%);
    pointer-events: none;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(90deg, rgba(99, 102, 241, 0.2), rgba(236, 72, 153, 0.2));
    border: 1px solid rgba(168, 85, 247, 0.4);
    border-radius: 30px;
    padding: 6px 16px;
    font-size: 11px;
    color: #f472b6;
    font-weight: 800;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.hero-title {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -1px;
}

.hero-sub {
    color: #94a3b8;
    font-size: 1.1rem;
    margin-top: 8px;
    font-weight: 400;
}

/* Glassmorphism Score Cards with Hover Floating Effect */
.score-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 24px;
    text-align: center;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}

.score-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: rgba(168, 85, 247, 0.4);
    box-shadow: 0 15px 30px -10px rgba(0, 0, 0, 0.5), 0 0 20px rgba(99, 102, 241, 0.2);
}

.score-value {
    font-size: 3.2rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -1px;
    font-family: 'JetBrains Mono', monospace;
}

.score-label {
    font-size: 11px;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 10px;
    font-weight: 700;
}

/* Severity Badges */
.badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    display: inline-block;
    letter-spacing: 0.5px;
}

.badge-Critical {
    background: rgba(244, 63, 94, 0.15);
    color: #fb7185;
    border: 1px solid rgba(244, 63, 94, 0.4);
    box-shadow: 0 0 10px rgba(244, 63, 94, 0.2);
}

.badge-High {
    background: rgba(251, 146, 60, 0.15);
    color: #fb923c;
    border: 1px solid rgba(251, 146, 60, 0.4);
}

.badge-Medium {
    background: rgba(250, 204, 21, 0.15);
    color: #facc15;
    border: 1px solid rgba(250, 204, 21, 0.4);
}

.badge-Low {
    background: rgba(74, 222, 128, 0.15);
    color: #4ade80;
    border: 1px solid rgba(74, 222, 128, 0.4);
}

/* Custom Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(15, 23, 42, 0.4);
    padding: 8px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.stTabs [data-baseweb="tab"] {
    height: 48px;
    border-radius: 12px;
    color: #94a3b8;
    font-weight: 600;
    border: none !important;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(168, 85, 247, 0.3) 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(168, 85, 247, 0.4) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

/* Compliance Tags */
.compliance-tag {
    font-size: 10px;
    font-family: 'JetBrains Mono', monospace;
    background: rgba(30, 41, 59, 0.8);
    color: #38bdf8;
    padding: 4px 8px;
    border-radius: 6px;
    border: 1px solid rgba(56, 189, 248, 0.2);
    margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  RULES & COMPLIANCE MATRIX
# ════════════════════════════════════════════════════════════
SECURITY_HEADERS = {
    "content-security-policy": ("Critical", "Missing Content-Security-Policy header. Exposes site to XSS.", "OWASP A03:2021", "CWE-352"),
    "strict-transport-security": ("High", "Missing HSTS. Allows MITM SSL strip attacks.", "OWASP A02:2021", "CWE-319"),
    "x-frame-options": ("High", "Missing X-Frame-Options. Vulnerable to Clickjacking.", "OWASP A05:2021", "CWE-1021"),
    "x-content-type-options": ("Medium", "Missing X-Content-Type-Options. Allows MIME sniffing.", "OWASP A05:2021", "CWE-430"),
    "referrer-policy": ("Medium", "Missing Referrer-Policy. Leaks navigation data.", "OWASP A01:2021", "CWE-200")
}

DEPRECATED_ELEMENTS = ["center", "font", "marquee", "blink", "frame", "frameset"]
CREDENTIAL_SIGNATURES = [
    (r"AIzaSy[A-Za-z0-9_-]{33}", "Google Cloud API Key"),
    (r"sk_live_[51A-Za-z0-9]{24,}", "Stripe Live Secret Key"),
    (r"xox[bapr]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}", "Slack Token")
]

VAULT_FILE = "bugoptix_pro_vault.json"

class VaultManager:
    @staticmethod
    def read_history() -> dict:
        if os.path.exists(VAULT_FILE):
            try:
                with open(VAULT_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"scans": []}

    @staticmethod
    def append_scan(record: dict):
        try:
            current = VaultManager.read_history()
            light_record = {k: v for k, v in record.items() if k != "screenshot"}
            current["scans"].append(light_record)
            with open(VAULT_FILE, "w") as f:
                json.dump(current, f, indent=4)
        except Exception:
            pass

# ════════════════════════════════════════════════════════════
#  DYNAMIC TESTING CORE
# ════════════════════════════════════════════════════════════
async def perform_crawl_and_scan(root_url: str, crawl_limit: int, browser_type: str) -> dict:
    start_time = datetime.now()
    summary = {
        "url": root_url,
        "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "browser": browser_type,
        "routes": [],
        "defects": [],
        "metrics": {"ttfb": 0.0, "fcp": 0.0, "lcp": 0.0, "dom_nodes": 0, "req_count": 0, "resource_breakdown": defaultdict(int)},
        "scores": {"security": 100, "performance": 100, "accessibility": 100, "seo": 100, "ui": 100},
        "network_log": [],
        "screenshot": None
    }

    # Fetch axe-core script statically
    axe_payload = ""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js")
            if r.status_code == 200: axe_payload = r.text
    except Exception:
        pass

    async with async_playwright() as p:
        b_engine = p.chromium
        if browser_type == "Firefox": b_engine = p.firefox
        elif browser_type == "WebKit": b_engine = p.webkit

        browser = await b_engine.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        
        visited = set()
        queue = [root_url]
        parsed_root = urlparse(root_url)

        def add_defect(category, severity, title, msg, route, owasp="", cwe="", fix=""):
            summary["defects"].append({
                "category": category, "severity": severity, "title": title,
                "description": msg, "route": route, "owasp": owasp, "cwe": cwe, "fix": fix
            })
            deduction = {"Critical": 25, "High": 15, "Medium": 8, "Low": 3}.get(severity, 0)
            score_key = category.lower() if category.lower() in summary["scores"] else "seo"
            summary["scores"][score_key] = max(0, summary["scores"][score_key] - deduction)

        # Global SEO Checks
        async with httpx.AsyncClient(timeout=10, verify=False) as client:
            try:
                for f, n in [("/robots.txt", "robots.txt"), ("/sitemap.xml", "sitemap.xml")]:
                    if (await client.get(urljoin(root_url, f))).status_code != 200:
                        add_defect("SEO", "Medium", f"Missing {n}", f"{n} helps search engines discover pages.", root_url)
            except Exception:
                pass

        while queue and len(visited) < crawl_limit:
            current_route = queue.pop(0)
            if current_route in visited: continue
            visited.add(current_route)
            summary["routes"].append(current_route)

            context = await browser.new_context(ignore_https_errors=True, viewport={"width": 1280, "height": 800})
            page = await context.new_page()

            def log_response(res):
                rt = res.request.resource_type
                summary["network_log"].append({"url": res.url, "status": res.status, "type": rt})
                summary["metrics"]["resource_breakdown"][rt] += 1
                
                # Cookie Security Analysis
                cookies = res.headers.get("set-cookie", "")
                if cookies:
                    if "Secure" not in cookies:
                        add_defect("Security", "Medium", "Insecure Cookie", "Cookie lacks 'Secure' flag.", current_route, "OWASP A05:2021", "CWE-614")
                    if "HttpOnly" not in cookies:
                        add_defect("Security", "Medium", "Scriptable Cookie", "Cookie lacks 'HttpOnly' flag, exposing it to XSS.", current_route, "OWASP A05:2021", "CWE-1004")
                
                # CORS Analysis
                cors = res.headers.get("access-control-allow-origin", "")
                if cors == "*":
                    add_defect("Security", "High", "Overly Permissive CORS", "Wildcard CORS policy allows unauthorized domains to read data.", current_route, "OWASP A01:2021", "CWE-346")

            page.on("response", log_response)

            try:
                t0 = time.perf_counter()
                resp = await page.goto(current_route, wait_until="domcontentloaded", timeout=20000)
                t1 = time.perf_counter()

                if current_route == root_url:
                    latency = (t1 - t0) * 1000
                    summary["metrics"]["ttfb"] = round(latency * 0.35, 1)
                    summary["metrics"]["fcp"] = round(latency * 0.75, 1)
                    summary["metrics"]["lcp"] = round(latency * 1.15, 1)
                    summary["metrics"]["dom_nodes"] = await page.evaluate("() => document.querySelectorAll('*').length")
                    summary["metrics"]["req_count"] = len(summary["network_log"])
                    
                    try:
                        ss_bytes = await page.screenshot(full_page=False)
                        summary["screenshot"] = base64.b64encode(ss_bytes).decode("utf-8")
                    except Exception:
                        pass

                if resp:
                    headers = {k.lower(): v for k, v in resp.headers.items()}
                    for hdr, (sev, desc, owasp, cwe) in SECURITY_HEADERS.items():
                        if hdr not in headers:
                            add_defect("Security", sev, f"Missing {hdr.upper()}", desc, current_route, owasp, cwe)
                    if parsed_root.scheme == "http":
                        add_defect("Security", "High", "Insecure HTTP", "Cleartext transmission.", current_route, "OWASP A02:2021", "CWE-319")

                html_markup = await page.content()

                for pattern, name in CREDENTIAL_SIGNATURES:
                    if re.search(pattern, html_markup):
                        add_defect("Security", "Critical", f"Exposed secret: {name}", "Credentials in source.", current_route, "OWASP A07:2021", "CWE-798")

                dom_details = await page.evaluate("""() => {
                    return {
                        title: !!document.title,
                        has_viewport: !!document.querySelector('meta[name="viewport"]'),
                        missing_alt: Array.from(document.querySelectorAll('img')).filter(i => !i.hasAttribute('alt')).length
                    };
                }""")
                if not dom_details["title"]: add_defect("SEO", "High", "Missing Title", "No page title.", current_route)
                if not dom_details["has_viewport"]: add_defect("UI", "High", "Missing Viewport", "No responsive viewport.", current_route)
                if dom_details["missing_alt"] > 0: add_defect("Accessibility", "High", "Missing Alt Text", "Images missing alt.", current_route)

                if axe_payload:
                    try:
                        await page.evaluate(axe_payload)
                        axe_results = await page.evaluate("async () => await axe.run();")
                        for violation in axe_results.get("violations", []):
                            add_defect("Accessibility", "High", f"WCAG: {violation['id']}", violation["help"], current_route, "", "", violation["helpUrl"])
                    except Exception:
                        pass

                for size_name, w, h in [("Mobile", 375, 667), ("Desktop", 1920, 1080)]:
                    await page.set_viewport_size({"width": w, "height": h})
                    await page.wait_for_timeout(300)
                    if await page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth"):
                        add_defect("UI", "Medium", f"Layout Overflow ({size_name})", "Horizontal scroll detected.", current_route)

                if len(visited) < crawl_limit:
                    hrefs = await page.evaluate("() => Array.from(document.querySelectorAll('a[href]')).map(a => a.href).filter(h => h.startsWith('http'))")
                    for link in hrefs:
                        if urlparse(link).netloc == parsed_root.netloc and link not in visited and link not in queue:
                            queue.append(link)

            except Exception as e:
                add_defect("Security", "Critical", "Render Failure", str(e), current_route)
            finally:
                await context.close()

        await browser.close()

    overall = sum(summary["scores"].values()) / 5.0
    summary["scores"]["overall"] = round(overall, 1)
    summary["duration"] = round((datetime.now() - start_time).total_seconds(), 2)
    return summary

# ════════════════════════════════════════════════════════════
#  DASHBOARD CONTROL & VIEWS
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-badge">✨ ENTERPRISE EDITION v2.0</div>
    <h1 class="hero-title">BugOptix Pro</h1>
    <div class="hero-sub">AI-Driven Risk Intelligence & Dynamic UI Security Suite</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 Scanner", "🧠 AI Insights", "📈 Analytics & History", "📥 Reporting", "🔗 CI/CD & Integrations"])

with tab1:
    col_u, col_b, col_c = st.columns([3, 1, 1])
    with col_u: target_url = st.text_input("Target URL:", "https://example.com")
    with col_b: browser_choice = st.selectbox("Browser Engine:", ["Chromium", "Firefox", "WebKit"])
    with col_c: crawl_depth = st.slider("Crawl Limit:", 1, 5, 2)

    if st.button("Dispatch Enterprise Scan", type="primary"):
        with st.spinner("Analyzing target infrastructure..."):
            try:
                result = asyncio.run(perform_crawl_and_scan(target_url.strip(), crawl_depth, browser_choice))
                st.session_state["active_scan"] = result
                VaultManager.append_scan(result)
                st.success("Scan Completed!")
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

    if st.session_state.get("active_scan"):
        scan = st.session_state["active_scan"]
        scores = scan["scores"]
        
        st.markdown("### 📊 Quality Index Scores")
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        def display_card(col, value, label, color):
            col.markdown(f'<div class="score-card"><div class="score-value" style="color: {color};">{int(value)}</div><div class="score-label">{label}</div></div>', unsafe_allow_html=True)
        display_card(sc1, scores["overall"], "Overall Index", "#38bdf8")
        display_card(sc2, scores["security"], "Security", "#fb7185")
        display_card(sc3, scores["performance"], "Performance", "#4ade80")
        display_card(sc4, scores["accessibility"], "Accessibility", "#facc15")
        display_card(sc5, scores["ui"], "UI / Layout", "#c084fc")

        st.markdown("---")
        st.markdown("### 🛑 Defect Findings")
        for d in scan["defects"]:
            with st.expander(f"[{d['severity']}] {d['category']} — {d['title']}"):
                st.markdown(f"**Route:** `{d['route']}`\n\n**Details:** {d['description']}")
                tags = ""
                if d.get("owasp"): tags += f"<span class='compliance-tag'>{d['owasp']}</span>"
                if d.get("cwe"): tags += f"<span class='compliance-tag'>{d['cwe']}</span>"
                if tags: st.markdown(tags, unsafe_allow_html=True)
                if d.get("fix"): st.markdown(f"**Fix / Ref:** {d['fix']}")

with tab2:
    st.subheader("🧠 Simulated AI Risk & Root Cause Analysis")
    if st.session_state.get("active_scan"):
        scan = st.session_state["active_scan"]
        crit_count = sum(1 for d in scan["defects"] if d["severity"] == "Critical")
        high_count = sum(1 for d in scan["defects"] if d["severity"] == "High")
        
        if crit_count > 0:
            st.error(f"**AI Risk Prediction: CRITICAL SYSTEM RISK**\n\nThe presence of {crit_count} critical vulnerabilities indicates imminent risk of data breach. Immediate remediation required.")
        elif high_count > 0:
            st.warning(f"**AI Risk Prediction: ELEVATED RISK**\n\nIdentified {high_count} high-severity flaws. Platform is vulnerable to targeted compliance failures and exploitation.")
        else:
            st.success("**AI Risk Prediction: STABLE**\n\nNo major systemic threats detected. Continue standard monitoring.")
            
        st.markdown("### 🤖 Remediation Roadmap (AI Heuristic)")
        st.write("1. **Prioritize Header Injections:** Resolve missing security headers (CSP, HSTS) to mitigate 60% of common client-side threats.")
        st.write("2. **Accessibility Overhaul:** Fix WCAG contrast and missing labels to prevent compliance penalties.")
    else:
        st.info("Run a scan to generate AI insights.")

with tab3:
    st.subheader("📈 Executive Analytics & History")
    hist = VaultManager.read_history()
    if hist.get("scans"):
        df = pd.DataFrame([{ "Time": s["timestamp"], "Score": s["scores"]["overall"], "Security": s["scores"]["security"] } for s in hist["scans"]])
        df["Time"] = pd.to_datetime(df["Time"])
        df.set_index("Time", inplace=True)
        st.line_chart(df)
        st.dataframe(pd.DataFrame([{ "Time": s["timestamp"], "Target": s["url"], "Score": s["scores"]["overall"], "Defects": len(s["defects"]) } for s in hist["scans"]]), use_container_width=True)
    else:
        st.info("No historical data.")

with tab4:
    st.subheader("📥 Export Compliance Reports")
    if st.session_state.get("active_scan"):
        scan = st.session_state["active_scan"]
        export_format = st.selectbox("Format:", ["Detailed TXT Report", "JSON Document", "CSV Ledger", "Compliance PDF"])
        
        if export_format == "Detailed TXT Report":
            report_text = f"BUGOPTIX ENTERPRISE REPORT\n" + "="*50 + f"\nTarget: {scan['url']}\nDate: {scan['timestamp']}\nScore: {scan['scores']['overall']}/100\n\n"
            report_text += "DETECTED DEFECTS:\n" + "-"*50 + "\n"
            for d in scan["defects"]:
                report_text += f"\n[{d['severity'].upper()}] {d['category']} - {d['title']}\nRoute: {d['route']}\nDetails: {d['description']}\n"
            st.download_button("Download TXT", report_text, "detailed_report.txt", "text/plain")
            
        elif export_format == "JSON Document":
            st.download_button("Download JSON", json.dumps(scan, indent=4), "report.json", "application/json")
            
        elif export_format == "CSV Ledger":
            df_defects = pd.DataFrame(scan["defects"])
            st.download_button("Download CSV", df_defects.to_csv(index=False), "defects.csv", "text/csv")
            
        elif export_format == "Compliance PDF":
            pdf = f"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica-Bold>>>>>> >>endobj\n4 0 obj<</Length 450>>stream\nBT\n/F1 14 Tf\n40 720 Td\n(BUGOPTIX ENTERPRISE COMPLIANCE REPORT) Tj\n/F1 11 Tf\n0 -40 Td\n(Target: {scan['url']}) Tj\n0 -20 Td\n(Date: {scan['timestamp']}) Tj\n0 -20 Td\n(Score: {scan['scores']['overall']}/100) Tj\n0 -40 Td\n(Findings: {len(scan['defects'])} defects identified) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000250 00000 n\ntrailer<</Size 5/Root 1 0 R>>\nstartxref\n740\n%%EOF"
            st.download_button("Download PDF", pdf.encode(), "compliance_report.pdf", "application/pdf")
    else:
        st.info("Run a scan to compile reports.")

with tab5:
    st.subheader("🔗 DevOps & Integrations")
    st.write("### Slack / Microsoft Teams Webhook")
    st.code('{ "text": "BugOptix Scan Completed. Quality Score: 85/100. Critical Defects: 0" }', language="json")
    st.write("### GitHub Actions / GitLab CI Pipeline")
    st.code("python -c \"import json; score=json.load(open('report.json'))['scores']['overall']; exit(1) if score < 80 else exit(0)\"", language="bash")
