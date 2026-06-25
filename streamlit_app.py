import os
import sys
import subprocess
import streamlit as st

# FORCE PLAYWRIGHT TO INSTALL ON THE CLOUD SERVER ONCE AT STARTUP
@st.cache_resource
def install_browser_binaries():
    try:
        # Runs the official command to download the headless engine
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Binary setup error: {e}")

# Run the installer function
install_browser_binaries()

# ----------------------------------------------------
# Your Main App Logic Starts Here
# ----------------------------------------------------
st.title("Comprehensive Deep Diagnostic Scan")

if st.button("Execute Comprehensive Deep Diagnostic Scan"):
    st.info("Scanner initialized. Running task...")
    
    # IMPORTANT: Import your automation libraries *INSIDE* the button 
    # to guarantee they don't fire until after the installer above finishes.
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Launch the headless shell safely
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://example.com")
            st.success(f"Successfully reached target! Title: {page.title()}")
            browser.close()
            
    except Exception as error:
        st.error(f"Execution Error: {error}")
