import os
import subprocess
import streamlit as st

# Automatically install Playwright browsers if they are missing
@st.cache_resource
def install_playwright_browsers():
    try:
        # Check if the browser is available, if not, install it
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Failed to install browser binaries: {e}")

install_playwright_browsers()