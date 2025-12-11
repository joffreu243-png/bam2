#!/usr/bin/env python3
"""
Browser Automator Pro v5.0
Hi-Tech Edition with NiceGUI

Usage:
    python main.py          # Run NiceGUI version (default)
    python main.py --legacy # Run old CustomTkinter version
"""

import sys
from pathlib import Path

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent))


def run_nicegui():
    """Run modern NiceGUI version"""
    print("=" * 70)
    print("⚡ BROWSER AUTOMATOR PRO v5.0 | HI-TECH EDITION")
    print("=" * 70)
    print("🌐 Powered by NiceGUI (Web-based interface)")
    print("🎨 Hi-Tech Design: Sharp corners, shadows, cyber colors")
    print("🚀 Smooth performance, no lag")
    print("📍 Opening in browser (random port)")
    print("=" * 70)
    print()

    from src.gui.nicegui_app import main
    main()


def run_legacy():
    """Run legacy CustomTkinter version"""
    print("=" * 70)
    print("🚀 auto2tesst v3.0 EPIC - Legacy Mode")
    print("=" * 70)
    print("✨ Powered by CustomTkinter")
    print("=" * 70)
    print()

    from src.gui.modern_main_window_v3 import main
    main()


if __name__ == "__main__":
    try:
        if '--legacy' in sys.argv or '--old' in sys.argv:
            run_legacy()
        else:
            run_nicegui()
    except KeyboardInterrupt:
        print("\n✋ Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
