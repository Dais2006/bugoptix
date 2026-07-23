import os
import asyncio
import subprocess
import sys
import json
import base64
import re
import httpx
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse, parse_qs

import streamlit as st
import pandas as pd

# Async policy fix for Windows Streamlit runtimes
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
#  STYLING & INTERFACE MATRIX
# ════════════════════════════════════════════════════════════
st.set_page_config(page_title="BugOptix Pro | Passive Enterprise Auditor", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

*, *::before, *::after { font-family: 'Plus Jakarta Sans', sans-serif; box-sizing: border-box; }

html, body, [class*="css"] {
    background-color: #05070f !important;
    color: #f1f5f9;
}

#MainMenu, footer, header { visibility: hidden; }

.hero {
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    padding: 30px 40px;
    margin-bottom: 24px;
}

.hero-title {
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.score-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}

.score-value {
    font-size: 2.2rem;
    font-weight: 900;
    font-family: 'JetBrains Mono', monospace;
}

.score-label {
    font-size: 11px;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 6px;
}

.compliance-tag {
    font-size: 10px;
    font-family: 'JetBrains Mono', monospace;
    background: rgba(30, 41, 59, 0.8);
    color: #38bdf8;
    padding: 3px 8px;
    border-radius: 6px;
    border: 1px solid rgba(56, 189, 248, 0.2);
    margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  PASSIVE INSPECTION & CVSS RULES
# ════════════════════════════════════════════════════════════
SECURITY_HEADERS = {
    "content-security-policy": ("Critical", "Missing CSP Header", "OWASP A03:2021", "CWE-352", 7.5),
    "strict-transport-security": ("High", "Missing HSTS Header", "OWASP A02:2021", "CWE-319", 6.5),
    "x-frame-options": ("High", "Missing X-Frame-Options", "OWASP A05:2021", "CWE-1021", 5.4),
    "x-content-type-options": ("Medium", "Missing X-Content-Type-Options", "OWASP A05:2021", "CWE-430", 4.3),
    "referrer-policy": ("Medium", "Missing Referrer-Policy", "OWASP A01:2021", "CWE-200", 3.1)
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
                findings.append({"issue": "Token allows 'none' algorithm", "cvss": 9.1})
            
            p_bytes = base64.urlsafe_bdecode(parts[1] + "=" * (-len(parts[1]) % 4))
            payload = json.loads(p_bytes)
            if "exp" not in payload:
                findings.append({"issue": "Token lacks Expiration Claim ('exp')", "cvss": 5.3})
        except Exception as e:
            findings.append({"issue": f"Parsing Error: {str(e)}", "cvss": 0.0})
        return findings

async def perform_passive_audit(target_url: str) -> dict:
    summary = {
        "url": target_url,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "defects": [],
        "owasp_matrix": defaultdict(int),
        "evidence": {"headers": {}, "screenshot": None},
        "metrics": {"max_cvss": 0.0}
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:
            resp = await page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
            
            # 1. Capture Header Evidence & Passive Check
            if resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                summary["evidence"]["headers"] = dict(resp.headers)
                
                for hdr, (sev, desc, owasp, cwe, cvss) in SECURITY_HEADERS.items():
                    if hdr not in headers:
                        summary["defects"].append({
                            "category": "Headers", "severity": sev, "title": f"Missing {hdr.upper()}",
                            "description": desc, "owasp": owasp, "cwe": cwe, "cvss": cvss
                        })
                        summary["owasp_matrix"][owasp] += 1
                        summary["metrics"]["max_cvss"] = max(summary["metrics"]["max_cvss"], cvss)

            # 2. Passive Parameter Surface Check
            parsed = urlparse(target_url)
            params = parse_qs(parsed.query)
            suspicious_params = ["redirect", "url", "next", "file", "path", "id"]
            for param in params:
                if param.lower() in suspicious_params:
                    summary["defects"].append({
                        "category": "Endpoint Surface", "severity": "Low",
                        "title": f"Sensitive Query Parameter Detected: '{param}'",
                        "description": "Parameter pattern often associated with navigation/redirection logic. Review access controls.",
                        "owasp": "OWASP A01:2021", "cwe": "CWE-601", "cvss": 3.1
                    })
                    summary["owasp_matrix"]["OWASP A01:2021"] += 1

            # 3. Form Anti-CSRF Token Audit
            forms = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('form')).map(f => ({
                    method: f.method.toUpperCase(),
                    action: f.action,
                    has_token: !!f.querySelector('input[type="hidden"][name*="csrf" i], input[type="hidden"][name*="token" i]')
                }));
            }""")
            
            for f in forms:
                if f["method"] in ["POST", "PUT", "DELETE"] and not f["has_token"]:
                    summary["defects"].append({
                        "category": "CSRF Defenses", "severity": "Medium",
                        "title": "State-Changing Form Missing Anti-CSRF Field",
                        "description": f"Form acting on '{f['action']}' lacks a hidden anti-CSRF token attribute.",
                        "owasp": "OWASP A01:2021", "cwe": "CWE-352", "cvss": 4.3
                    })
                    summary["owasp_matrix"]["OWASP A01:2021"] += 1

            # 4. Screenshot Capture
            ss_bytes = await page.screenshot(full_page=False)
            summary["evidence"]["screenshot"] = base64.b64encode(ss_bytes).decode("utf-8")

        except Exception as e:
            summary["defects"].append({
                "category": "Runtime", "severity": "High", "title": "Audit Failure",
                "description": str(e), "owasp": "OWASP A05:2021", "cwe": "CWE-693", "cvss": 0.0
            })
        finally:
            await browser.close()

    return summary

# ════════════════════════════════════════════════════════════
#  DASHBOARD CONTROLLER
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <h1 class="hero-title">BugOptix Pro</h1>
    <p style="color: #94a3b8; margin-top: 6px;">Passive Web Configuration & Security Audit Engine</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 Passive Audit Engine", "🔑 Static JWT Inspector", "📸 Evidence Vault"])

with tab1:
    target = st.text_input("Target URL:", "https://example.com")
    if st.button("Run Passive Audit", type="primary"):
        with st.spinner("Analyzing web configuration and headers..."):
            res = asyncio.run(perform_passive_audit(target))
            st.session_state["audit_res"] = res

    if st.session_state.get("audit_res"):
        data = st.session_state["audit_res"]
        
        st.markdown("### 📊 Summary Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="score-card"><div class="score-value" style="color: #fb7185;">{data["metrics"]["max_cvss"]}</div><div class="score-label">Max CVSS Score</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="score-card"><div class="score-value" style="color: #38bdf8;">{len(data["defects"])}</div><div class="score-label">Defects Identified</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="score-card"><div class="score-value" style="color: #c084fc;">{len(data["owasp_matrix"])}</div><div class="score-label">OWASP Categories Impacted</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🛑 Findings & CVSS Ratings")
        for d in data["defects"]:
            with st.expander(f"[{d['severity']}] CVSS {d['cvss']} — {d['title']}"):
                st.write(d["description"])
                st.markdown(f"<span class='compliance-tag'>{d['owasp']}</span><span class='compliance-tag'>{d['cwe']}</span>", unsafe_allow_html=True)

with tab2:
    st.subheader("🔑 Static JWT Claims Inspection")
    jwt_input = st.text_area("Paste JWT String:")
    if st.button("Analyze JWT"):
        if jwt_input.strip():
            results = PassiveJWTAnalyzer.inspect_token(jwt_input.strip())
            for r in results:
                st.warning(f"⚠️ {r['issue']} (CVSS: {r['cvss']})")
        else:
            st.error("Please enter a JWT string.")

with tab3:
    st.subheader("📸 Captured Evidence & Headers")
    if st.session_state.get("audit_res"):
        ev = st.session_state["audit_res"]["evidence"]
        if ev["screenshot"]:
            st.image(base64.b64decode(ev["screenshot"]), caption="DOM Render Evidence", use_column_width=True)
        st.markdown("#### Response Headers")
        st.json(ev["headers"])
    else:
        st.info("Run an audit to view evidence.")
