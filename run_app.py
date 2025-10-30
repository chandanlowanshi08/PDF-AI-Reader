#!/usr/bin/env python3
"""
PDF Assistant Frontend Launcher
Run this script to start the Streamlit web application
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit PDF Assistant app"""
    print("🚀 Starting PDF Assistant Frontend...")
    print("📄 Make sure you have set up your GROQ_API_KEY in a .env file")
    print("🌐 The app will open in your default web browser")
    print("-" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("   Please create a .env file with your GROQ_API_KEY")
        print("   Example: GROQ_API_KEY=your_api_key_here")
        print()
    
    try:
        # Launch Streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 PDF Assistant stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching app: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
