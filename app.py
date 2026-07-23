import os
import asyncio
import json
import base64
import re
import time
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse, urljoin
from io import BytesIO
import concurrent.futures

import streamlit as st
import pandas as pd

# ════════════════════════════════════════════════════════════
#  1. PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="BugOptix Pro | Enterprise Auditor", 
    page_icon="⚡", 
    layout="wide"
)

# ════════════════════════════════════════════════════════════
#  2. SAFE IMPORTS FOR THIRD-PARTY LIBRARIES
# ════════════════════════════════════════════════════════════
HTTPX_AVAILABLE = False
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    pass

BS4_AVAILABLE = False
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    pass

PLOTLY_AVAILABLE = False
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except Exception:
    pass

REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except Exception:
    pass

# ════════════════════════════════════════════════════════════
#  3. OBSIDIAN STYLING SYSTEM & TAB ANIMATIONS
# ════════════════════════════════════════════════════════════
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

/* Dynamic Menu / Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    background-color: #111113;
    padding: 10px 16px;
    border-radius: 14px;
    border: 1px solid #1f1f24;
}

.stTabs [data-baseweb="tab"] {
    height: 48px;
    background-color: #08080a;
    border-radius: 10px;
    color: #8e8e93;
    font-weight: 700;
    font-size: 14px;
    border: 1px solid transparent;
    padding: 0px 18px;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.stTabs [data-baseweb="tab"]:hover {
    color: #ffffff;
    border-color: #ff4600;
    transform: translateY(-2px);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #ff4600 0%, #ff8700 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(255, 70, 0, 0.4);
}

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
#  4. SECURITY ENGINES & RULES
# ════════════════════════════════════════════════════════════
SECURITY_HEADERS = {
    "content-security-policy": ("Critical", "Missing Content-Security-Policy header. Exposes site to XSS.", "OWASP A03:2021", "CWE-352", 7.5, "Implement a strict CSP restricting script execution to trusted domains."),
    "strict-transport-security": ("High", "Missing HSTS. Allows MITM SSL strip attacks.", "OWASP A02:2021", "CWE-319", 6.5, "Enable HSTS header with max-age=31536000 and includeSubDomains."),
    "x-frame-options": ("High", "Missing X-Frame-Options. Vulnerable to Clickjacking.", "OWASP A05:2021", "CWE-1021", 5.4, "Configure X-Frame-Options to DENY or SAMEORIGIN."),
    "x-content-type-options": ("Medium", "Missing X-Content-Type-Options. Allows MIME sniffing.", "OWASP A05:2021", "CWE-430", 4.3, "Set X-Content-Type-Options to 'nosniff'."),
    "referrer-policy": ("Medium", "Missing Referrer-Policy. Leaks navigation data.", "OWASP A01:2021", "CWE-200", 3.1, "Set Referrer-Policy to 'strict-origin-when-cross-origin'."),
    "permissions-policy": ("Low", "Missing Permissions-Policy. Allows unrestricted browser feature usage.", "OWASP A05:2021", "CWE-693", 2.0, "Define explicit permissions policy for camera, microphone, and geolocation.")
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
            current["scans"].append(record)
            with open(VAULT_FILE, "w") as f:
                json.dump(current, f, indent=4)
        except Exception:
            pass

# ════════════════════════════════════════════════════════════
#  5. PROFESSIONAL ENTERPRISE PDF GENERATOR
# ════════════════════════════════════════════════════════════
def generate_pdf_report(scan_data: dict) -> bytes:
    if not REPORTLAB_AVAILABLE:
        return b""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    # Styles Setup
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor("#ff4600"), spaceAfter=6, fontName="Helvetica-Bold")
    subtitle_style = ParagraphStyle('DocSubTitle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor("#666666"), spaceAfter=14)
    h2_style = ParagraphStyle('DocH2', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor("#111113"), spaceBefore=14, spaceAfter=8, fontName="Helvetica-Bold")
    body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor("#333333"), leading=11)
    cell_style = ParagraphStyle('DocCell', parent=styles['Normal'], fontSize=7.5, textColor=colors.HexColor("#222222"), leading=9)
    json_code_style = ParagraphStyle('JsonCode', parent=styles['Normal'], fontName='Courier', fontSize=6.5, leading=8, textColor=colors.HexColor("#1e1e1e"))
    
    story = []

    # --- COVER / HEADER & METADATA BLOCK ---
    story.append(Paragraph("BUGOPTIX PRO — ENTERPRISE SECURITY & AUDIT REPORT", title_style))
    story.append(Paragraph("CONFIDENTIAL | FOR INTERNAL & TECHNICAL STAKEHOLDER REVIEW ONLY", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#ff4600"), spaceAfter=12))

    meta_data = [
        [Paragraph("<b>Target URL:</b>", body_style), Paragraph(scan_data['url'], body_style), Paragraph("<b>Audit Date:</b>", body_style), Paragraph(scan_data['timestamp'], body_style)],
        [Paragraph("<b>Execution Engine:</b>", body_style), Paragraph(scan_data.get('browser', 'Fast Parser'), body_style), Paragraph("<b>Pages Crawled:</b>", body_style), Paragraph(str(len(scan_data.get('routes', []))), body_style)],
        [Paragraph("<b>Max Severity Threat:</b>", body_style), Paragraph(f"CVSS {scan_data['metrics'].get('max_cvss', 0.0)}", body_style), Paragraph("<b>Overall Index:</b>", body_style), Paragraph(f"{scan_data['scores']['overall']}/100", body_style)],
    ]
    t_meta = Table(meta_data, colWidths=[100, 170, 90, 160])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    # --- EXECUTIVE NARRATIVE ---
    story.append(Paragraph("1. Executive Summary", h2_style))
    story.append(Paragraph(
        f"A comprehensive security, compliance, and performance assessment was conducted for <b>{scan_data['url']}</b>. "
        f"The platform achieved an overall rating of <b>{scan_data['scores']['overall']}/100</b>. "
        f"A total of <b>{len(scan_data.get('defects', []))} defect(s)</b> were identified during automated crawling. Immediate remediation is advised for issues marked as Critical or High.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # --- SCORECARDS TABLE ---
    scores = scan_data['scores']
    score_table_data = [
        ["Overall Index", "Security", "Performance", "Accessibility", "UI Rating"],
        [f"{scores['overall']}/100", f"{scores['security']}/100", f"{scores['performance']}/100", f"{scores['accessibility']}/100", f"{scores['ui']}/100"]
    ]
    t_scores = Table(score_table_data, colWidths=[104]*5)
    t_scores.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#111113")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_scores)
    story.append(Spacer(1, 12))

    # --- VULNERABILITY MATRIX ---
    story.append(Paragraph("2. Detailed Findings & Compliance Mapping", h2_style))
    defects = scan_data.get("defects", [])
    if defects:
        defect_table_data = [["Sev", "Category", "Vulnerability & Description", "OWASP / CWE", "CVSS", "Remediation Guidance"]]
        for d in defects:
            defect_table_data.append([
                d.get("severity", "Low"),
                d.get("category", "General"),
                Paragraph(f"<b>{d.get('title', '')}</b><br/>{d.get('description', '')}", cell_style),
                Paragraph(f"{d.get('owasp', 'N/A')}<br/>{d.get('cwe', 'N/A')}", cell_style),
                str(d.get("cvss", "0.0")),
                Paragraph(d.get("fix", "Review server configuration and code."), cell_style)
            ])
        t_defects = Table(defect_table_data, colWidths=[40, 55, 150, 75, 35, 165])
        t_defects.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#ff4600")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
            ('FONTSIZE', (0,0), (-1,-1), 7.5),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_defects)
    else:
        story.append(Paragraph("No critical defects or security risks were identified.", body_style))

    # --- PAGE 2: PHISHING & RAW JSON DATA ---
    story.append(PageBreak())
    story.append(Paragraph("3. Specialized Security & Telemetry", h2_style))
    p_res = scan_data.get("phishing_analysis", {})
    story.append(Paragraph(f"<b>Phishing Risk Score:</b> {p_res.get('risk_score', 0)}/100 | <b>Status:</b> {'HIGH RISK' if p_res.get('is_phishing') else 'Pass/Low Risk'}", body_style))
    if p_res.get("indicators"):
        for ind in p_res["indicators"]:
            story.append(Paragraph(f"• {ind}", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("4. Technical Machine-Readable Telemetry (JSON)", h2_style))
    story.append(Paragraph("Structured record attached for automated CI/CD pipeline ingestion and SIEM logging.", subtitle_style))
    
    formatted_json_str = json.dumps(scan_data, indent=2)
    json_lines = formatted_json_str.split("\n")
    json_table_data = []
    for line in json_lines:
        safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&nbsp;")
        json_table_data.append([Paragraph(safe_line, json_code_style)])

    t_json = Table(json_table_data, colWidths=[520])
    t_json.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#dcdcdc")),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_json)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ════════════════════════════════════════════════════════════
#  6. ISOLATED ASYNC EXECUTION WORKER
# ════════════════════════════════════════════════════════════
def run_async_isolated(coro):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()

# ════════════════════════════════════════════════════════════
#  7. CRAWLER & AUDIT ENGINE
# ════════════════════════════════════════════════════════════
async def perform_crawl_and_scan(root_url: str, crawl_limit: int, engine_mode: str, is_unlimited: bool) -> dict:
    if not HTTPX_AVAILABLE or not BS4_AVAILABLE:
        raise RuntimeError("Required packages 'httpx' or 'beautifulsoup4' are missing in the environment.")

    start_time = datetime.now()
    phishing_eval = PhishingDetector.analyze_url(root_url)

    summary = {
        "url": root_url,
        "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "browser": engine_mode,
        "phishing_analysis": phishing_eval,
        "routes": [],
        "defects": [],
        "detected_jwts": [],
        "owasp_matrix": defaultdict(int),
        "metrics": {"ttfb": 0.0, "dom_interactive": 0.0, "dom_complete": 0.0, "transfer_size_kb": 0, "dom_nodes": 0, "req_count": 0, "max_cvss": 0.0, "resource_breakdown": defaultdict(int)},
        "scores": {"security": 100, "performance": 100, "accessibility": 100, "seo": 100, "ui": 100},
        "network_log": [],
        "headers_captured": {}
    }

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
        add_defect("Security", "Critical", "Phishing Signature Detected", f"Structural URL analysis identified high-risk phishing indicators: {', '.join(phishing_eval['indicators'])}", root_url, "OWASP A07:2021", "CWE-352", "Audit domain registration and enforce domain monitoring.", cvss=8.5)

    parsed_root = urlparse(root_url)
    target_limit = 999999 if is_unlimited else crawl_limit
    visited = set()
    queue = [root_url]

    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=10.0) as client:
        while queue and len(visited) < target_limit:
            current_route = queue.pop(0)
            if current_route in visited: continue
            visited.add(current_route)
            summary["routes"].append(current_route)

            try:
                t0 = time.time()
                resp = await client.get(current_route)
                latency = round((time.time() - t0) * 1000, 2)

                if current_route == root_url:
                    summary["metrics"]["ttfb"] = latency
                    summary["metrics"]["transfer_size_kb"] = round(len(resp.content) / 1024, 2)
                    summary["headers_captured"] = dict(resp.headers)

                summary["network_log"].append({"url": current_route, "status": resp.status_code, "type": "document"})

                # Security Headers Audit
                headers = {k.lower(): v for k, v in resp.headers.items()}
                for hdr, (sev, desc, owasp, cwe, cvss, fix) in SECURITY_HEADERS.items():
                    if hdr not in headers:
                        add_defect("Security", sev, f"Missing {hdr.upper()}", desc, current_route, owasp, cwe, fix, cvss=cvss)

                cookies = resp.headers.get("set-cookie", "")
                if cookies:
                    if "Secure" not in cookies:
                        add_defect("Security", "Medium", "Insecure Cookie", "Cookie lacks 'Secure' flag.", current_route, "OWASP A05:2021", "CWE-614", "Append 'Secure' attribute to set-cookie headers.", cvss=4.3)
                    if "HttpOnly" not in cookies:
                        add_defect("Security", "Medium", "Scriptable Cookie", "Cookie lacks 'HttpOnly' flag.", current_route, "OWASP A05:2021", "CWE-1004", "Append 'HttpOnly' attribute to sensitive cookies.", cvss=4.3)

                for h_name, h_val in resp.headers.items():
                    jwt_matches = re.findall(JWT_REGEX, h_val)
                    for jwt in jwt_matches:
                        if jwt not in summary["detected_jwts"]:
                            summary["detected_jwts"].append(jwt)
                            findings = PassiveJWTAnalyzer.inspect_token(jwt)
                            for f in findings:
                                if f["cvss"] > 0:
                                    add_defect("Security", "High" if f["cvss"] >= 7.0 else "Medium", f"Automatic JWT Defect: {f['issue']}", f"Found in header '{h_name}'.", current_route, "OWASP A02:2021", "CWE-287", "Enforce asymmetric signatures and valid exp claims.", cvss=f["cvss"])

                # DOM Content & Secret Scanning
                html_markup = resp.text
                if current_route == root_url:
                    soup = BeautifulSoup(html_markup, "html.parser")
                    summary["metrics"]["dom_nodes"] = len(soup.find_all())

                    imgs_without_alt = soup.find_all("img", alt=False)
                    if imgs_without_alt:
                        add_defect("Accessibility", "Medium", "Missing Image Alt Tags", f"Found {len(imgs_without_alt)} image tags without 'alt' attributes.", current_route, "OWASP A05:2021", "CWE-1007", "Add meaningful alt text to images.", cvss=3.0)

                    inputs_without_label = [i for i in soup.find_all("input") if not i.get("aria-label") and not i.get("id")]
                    if inputs_without_label:
                        add_defect("Accessibility", "Low", "Unlabeled Input Fields", f"Found {len(inputs_without_label)} input fields lacking explicit labels.", current_route, "OWASP A05:2021", "CWE-1007", "Associate input elements with explicit labels.", cvss=2.0)

                html_jwts = re.findall(JWT_REGEX, html_markup)
                for jwt in html_jwts:
                    if jwt not in summary["detected_jwts"]:
                        summary["detected_jwts"].append(jwt)
                        findings = PassiveJWTAnalyzer.inspect_token(jwt)
                        for f in findings:
                            if f["cvss"] > 0:
                                add_defect("Security", "High" if f["cvss"] >= 7.0 else "Medium", f"Automatic JWT Defect: {f['issue']}", "Found in HTML/JS source.", current_route, "OWASP A02:2021", "CWE-287", "Remove hardcoded JWTs from client-side markup.", cvss=f["cvss"])

                for pattern, name in CREDENTIAL_SIGNATURES:
                    if re.search(pattern, html_markup):
                        add_defect("Security", "Critical", f"Exposed secret: {name}", "Credentials exposed in DOM markup.", current_route, "OWASP A07:2021", "CWE-798", "Revoke compromised key and store in vault.", cvss=8.9)

                # Site Link Crawler
                if len(visited) < target_limit:
                    soup = BeautifulSoup(html_markup, "html.parser")
                    for a in soup.find_all("a", href=True):
                        link = urljoin(current_route, a["href"])
                        if urlparse(link).netloc == parsed_root.netloc and link not in visited and link not in queue:
                            queue.append(link)

            except Exception as e:
                add_defect("Security", "Low", "Route Fetch Error", str(e), current_route, fix="Verify route accessibility.")

    overall = sum(summary["scores"].values()) / 5.0
    summary["scores"]["overall"] = round(overall, 1)
    summary["duration"] = round((datetime.now() - start_time).total_seconds(), 2)
    return summary

# ════════════════════════════════════════════════════════════
#  8. DASHBOARD USER INTERFACE
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-banner">
    <div class="nike-tag">JUST SCAN IT.</div>
    <h1 class="hero-title">BugOptix Pro</h1>
    <div class="hero-sub">Enterprise Automated Crawl Engine & Passive Security Intelligence</div>
</div>
""", unsafe_allow_html=True)

# Correct Order: Scan Engine first, followed by Executive Summary and Specialized Audits
tab1, tab_summary, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⚡ Scan Engine", 
    "📊 Executive Summary",
    "🛡️ Phishing Audit", 
    "🔑 JWT Inspector", 
    "📈 Vitals & Metrics", 
    "📄 Technical Reports", 
    "🔗 CI/CD Pipeline"
])

# --- TAB 1: SCAN ENGINE ---
with tab1:
    col_u, col_b, col_unlim, col_c = st.columns([3, 1, 1, 1])
    with col_u: target_url = st.text_input("Target Domain:", "https://example.com")
    with col_b: browser_choice = st.selectbox("Engine:", ["Fast Dynamic Parser", "Deep HTTP Prober"])
    with col_unlim: is_unlimited = st.checkbox("Unlimited Crawl", value=False)
    with col_c: crawl_depth = st.slider("Crawl Limit:", 1, 50, 3, disabled=is_unlimited)

    if st.button("RUN ENGINE", type="primary"):
        with st.spinner("Analyzing target domain & inspecting HTTP assets..."):
            try:
                result = run_async_isolated(perform_crawl_and_scan(target_url.strip(), crawl_depth, browser_choice, is_unlimited))
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
        st.markdown("### 🛑 Discovered Vulnerabilities & Findings")
        if scan["defects"]:
            for d in scan["defects"]:
                cvss_label = f" | CVSS: {d['cvss']}" if d.get('cvss') else ""
                with st.expander(f"[{d['severity']}]{cvss_label} {d['category']} — {d['title']}"):
                    st.markdown(f"**Route:** `{d['route']}`\n\n**Details:** {d['description']}\n\n**Fix Guidance:** `{d.get('fix', 'N/A')}`")
        else:
            st.success("No defects or security issues discovered on target.")

# --- TAB 2: EXECUTIVE SUMMARY ---
with tab_summary:
    st.subheader("📊 C-Level Executive Security Summary")
    if st.session_state.get("active_scan"):
        scan = st.session_state["active_scan"]
        defects = scan.get("defects", [])
        scores = scan["scores"]
        
        col_pdf1, col_pdf2 = st.columns([3, 1])
        with col_pdf1:
            st.markdown(f"**Target Host:** `{scan['url']}` | **Scanned At:** `{scan['timestamp']}`")
        with col_pdf2:
            if REPORTLAB_AVAILABLE:
                pdf_bytes = generate_pdf_report(scan)
                st.download_button(
                    label="📄 Export Professional PDF Report",
                    data=pdf_bytes,
                    file_name=f"executive_summary_{scan['url'].replace('https://','').replace('http://','').replace('/','_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        st.markdown("---")

        if PLOTLY_AVAILABLE:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=scores["overall"],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Security Posture Score", 'font': {'size': 18, 'color': '#ffffff'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': "#ffffff"},
                        'bar': {'color': "#ff4600"},
                        'steps': [
                            {'range': [0, 50], 'color': "rgba(255, 42, 95, 0.3)"},
                            {'range': [50, 80], 'color': "rgba(255, 183, 0, 0.3)"},
                            {'range': [80, 100], 'color': "rgba(0, 230, 153, 0.3)"}
                        ],
                    }
                ))
                fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=280)
                st.plotly_chart(fig_gauge, use_container_width=True)

            with col_g2:
                max_cvss = scan["metrics"].get("max_cvss", 0.0)
                fig_cvss_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=max_cvss,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Peak CVSS Severity Threat", 'font': {'size': 18, 'color': '#ffffff'}},
                    gauge={
                        'axis': {'range': [0, 10.0], 'tickcolor': "#ffffff"},
                        'bar': {'color': "#ff2a5f"},
                        'steps': [
                            {'range': [0, 3.9], 'color': "rgba(0, 230, 153, 0.3)"},
                            {'range': [4.0, 6.9], 'color': "rgba(255, 183, 0, 0.3)"},
                            {'range': [7.0, 10.0], 'color': "rgba(255, 42, 95, 0.4)"}
                        ],
                    }
                ))
                fig_cvss_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=280)
                st.plotly_chart(fig_cvss_gauge, use_container_width=True)
        else:
            st.dataframe(pd.DataFrame(defects) if defects else "No defects discovered.")
    else:
        st.info("⚡ Run an active audit scan in the Scan Engine tab to populate the Executive Summary dashboard.")

# --- TAB 3: PHISHING AUDIT ---
with tab2:
    st.subheader("🛡️ Phishing & Brand Protection Intelligence")
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
        st.info("Execute a scan to view phishing risk intelligence.")

# --- TAB 4: JWT INSPECTOR ---
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
            st.info("No active JWT tokens detected during domain crawl.")

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

# --- TAB 5: VITALS & METRICS ---
with tab4:
    st.subheader("📈 Real Network Vitals & Telemetry")
    if st.session_state.get("active_scan"):
        metrics = st.session_state["active_scan"]["metrics"]
        m1, m2, m3 = st.columns(3)
        m1.metric("TTFB (Latency)", f"{metrics['ttfb']} ms")
        m2.metric("DOM Elements Count", f"{metrics['dom_nodes']}")
        m3.metric("Transfer Size", f"{metrics['transfer_size_kb']} KB")
    else:
        st.info("No active scan performance metrics available.")

# --- TAB 6: TECHNICAL REPORTS ---
with tab5:
    st.subheader("📄 Download Technical Reports")
    if st.session_state.get("active_scan"):
        scan = st.session_state["active_scan"]
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("📥 Download JSON Telemetry Data", json.dumps(scan, indent=4), "audit_report.json", "application/json", use_container_width=True)
        with col_dl2:
            if REPORTLAB_AVAILABLE:
                pdf_bytes = generate_pdf_report(scan)
                st.download_button("📄 Download Professional PDF Report", pdf_bytes, "audit_report.pdf", "application/pdf", use_container_width=True)
    else:
        st.info("Run an audit scan to generate downloadable reports.")

# --- TAB 7: CI/CD PIPELINE ---
with tab6:
    st.subheader("🔗 CI/CD Pipeline Automation Script")
    st.code("python -c \"import json; score=json.load(open('report.json'))['scores']['overall']; exit(1) if score < 80 else exit(0)\"", language="bash")
