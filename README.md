# bugoptix
bug finder
# 🛡️ BugOptix AI — Deep Diagnostic Suite

BugOptix AI is an enterprise-grade, automated web application QA and technical compliance engine. By bridging headless browser automation with advanced artificial intelligence, BugOptix sandboxes target web applications, monitors real-time technical regressions, and synthesizes developer logs into executive, client-ready business reports.

Built with **Python**, **Streamlit**, **Playwright**, and the modern **Google GenAI SDK**, it features a dual-processing intelligence architecture designed to stay highly available, even under strict API quota constraints.

---

## 🚀 Core Features

### 1. Deep Audit Scraper Engine (Playwright)
Instead of relying on simple, static HTML parsers, BugOptix provisions an isolated, headless Chromium browser environment. It actively listens to a live target web framework to capture background runtime anomalies:
* **Diagnostic Layer (Console Monitor):** Continuously catches runtime JavaScript crashes (`pageerror`) that remain completely invisible to normal visitors but ruin user experiences.
* **Network Monitor:** Tracks failing network endpoints, blocked API requests, and missing critical CDN resources (`requestfailed`).

### 2. Live Performance Diagnostics (Core Web Vitals)
A stable website can still fail if it behaves sluggishly. The engine interacts directly with the browser's native JavaScript performance metrics window to deliver precision benchmarking data:
* **Raw Browser Load Time:** Calculates the exact duration (in milliseconds) of the physical handshake and page load timeline.
* **DOM Engine Readiness:** Tracks how fast the structural DOM layer parses, revealing underlying design blocking issues.

### 3. Multi-Model Intelligence Selector
BugOptix integrates seamlessly with Google’s production-grade Large Language Models. It features an interactive model dropdown selector in the control panel allowing engineers to switch between different operational intelligence profiles on the fly:
* `gemini-2.5-flash` (Optimized, lightweight execution)
* `gemini-2.5-pro` (Deep, analytical logic sweeps)
* `gemini-1.5-flash` (Legacy infrastructure fallback routing)

### 4. Fully Autonomous Local Failsafe Engine
To guarantee zero-downtime operation, the suite is engineered with a self-healing exception handling architecture. If the primary Google API keys are absent, frozen, or hit server rate limits (`429 Resource Exhausted`), the application seamlessly switches to a local parsing mode. It evaluates data locally and auto-generates a structured compliance matrix report instantly without an active internet connection.

### 5. Mobile Viewport & Target Element Emulation
* **Responsive Footprints:** Test responsive layouts by emulating real mobile and tablet environments (such as Apple iPhone 14/15 or iPad Pro profiles) to identify visual defects on compact viewports.
* **Target Scope Isolator:** Pinpoint a single critical page element (like `#login-form` or `.nav-bar`) using standard CSS selectors to isolate technical audits on specific components.

---

## 🛠️ Architecture & Stack

* **Frontend Dashboard:** Streamlit (Custom Dark Theme Corporate CSS Injection)
* **Automation Framework:** Playwright Asynchronous Core (`asyncio`)
* **AI Processing Model:** Google GenAI SDK (`gemini-2.5-flash` target)
* **Token Optimization Matrix:** Built-in whitespace stripping and aggressive character truncation to protect free-tier operational quotas.

---

## 📦 Installation & Setup

Follow these quick commands to spin up BugOptix AI on your local workstation:

### 1. Clone the Workspace & Enter Repository
```bash
git clone [https://github.com/YOUR_USERNAME/BugOptix-AI-Tester.git](https://github.com/YOUR_USERNAME/BugOptix-AI-Tester.git)
cd BugOptix-AI-Tester
