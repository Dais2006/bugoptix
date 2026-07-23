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
from urllib.parse import urlparse, urljoin, parse_qs

import streamlit as st
import pandas as pd

# Async runtime safety for Streamlit on Windows / Multi-thread loops
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

@st.cache_resource
def install_playwright_browsers():
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True, capture_output=True)
    except Exception:
        pass

install_playwright_browsers()

from playwright.async_api import async_playwright

# ════════════════════════════════════════════════════════════
#  NIKE-INSPIRED OBSIDIAN DESIGN SYSTEM
# ════════════════════════════════════════════════════════════
st.set_page_config(page_title="BugOptix Pro | Enterprise Auditor", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Plus+Jakarta+Sans:wght@300;400;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

*, *::before, *::after { 
    font-family: 'Plus Jakarta Sans', sans-serif !important; 
    box-sizing: border-box; 
}

html, body, [class*="css"] {
    background-color: #080808 !important;
    background-image: 
        radial-gradient(circle at 10% 20%, rgba(255, 70, 0, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(0, 230, 153, 0.05) 0%, transparent 40%);
    background-attachment: fixed;
    color: #f5f5f7;
}

#MainMenu, footer, header { visibility: hidden; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0c0c0e; }
::-webkit-scrollbar-thumb { background: #26262a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #ff4600; }

.hero-banner {
    background: linear-gradient(135deg, #111113 0%, #08080a 100%);
    border: 1px solid #1f1f24;
    border-radius: 20px;
    padding: 36px 44px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
}

.hero-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #ff4600, #ff8700, #00e699);
}

.nike-tag {
    display: inline-block;
    font-family: 'Anton', sans-serif !important;
    font-size: 13px;
    letter-spacing: 2px;
    color: #ff4600;
    text-transform: uppercase;
    background: rgba(255, 70, 0, 0.1);
    border: 1px solid rgba(255, 70, 0, 0.3);
    padding: 4px 12px;
    border-radius: 4px;
    margin-bottom: 12px;
}

.hero-title {
    font-family: 'Anton', sans-serif !important;
    font-size: 3.6rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #ffffff;
    margin: 0;
    line-height: 1;
}

.hero-sub {
    color: #8e8e93;
    font-size: 1.05rem;
    margin-top: 10px;
    font-weight: 400;
}

.metric-card {
    background: #111113;
    border: 1px solid #1f1f24;
    border-radius: 16px;
    padding: 24px;
    text-align: left;
    position: relative;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: #ff4600;
    box-shadow: 0 12px 24px rgba(255, 70, 0, 0.15);
}

.metric-val {
    font-family: 'Anton', sans-serif !important;
    font-size: 3.5rem;
    line-height: 1;
    margin-bottom: 6px;
}

.metric-lbl {
    font-size: 12px;
    color: #8e8e93;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
}

.compliance-tag {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px;
    background: #1a1a1e;
    color: #ff8700;
    padding: 4px 10px;
    border-radius: 6px;
    border: 1px solid rgba(255, 135, 0, 0.2);
    margin-right: 6px;
    display: inline-block;
}

.jwt-card {
    background: #0d0d0f;
    border: 1px solid #ff4600;
    border-radius: 12px;
    padding: 16px;
    margin-top: 12px;
}

.jwt-code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px;
    color: #00e699;
    word-break: break-all;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  SECURITY, PHISHING & PASSIVE JWT ENGINES
# ════════════════════════════════════════════════════════════
SECURITY_HEADERS = {
    "content-security-policy": ("Critical", "Missing Content-Security-Policy header. Exposes site to XSS.", "OWASP A03:2021", "CWE-352", 7.5),
    "strict-transport-security": ("High", "Missing HSTS. Allows MITM SSL strip attacks.", "OWASP A02:2021", "CWE-319", 6.5),
    "x-frame-options": ("High", "Missing X-Frame-Options. Vulnerable to Clickjacking.", "OWASP A05:2021", "CWE-1021", 5.4),
    "x-content-type-options": ("Medium", "Missing X-Content-Type-Options. Allows MIME sniffing.", "OWASP A05:2021", "CWE-430", 4.3),
    "referrer-policy": ("Medium", "Missing Referrer-Policy. Leaks navigation data.", "OWASP A01:2021", "CWE-200", 3.1),
    "permissions-policy": ("Low", "Missing Permissions-Policy. Allows unrestricted browser feature usage.", "OWASP A05:2021", "CWE-693", 2.0)
}

CREDENTIAL_SIGNATURES = [
    (r"AIzaSy[A-Za-z0-9_-]{33}", "Google Cloud API Key"),
    (r"sk_live_[51A-Za-z0-9]{24,}", "Stripe Live Secret Key"),
    (r"xox[bapr]-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}", "Slack Token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"-----BEGIN PRIVATE KEY-----", "RSA/Generic Private Key")
]

JWT_REGEX = r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"

class PhishingDetector:
    @staticmethod
    def analyze_url(url: str) -> dict:
        parsed = urlparse(url)
        hostname = parsed.netloc.split(':')[0]
        indicators = []
        risk_score = 0

        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
            indicators.append("Host is a raw IP address (Common Phishing Trait)")
            risk_score += 45

        if len(url) > 75:
            indicators.append("Excessively long URL (> 75 chars)")
            risk_score += 15

        if "@" in url:
            indicators.append("Contains '@' symbol (Used to blind/redirect credentials)")
            risk_score += 30

        if url.rfind("//") > 7:
            indicators.append("Contains suspicious double-slash '//' path redirection")
            risk_score += 25

        if hostname.count("-") > 2:
            indicators.append("Excessive hyphens in domain name")
            risk_score += 15

        suspicious_keywords = ["login", "verify", "update", "account", "banking", "secure", "signin", "nike", "paypal"]
        for kw in suspicious_keywords:
            if kw in hostname.lower() and not hostname.lower().startswith(kw):
                indicators.append(f"Contains target keyword '{kw}' in subdomain structure")
                risk_score += 20

        suspicious_tlds = [".xyz", ".top", ".tk", ".ml", ".ga", ".cf", ".gq", ".work"]
        if any(hostname.endswith(tld) for tld in suspicious_tlds):
            indicators.append("Uses a high-risk TLD frequently associated with phishing")
            risk_score += 20

        return {
            "is_phishing": risk_score >= 40,
            "risk_score": min(risk_score, 100),
            "indicators": indicators
        }

class PassiveJWTAnalyzer:
    @staticmethod
    def inspect_token(token_str: str) -> list:
        findings = []
        parts = token_str.split(".")
        if len(parts) != 3:
            return [{"issue": "Invalid JWT format", "cvss": 0.0}]
        try:
            h_bytes = base64.urlsafe_bdecode(parts[0] + "=" * (-len(parts[0]) % 4))
            header = json.loads(h_bytes)
            if header.get("alg", "").lower() == "none":
                findings.append({"issue": "JWT explicitly allows 'none' algorithm signature bypass", "cvss": 9.1})
            
            p_bytes = base64.urlsafe_bdecode(parts[1] + "=" * (-len(parts[1]) % 4))
            payload = json.loads(p_bytes)
            if "exp" not in payload:
                findings.append({"issue": "JWT lacks Expiration Claim ('exp')", "cvss": 5.3})
        except Exception as e:
            findings.append({"issue": f"Parsing Error: {str(e)}", "cvss": 0.0})
        return findings

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
#  DYNAMIC TESTING CORE (SELF-HEALING BROWSER PIPELINE)
# ════════════════════════════════════════════════════════════
async def perform_crawl_and_scan(root_url: str, crawl_limit: int, browser_type: str, is_unlimited: bool) -> dict:
    start_time = datetime.now()
    phishing_eval = PhishingDetector.analyze_url(root_url)

    summary = {
        "url": root_url,
        "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "browser": browser_type,
        "phishing_analysis": phishing_eval,
        "routes": [],
        "defects": [],
        "detected_jwts": [],
        "owasp_matrix": defaultdict(int),
        "metrics": {"ttfb": 0.0, "dom_interactive": 0.0, "dom_complete": 0.0, "transfer_size_kb": 0, "dom_nodes": 0, "req_count": 0, "max_cvss": 0.0, "resource_breakdown": defaultdict(int)},
        "scores": {"security": 100, "performance": 100, "accessibility": 100, "seo": 100, "ui": 100},
        "network_log": [],
        "headers_captured": {},
        "screenshot": None
    }

    axe_payload = ""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js")
            if r.status_code == 200: axe_payload = r.text
    except Exception:
        pass

    def add_defect(category, severity, title, msg, route, owasp="", cwe="", fix="", cvss=0.0):
        summary["defects"].append({
            "category": category, "severity": severity, "title": title,
            "description": msg, "route": route, "owasp": owasp, "cwe": cwe, "fix": fix, "cvss": cvss
        })
        if owasp:
            summary["owasp_matrix"][owasp] += 1
        summary["metrics"]["max_cvss"] = max(summary["metrics"]["max_cvss"], cvss)
        deduction = {"Critical": 25, "High": 15, "Medium": 8, "Low": 3}.get(severity, 0)
        score_key = category.lower() if category.lower() in summary["scores"] else "seo"
        summary["scores"][score_key] = max(0, summary["scores"][score_key] - deduction)

    if phishing_eval["is_phishing"]:
        add_defect("Security", "Critical", "Phishing Signature Detected", f"Structural URL analysis identified high-risk phishing indicators: {', '.join(phishing_eval['indicators'])}", root_url, "OWASP A07:2021", "CWE-352", cvss=8.5)

    parsed_root = urlparse(root_url)
    target_limit = 999999 if is_unlimited else crawl_limit
    visited = set()
    queue = [root_url]

    async with async_playwright() as p:
        b_engine = p.chromium
        if browser_type == "Firefox": b_engine = p.firefox
        elif browser_type == "WebKit": b_engine = p.webkit

        browser = await b_engine.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])

        try:
            while queue and len(visited) < target_limit:
                current_route = queue.pop(0)
                if current_route in visited: continue
                visited.add(current_route)
                summary["routes"].append(current_route)

                # Self-healing check: Re-launch browser if closed or disconnected
                if not browser or not browser.is_connected():
                    browser = await b_engine.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])

                context = None
                try:
                    context = await browser.new_context(ignore_https_errors=True, viewport={"width": 1280, "height": 800})
                    page = await context.new_page()

                    def log_response(res):
                        try:
                            rt = res.request.resource_type
                            summary["network_log"].append({"url": res.url, "status": res.status, "type": rt})
                            summary["metrics"]["resource_breakdown"][rt] += 1

                            if parsed_root.scheme == "https" and res.url.startswith("http://"):
                                add_defect("Security", "High", "Mixed Content Detected", f"Insecure HTTP resource loaded over HTTPS connection: {res.url}", current_route, "OWASP A02:2021", "CWE-311", cvss=6.5)

                            cookies = res.headers.get("set-cookie", "")
                            if cookies:
                                if "Secure" not in cookies:
                                    add_defect("Security", "Medium", "Insecure Cookie", "Cookie lacks 'Secure' flag.", current_route, "OWASP A05:2021", "CWE-614", cvss=4.3)
                                if "HttpOnly" not in cookies:
                                    add_defect("Security", "Medium", "Scriptable Cookie", "Cookie lacks 'HttpOnly' flag.", current_route, "OWASP A05:2021", "CWE-1004", cvss=4.3)

                            for h_name, h_val in res.headers.items():
                                jwt_matches = re.findall(JWT_REGEX, h_val)
                                for jwt in jwt_matches:
                                    if jwt not in summary["detected_jwts"]:
                                        summary["detected_jwts"].append(jwt)
                                        findings = PassiveJWTAnalyzer.inspect_token(jwt)
                                        for f in findings:
                                            if f["cvss"] > 0:
                                                add_defect("Security", "High" if f["cvss"] >= 7.0 else "Medium", f"Automatic JWT Defect: {f['issue']}", f"Found in response header '{h_name}'.", current_route, "OWASP A02:2021", "CWE-287", cvss=f["cvss"])
                        except Exception:
                            pass

                    page.on("response", log_response)

                    resp = await page.goto(current_route, wait_until="load", timeout=20000)

                    if current_route == root_url:
                        try:
                            perf_data = await page.evaluate("""() => {
                                const nav = performance.getEntriesByType('navigation')[0];
                                return nav ? {
                                    ttfb: nav.responseStart - nav.requestStart,
                                    dom_interactive: nav.domInteractive,
                                    dom_complete: nav.domComplete,
                                    transfer_size: nav.transferSize
                                } : null;
                            }""")
                            if perf_data:
                                summary["metrics"]["ttfb"] = round(perf_data["ttfb"], 2)
                                summary["metrics"]["dom_interactive"] = round(perf_data["dom_interactive"], 2)
                                summary["metrics"]["dom_complete"] = round(perf_data["dom_complete"], 2)
                                summary["metrics"]["transfer_size_kb"] = round(perf_data["transfer_size"] / 1024, 2)
                        except Exception:
                            pass

                        try:
                            summary["metrics"]["dom_nodes"] = await page.evaluate("() => document.querySelectorAll('*').length")
                            summary["metrics"]["req_count"] = len(summary["network_log"])
                            ss_bytes = await page.screenshot(full_page=False)
                            summary["screenshot"] = base64.b64encode(ss_bytes).decode("utf-8")
                        except Exception:
                            pass

                    if resp:
                        summary["headers_captured"] = dict(resp.headers)
                        headers = {k.lower(): v for k, v in resp.headers.items()}
                        for hdr, (sev, desc, owasp, cwe, cvss) in SECURITY_HEADERS.items():
                            if hdr not in headers:
                                add_defect("Security", sev, f"Missing {hdr.upper()}", desc, current_route, owasp, cwe, cvss=cvss)

                    html_markup = await page.content()

                    html_jwts = re.findall(JWT_REGEX, html_markup)
                    for jwt in html_jwts:
                        if jwt not in summary["detected_jwts"]:
                            summary["detected_jwts"].append(jwt)
                            findings = PassiveJWTAnalyzer.inspect_token(jwt)
                            for f in findings:
                                if f["cvss"] > 0:
                                    add_defect("Security", "High" if f["cvss"] >= 7.0 else "Medium", f"Automatic JWT Defect: {f['issue']}", "Found hardcoded in page DOM script source.", current_route, "OWASP A02:2021", "CWE-287", cvss=f["cvss"])

                    for pattern, name in CREDENTIAL_SIGNATURES:
                        if re.search(pattern, html_markup):
                            add_defect("Security", "Critical", f"Exposed secret: {name}", "Credentials in source.", current_route, "OWASP A07:2021", "CWE-798", cvss=8.9)

                    if axe_payload:
                        try:
                            await page.evaluate(axe_payload)
                            axe_results = await page.evaluate("async () => await axe.run();")
                            for violation in axe_results.get("violations", []):
                                add_defect("Accessibility", "High", f"WCAG: {violation['id']}", violation["help"], current_route, "", "", violation["helpUrl"], cvss=3.0)
                        except Exception:
                            pass

                    if len(visited) < target_limit:
                        hrefs = await page.evaluate("() => Array.from(document.querySelectorAll('a[href]')).map(a => a.href).filter(h => h.startsWith('http'))")
                        for link in hrefs:
                            if urlparse(link).netloc == parsed_root.netloc and link not in visited and link not in queue:
                                queue.append(link)

                except Exception as e:
                    add_defect("Security", "Low", "Route Navigation Failure", str(e), current_route)
                finally:
                    if context:
                        try:
                            await context.close()
                        except Exception:
                            pass
        finally:
            if browser and browser.is_connected():
                await browser.close()

    overall = sum(summary["scores"].values()) / 5.0
    summary["scores"]["overall"] = round(overall, 1)
    summary["duration"] = round((datetime.now() - start_time).total_seconds(), 2)
    return summary

