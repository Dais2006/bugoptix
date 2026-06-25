import os
import subprocess
import sys

# 1. FORCE THE BROWSER INSTALLATION ON SERVER STARTUP
# We do this before any other imports to guarantee the binary exists.
def setup_playwright():
    try:
        # Inform the logs we are installing
        print("Starting Playwright system installation...")
        
        # Install the specific chromium headless shell binary
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        
        # Install any missing system dependencies for Linux
        subprocess.run([sys.executable, "-m", "playwright", "install-deps"], check=True)
        
        print("Playwright installation completed successfully!")
    except Exception as e:
        print(f"Playwright installation failed: {e}")

# Run the installer automatically every time the container starts up
setup_playwright()

# Now it is safe to import streamlit and playwright
import streamlit as st
from playwright.sync_api import sync_playwright

# ----------------------------------------------------
# 2. APPLICATION INTERFACE
# ----------------------------------------------------
st.title("Automated Web Application QA & Technical Compliance Engine")

# Optional setup checks visible to you
st.sidebar.success("System Environment: Initialized")

if st.button("Execute Comprehensive Deep Diagnostic Scan"):
    st.info("Scanner initialized. Launching browser instance...")
    
    try:
        # Wrap execution tightly in context managers
        with sync_playwright() as p:
            # Headless mode is mandatory on cloud environments
            browser = p.chromium.launch(headless=True)
            
            page = browser.new_page()
            st.info("Navigating to target URL...")
            
            # Navigate to the target input field URL safely
            page.goto("https://zgcollege.wakinedu.com/erp/admission", timeout=60000)
            
            st.success(f"Successfully reached page! Title: {page.title()}")
            
            # --- Insert your custom testing or scraping analysis code here ---
            
            browser.close()
            
    except Exception as error:
        st.error(f"Execution Error encountered: {error}")
