import os
import subprocess
import streamlit as st


# 1. RUN PLAYWRIGHT SETUP ONCE BEFORE THE APP LOADS
@st.cache_resource
def initialize_playwright():
    try:
        # Check if browser is installed by executing a test command or forcing installation
        # This will install Chromium and its internal Linux dependencies on the container
        subprocess.run(["playwright", "install", "chromium"], check=True)
        subprocess.run(["playwright", "install-deps"], check=True)
        return True
    except Exception as e:
        st.error(f"Error initializing browser binaries: {e}")
        return False


# Trigger the browser setup
playwright_ready = initialize_playwright()

# 2. YOUR MAIN APP CODE STARTS HERE
st.title("Comprehensive Deep Diagnostic Scan")

if playwright_ready:
    st.success("App environment initialized successfully!")

    # --- Put the rest of your original code here ---
    # For example:
    if st.button("Execute Comprehensive Deep Diagnostic Scan"):
        st.info("Scanning started...")
        # Your web scraping or diagnostic logic runs here...
else:
    st.error("The app could not start because the browser dependencies are missing.")