# ════════════════════════════════════════════════════════════
#  APPLICATION DASHBOARD
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-banner">
    <div class="nike-tag">JUST SCAN IT.</div>
    <h1 class="hero-title">BugOptix Pro</h1>
    <div class="hero-sub">Enterprise Automated Crawl Engine & Passive JWT Security Intelligence</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⚡ Scan Engine", 
    "🛡️ Phishing Audit", 
    "🔑 JWT Auto-Analyzer", 
    "📈 Vitals & Metrics", 
    "📥 Reports", 
    "🔗 Pipeline"
])

with tab1:
    col_u, col_b, col_unlim, col_c = st.columns([3, 1, 1, 1])
    with col_u: target_url = st.text_input("Target Domain:", "https://example.com")
    with col_b: browser_choice = st.selectbox("Engine:", ["Chromium", "Firefox", "WebKit"])
    with col_unlim: is_unlimited = st.checkbox("Unlimited Crawl", value=False)
    with col_c: 
        crawl_depth = st.slider("Crawl Limit:", 1, 50, 3, disabled=is_unlimited)

    if st.button("RUN ENGINE", type="primary"):
        with st.spinner("Analyzing target domain & detecting JWT structures..."):
            try:
                result = asyncio.run(perform_crawl_and_scan(target_url.strip(), crawl_depth, browser_choice, is_unlimited))
                st.session_state["active_scan"] = result
                VaultManager.append_scan(result)
                st.success("Audit Execution Finished Successfully!")
            except Exception as e:
                st.error(f"Execution Failure: {str(e)}")

    if st.session_state.get("active_scan"):
        scan = st.session_state["active_scan"]
        scores = scan["scores"]
        
        st.markdown("### 📊 Index Breakdown")
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        def display_card(col, value, label, color):
            col.markdown(f'<div class="metric-card"><div class="metric-val" style="color: {color};">{int(value)}</div><div class="metric-lbl">{label}</div></div>', unsafe_allow_html=True)
        
        display_card(sc1, scores["overall"], "Overall Index", "#ff4600")
        display_card(sc2, scores["security"], "Security", "#ff2a5f")
        display_card(sc3, scores["performance"], "Performance", "#00e699")
        display_card(sc4, scores["accessibility"], "Accessibility", "#ffb700")
        display_card(sc5, scores["ui"], "UI / Layout", "#b800ff")

        st.markdown("---")
        st.markdown("### 🛑 Detected Findings")
        if scan["defects"]:
            for d in scan["defects"]:
                cvss_label = f" | CVSS: {d['cvss']}" if d.get('cvss') else ""
                with st.expander(f"[{d['severity']}]{cvss_label} {d['category']} — {d['title']}"):
                    st.markdown(f"**Route:** `{d['route']}`\n\n**Details:** {d['description']}")
                    tags = ""
                    if d.get("owasp"): tags += f"<span class='compliance-tag'>{d['owasp']}</span>"
                    if d.get("cwe"): tags += f"<span class='compliance-tag'>{d['cwe']}</span>"
                    if tags: st.markdown(tags, unsafe_allow_html=True)
        else:
            st.success("No defects or security issues discovered on target.")

with tab2:
    st.subheader("🛡️ Phishing Intelligence")
    if st.session_state.get("active_scan"):
        p_res = st.session_state["active_scan"]["phishing_analysis"]
        if p_res["is_phishing"]:
            st.error(f"⚠️ **HIGH RISK DOMAIN DETECTED** (Score: {p_res['risk_score']}/100)")
        else:
            st.success(f"✅ **LOW PHISHING RISK** (Score: {p_res['risk_score']}/100)")
            
        if p_res["indicators"]:
            for ind in p_res["indicators"]:
                st.write(f"- 🚨 {ind}")
        else:
            st.write("No structural phishing traits detected.")
    else:
        st.info("Execute a scan to view phishing risk intelligence.")

with tab3:
    st.subheader("🔑 Passive JWT Token Inspector")
    if st.session_state.get("active_scan"):
        detected = st.session_state["active_scan"].get("detected_jwts", [])
        st.markdown(f"#### 🤖 Discovered Tokens ({len(detected)})")
        if detected:
            for idx, jwt in enumerate(detected):
                st.markdown(f'<div class="jwt-card"><strong>Token #{idx+1}:</strong><br><span class="jwt-code">{jwt}</span></div>', unsafe_allow_html=True)
                findings = PassiveJWTAnalyzer.inspect_token(jwt)
                for f in findings:
                    st.warning(f"⚠️ {f['issue']} (CVSS: {f['cvss']})")
        else:
            st.info("No active JWT tokens detected during the domain crawl.")

    st.markdown("---")
    st.markdown("#### 🔍 Manual JWT Analysis")
    jwt_input = st.text_area("Paste JWT String:")
    if st.button("Parse & Inspect JWT"):
        if jwt_input.strip():
            findings = PassiveJWTAnalyzer.inspect_token(jwt_input.strip())
            for f in findings:
                st.warning(f"⚠️ {f['issue']} (CVSS Base Rating: {f['cvss']})")
        else:
            st.error("Please provide a valid JWT string.")

with tab4:
    st.subheader("📈 Real Browser Performance Vitals")
    if st.session_state.get("active_scan"):
        metrics = st.session_state["active_scan"]["metrics"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TTFB", f"{metrics['ttfb']} ms")
        m2.metric("DOM Interactive", f"{metrics['dom_interactive']} ms")
        m3.metric("DOM Complete", f"{metrics['dom_complete']} ms")
        m4.metric("Transfer Size", f"{metrics['transfer_size_kb']} KB")
    else:
        st.info("No active scan performance metrics available.")

with tab5:
    st.subheader("📥 Export Scan Reports")
    if st.session_state.get("active_scan"):
        scan = st.session_state["active_scan"]
        st.download_button("Download JSON Audit File", json.dumps(scan, indent=4), "audit_report.json", "application/json")
    else:
        st.info("Run an audit scan to generate a report.")

with tab6:
    st.subheader("🔗 CI/CD Pipeline Automation Script")
    st.code("python -c \"import json; score=json.load(open('report.json'))['scores']['overall']; exit(1) if score < 80 else exit(0)\"", language="bash")
