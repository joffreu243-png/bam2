"""
Browser Automator Pro v5.0 - NiceGUI Edition
Hi-Tech Design with Sharp Corners & Shadows
"""

from nicegui import ui, app
import json
import os
import sys
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.octobrowser_api import OctobrowserAPI
from src.utils.script_parser import ScriptParser
from src.utils.data_parser import SmartDataParser


# ============================================================================
# HI-TECH THEME - Sharp corners, shadows, cyber colors
# ============================================================================

HITECH_CSS = """
/* === GLOBAL HI-TECH STYLE === */
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-tertiary: #1a1a25;
    --bg-card: #15151f;
    --text-primary: #e0e0e5;
    --text-secondary: #8888a0;
    --accent-primary: #00d4ff;
    --accent-secondary: #0099cc;
    --accent-success: #00ff88;
    --accent-warning: #ffcc00;
    --accent-error: #ff4466;
    --border-color: #2a2a3a;
    --shadow-glow: rgba(0, 212, 255, 0.15);
}

body {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
}

/* No rounded corners - sharp edges */
.q-card, .q-btn, .q-input, .q-field, .q-tab-panel, .q-tabs, .q-tab,
.nicegui-input, .nicegui-button, .nicegui-card, .nicegui-textarea {
    border-radius: 0 !important;
}

/* Card styling with shadow */
.hitech-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5),
                0 0 40px var(--shadow-glow) !important;
    border-radius: 0 !important;
}

/* Glow effect on hover */
.hitech-card:hover {
    box-shadow: 0 6px 30px rgba(0, 0, 0, 0.6),
                0 0 60px var(--shadow-glow) !important;
    border-color: var(--accent-primary) !important;
}

/* Button styles */
.hitech-btn {
    background: linear-gradient(180deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
    text-transform: none !important;
    font-weight: 500 !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
    border-radius: 0 !important;
}

.hitech-btn:hover {
    background: linear-gradient(180deg, var(--bg-tertiary) 0%, #252535 100%) !important;
    border-color: var(--accent-primary) !important;
    box-shadow: 0 2px 15px rgba(0, 212, 255, 0.3) !important;
}

.hitech-btn-primary {
    background: linear-gradient(180deg, var(--accent-primary) 0%, var(--accent-secondary) 100%) !important;
    border: none !important;
    color: #000 !important;
    font-weight: 600 !important;
}

.hitech-btn-primary:hover {
    background: linear-gradient(180deg, #00e5ff 0%, var(--accent-primary) 100%) !important;
    box-shadow: 0 0 25px rgba(0, 212, 255, 0.5) !important;
}

.hitech-btn-success {
    background: linear-gradient(180deg, var(--accent-success) 0%, #00cc66 100%) !important;
    border: none !important;
    color: #000 !important;
}

.hitech-btn-danger {
    background: linear-gradient(180deg, var(--accent-error) 0%, #cc3355 100%) !important;
    border: none !important;
    color: #fff !important;
}

/* Input styling */
.hitech-input .q-field__control {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 0 !important;
}

.hitech-input .q-field__control:focus-within {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.2) !important;
}

.hitech-input input, .hitech-input textarea {
    color: var(--text-primary) !important;
    caret-color: var(--accent-primary) !important;
}

/* Tabs styling */
.hitech-tabs {
    background: var(--bg-secondary) !important;
    border-bottom: 2px solid var(--border-color) !important;
}

.hitech-tabs .q-tab {
    color: var(--text-secondary) !important;
    border-radius: 0 !important;
}

.hitech-tabs .q-tab--active {
    color: var(--accent-primary) !important;
    background: var(--bg-tertiary) !important;
}

.hitech-tabs .q-tab__indicator {
    background: var(--accent-primary) !important;
    height: 3px !important;
}

/* Code editor */
.hitech-code {
    background: #0d0d12 !important;
    border: 1px solid var(--border-color) !important;
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
    color: #e0e0e5 !important;
}

.hitech-code:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.15) !important;
}

/* Sidebar styling */
.hitech-sidebar {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-color) !important;
}

/* Thread cards */
.thread-card {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border-color) !important;
    padding: 12px !important;
    margin-bottom: 8px !important;
    transition: all 0.2s ease !important;
}

.thread-card:hover {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.2) !important;
}

/* Status indicators */
.status-running {
    color: var(--accent-success) !important;
    text-shadow: 0 0 10px var(--accent-success) !important;
}

.status-pending {
    color: var(--text-secondary) !important;
}

.status-error {
    color: var(--accent-error) !important;
    text-shadow: 0 0 10px var(--accent-error) !important;
}

/* Progress bar */
.hitech-progress {
    background: var(--bg-secondary) !important;
    height: 4px !important;
    border-radius: 0 !important;
}

.hitech-progress .q-linear-progress__track {
    background: var(--bg-tertiary) !important;
}

.hitech-progress .q-linear-progress__model {
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-success)) !important;
}

/* Log viewer */
.log-viewer {
    background: #08080c !important;
    border: 1px solid var(--border-color) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    color: var(--text-secondary) !important;
}

.log-success { color: var(--accent-success) !important; }
.log-error { color: var(--accent-error) !important; }
.log-warning { color: var(--accent-warning) !important; }
.log-info { color: var(--accent-primary) !important; }

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-primary);
}

/* Select/Dropdown styling */
.hitech-select .q-field__control {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 0 !important;
}

/* Panel header */
.panel-header {
    background: linear-gradient(180deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%) !important;
    border-bottom: 1px solid var(--border-color) !important;
    padding: 16px 20px !important;
}

/* Glowing text effect */
.glow-text {
    text-shadow: 0 0 10px var(--accent-primary), 0 0 20px var(--accent-primary) !important;
}

/* Animated border effect */
@keyframes border-glow {
    0%, 100% { border-color: var(--border-color); }
    50% { border-color: var(--accent-primary); }
}

.animate-border {
    animation: border-glow 2s ease-in-out infinite;
}
"""


class BrowserAutomatorApp:
    """Browser Automator Pro v5.0 - NiceGUI Edition"""

    def __init__(self):
        self.config = {}
        self.api: Optional[OctobrowserAPI] = None
        self.parser = ScriptParser()
        self.data_parser = SmartDataParser()

        # State
        self.threads_data: Dict[str, dict] = {}
        self.running_process = None
        self.current_provider = 'smart_wf'
        self.csv_data_rows = []
        self.log_entries: List[str] = []

        # UI references
        self.code_editor = None
        self.output_area = None
        self.threads_container = None
        self.stats_labels = {}

        # Load config
        self.load_config()

    def load_config(self):
        """Load configuration from config.json"""
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                'octobrowser': {'api_base_url': 'https://app.octobrowser.net/api/v2/automation', 'api_token': ''},
                'sms': {'provider': 'daisysms', 'api_key': '', 'service': 'ds'},
                'proxy': {'enabled': False, 'type': 'http', 'host': '', 'port': '', 'login': '', 'password': ''},
                'script_settings': {'output_directory': 'generated_scripts'}
            }

    def save_config(self):
        """Save configuration to config.json"""
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            ui.notify('Settings saved', type='positive')
        except Exception as e:
            ui.notify(f'Error saving: {e}', type='negative')

    def discover_providers(self) -> List[str]:
        """Auto-discover providers from src/providers/"""
        providers_dir = Path(__file__).parent.parent / 'providers'
        if not providers_dir.exists():
            return ['default_no_otp']
        providers = []
        for item in providers_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                if (item / 'generator.py').exists() and (item / 'runner.py').exists():
                    providers.append(item.name)
        return sorted(providers) if providers else ['default_no_otp']

    def build_ui(self):
        """Build the main UI"""
        # Add custom CSS
        ui.add_head_html(f'<style>{HITECH_CSS}</style>')
        ui.add_head_html('<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">')

        # Main container
        with ui.column().classes('w-full h-screen').style('background: #0a0a0f; padding: 0; margin: 0;'):
            self._build_header()

            with ui.row().classes('w-full flex-grow').style('height: calc(100vh - 70px);'):
                self._build_sidebar()
                self._build_main_content()

    def _build_header(self):
        """Build the top header bar"""
        with ui.row().classes('w-full items-center justify-between').style(
            'background: linear-gradient(180deg, #15151f 0%, #12121a 100%); '
            'border-bottom: 1px solid #2a2a3a; padding: 12px 24px; height: 70px;'
        ):
            # Logo & Title
            with ui.row().classes('items-center gap-4'):
                ui.label('⚡').classes('text-3xl')
                with ui.column().classes('gap-0'):
                    ui.label('BROWSER AUTOMATOR').classes('text-lg font-bold').style('color: #00d4ff; letter-spacing: 2px;')
                    ui.label('PRO v5.0 | HI-TECH EDITION').classes('text-xs').style('color: #8888a0; letter-spacing: 1px;')

            # Stats
            with ui.row().classes('items-center gap-6'):
                # Threads count
                with ui.row().classes('items-center gap-2').style('background: #1a1a25; padding: 8px 16px; border: 1px solid #2a2a3a;'):
                    self.stats_labels['indicator'] = ui.label('●').style('color: #666;')
                    self.stats_labels['threads'] = ui.label('THREADS: 0').style('color: #e0e0e5; font-size: 12px;')

                # Active count
                with ui.row().classes('items-center gap-2').style('background: #1a1a25; padding: 8px 16px; border: 1px solid #2a2a3a;'):
                    self.stats_labels['active'] = ui.label('ACTIVE: 0').style('color: #00ff88; font-size: 12px;')

                # Variables
                with ui.row().classes('items-center gap-2').style('background: #1a1a25; padding: 8px 16px; border: 1px solid #2a2a3a;'):
                    self.stats_labels['variables'] = ui.label('VARS: 0').style('color: #00d4ff; font-size: 12px;')

            # Theme toggle (placeholder)
            ui.button('◐', on_click=lambda: ui.notify('Theme toggle')).classes('hitech-btn').style('width: 40px; height: 40px;')

    def _build_sidebar(self):
        """Build the left sidebar with threads"""
        with ui.column().classes('hitech-sidebar').style('width: 280px; height: 100%; padding: 0;'):
            # Header
            with ui.row().classes('w-full items-center justify-between panel-header'):
                ui.label('THREADS').style('color: #e0e0e5; font-weight: 600; letter-spacing: 1px;')
                ui.button('CLEAR', on_click=self.clear_threads).classes('hitech-btn-danger').style('font-size: 10px; padding: 4px 12px;')

            # Threads list
            with ui.scroll_area().classes('flex-grow').style('padding: 12px;'):
                self.threads_container = ui.column().classes('w-full gap-2')
                self._update_threads_display()

            # Stop all button
            with ui.column().classes('w-full').style('padding: 12px; border-top: 1px solid #2a2a3a;'):
                ui.button('⏹ STOP ALL', on_click=self.stop_all).classes('hitech-btn-danger w-full').style('height: 44px; font-weight: 600;')
                ui.label('✨ Ready to automate').style('color: #8888a0; font-size: 11px; margin-top: 8px;')

    def _build_main_content(self):
        """Build the main content area with tabs"""
        with ui.column().classes('flex-grow').style('background: #0a0a0f; height: 100%;'):
            with ui.tabs().classes('hitech-tabs w-full') as tabs:
                launch_tab = ui.tab('🚀 LAUNCH')
                recorder_tab = ui.tab('📹 RECORDER')
                script_tab = ui.tab('📝 SCRIPT')
                data_tab = ui.tab('📊 DATA')
                settings_tab = ui.tab('⚙️ SETTINGS')
                logs_tab = ui.tab('📋 LOGS')

            with ui.tab_panels(tabs, value=launch_tab).classes('w-full flex-grow').style('background: #0a0a0f;'):
                with ui.tab_panel(launch_tab).style('padding: 20px;'):
                    self._build_launch_tab()

                with ui.tab_panel(recorder_tab).style('padding: 20px;'):
                    self._build_recorder_tab()

                with ui.tab_panel(script_tab).style('padding: 20px;'):
                    self._build_script_tab()

                with ui.tab_panel(data_tab).style('padding: 20px;'):
                    self._build_data_tab()

                with ui.tab_panel(settings_tab).style('padding: 20px;'):
                    self._build_settings_tab()

                with ui.tab_panel(logs_tab).style('padding: 20px;'):
                    self._build_logs_tab()

    def _build_launch_tab(self):
        """Build the main launch tab"""
        # Top control panel
        with ui.row().classes('w-full items-center gap-4 hitech-card').style('padding: 16px 20px; margin-bottom: 16px;'):
            # Thread count
            with ui.row().classes('items-center gap-2'):
                ui.label('THREADS:').style('color: #8888a0; font-size: 12px;')
                self.threads_input = ui.number(value=1, min=1, max=100).classes('hitech-input').style('width: 80px;')

            # Provider selector
            with ui.row().classes('items-center gap-2'):
                ui.label('PROVIDER:').style('color: #8888a0; font-size: 12px;')
                providers = self.discover_providers()
                self.provider_select = ui.select(options=providers, value=providers[0] if providers else 'default').classes('hitech-select').style('width: 180px;')

            ui.space()

            # Action buttons
            ui.button('🚀 RUN', on_click=self.run_script).classes('hitech-btn-primary').style('height: 40px; padding: 0 24px; font-weight: 600;')
            ui.button('⏹ TEST (1)', on_click=lambda: self.run_script(test=True)).classes('hitech-btn').style('height: 40px; padding: 0 20px;')

        # Main content - two columns
        with ui.row().classes('w-full gap-4').style('height: calc(100% - 90px);'):
            # Left: Code editor
            with ui.column().classes('hitech-card').style('flex: 6; height: 100%; padding: 0;'):
                # Code header
                with ui.row().classes('w-full items-center justify-between panel-header'):
                    ui.label('📝 AUTOMATION CODE').style('color: #e0e0e5; font-weight: 600;')
                    with ui.row().classes('gap-2'):
                        ui.button('📂 Load', on_click=self.load_script).classes('hitech-btn').style('font-size: 11px;')
                        ui.button('📋 Paste', on_click=self.paste_clipboard).classes('hitech-btn').style('font-size: 11px;')
                        ui.button('✨ Generate', on_click=self.generate_script).classes('hitech-btn-primary').style('font-size: 11px;')

                # Code editor
                self.code_editor = ui.textarea(
                    value='# Your Playwright automation code here\n\nasync def main(page, data):\n    await page.goto("https://example.com")\n    # Your code...\n',
                    placeholder='Enter your automation code here...'
                ).classes('hitech-code w-full flex-grow').style('min-height: 400px; resize: none;')

            # Right: Settings panel
            with ui.scroll_area().classes('hitech-card').style('flex: 4; height: 100%; padding: 0;'):
                with ui.column().classes('w-full gap-4').style('padding: 16px;'):
                    # Red Flags section
                    with ui.column().classes('w-full gap-2'):
                        with ui.row().classes('items-center gap-2'):
                            ui.label('🚩').style('font-size: 18px;')
                            ui.label('RED FLAGS').style('color: #ff4466; font-weight: 600; letter-spacing: 1px;')
                        ui.label('Auto-close patterns (one per line)').style('color: #8888a0; font-size: 11px;')
                        self.red_flags_input = ui.textarea(
                            value='suspicious activity\naccount blocked\nverification required',
                            placeholder='Enter patterns to auto-close...'
                        ).classes('hitech-code w-full').style('height: 120px; font-size: 11px;')

                    ui.separator().style('background: #2a2a3a;')

                    # Proxy settings
                    with ui.column().classes('w-full gap-2'):
                        with ui.row().classes('items-center gap-2'):
                            ui.label('🌐').style('font-size: 18px;')
                            ui.label('PROXY SETTINGS').style('color: #00d4ff; font-weight: 600; letter-spacing: 1px;')

                        with ui.row().classes('w-full gap-2'):
                            ui.checkbox('Enable Proxy').style('color: #e0e0e5;')

                        self.proxy_input = ui.input(
                            placeholder='host:port:user:pass'
                        ).classes('hitech-input w-full').style('font-size: 12px;')

                        ui.button('📂 Load Proxy List', on_click=self.load_proxy_list).classes('hitech-btn w-full').style('font-size: 11px;')

                    ui.separator().style('background: #2a2a3a;')

                    # Timing settings
                    with ui.column().classes('w-full gap-2'):
                        with ui.row().classes('items-center gap-2'):
                            ui.label('⏱').style('font-size: 18px;')
                            ui.label('TIMING').style('color: #ffcc00; font-weight: 600; letter-spacing: 1px;')

                        with ui.row().classes('w-full gap-4'):
                            with ui.column().classes('flex-1 gap-1'):
                                ui.label('Action Delay (ms)').style('color: #8888a0; font-size: 10px;')
                                ui.number(value=1000, min=100, max=10000).classes('hitech-input w-full')
                            with ui.column().classes('flex-1 gap-1'):
                                ui.label('Page Timeout (s)').style('color: #8888a0; font-size: 10px;')
                                ui.number(value=30, min=5, max=120).classes('hitech-input w-full')

                    ui.separator().style('background: #2a2a3a;')

                    # Quick actions
                    with ui.column().classes('w-full gap-2'):
                        ui.label('QUICK ACTIONS').style('color: #8888a0; font-weight: 600; font-size: 11px;')
                        with ui.row().classes('w-full gap-2'):
                            ui.button('💾 Save', on_click=self.save_script).classes('hitech-btn flex-1').style('font-size: 11px;')
                            ui.button('🗑 Clear', on_click=self.clear_editor).classes('hitech-btn flex-1').style('font-size: 11px;')

    def _build_recorder_tab(self):
        """Build the recorder tab"""
        with ui.column().classes('w-full h-full items-center justify-center gap-4'):
            ui.label('📹').style('font-size: 64px;')
            ui.label('ACTION RECORDER').style('color: #00d4ff; font-size: 24px; font-weight: 600; letter-spacing: 2px;')
            ui.label('Record browser actions and convert to automation code').style('color: #8888a0;')
            with ui.row().classes('gap-4 mt-4'):
                ui.button('▶ START RECORDING', on_click=lambda: ui.notify('Recording started')).classes('hitech-btn-primary').style('height: 50px; padding: 0 32px;')
                ui.button('⏹ STOP', on_click=lambda: ui.notify('Recording stopped')).classes('hitech-btn-danger').style('height: 50px; padding: 0 24px;')

    def _build_script_tab(self):
        """Build the generated script tab"""
        with ui.column().classes('w-full h-full gap-4'):
            with ui.row().classes('w-full items-center justify-between'):
                ui.label('GENERATED SCRIPT').style('color: #e0e0e5; font-weight: 600; letter-spacing: 1px;')
                with ui.row().classes('gap-2'):
                    ui.button('📋 Copy', on_click=self.copy_generated).classes('hitech-btn')
                    ui.button('💾 Export', on_click=self.export_script).classes('hitech-btn-primary')

            self.generated_script_area = ui.textarea(
                value='# Generated script will appear here...',
                placeholder='Generated automation script...'
            ).classes('hitech-code w-full flex-grow').style('min-height: 500px;')

    def _build_data_tab(self):
        """Build the data/variables tab"""
        with ui.column().classes('w-full h-full gap-4'):
            # Import section
            with ui.row().classes('w-full items-center gap-4 hitech-card').style('padding: 16px;'):
                ui.label('📊 DATA IMPORT').style('color: #e0e0e5; font-weight: 600;')
                ui.space()
                ui.button('📂 Import CSV', on_click=self.import_csv).classes('hitech-btn')
                ui.button('📂 Import Excel', on_click=self.import_excel).classes('hitech-btn')
                ui.button('✨ Generate Fake', on_click=self.generate_fake_data).classes('hitech-btn-primary')

            # Data table
            with ui.column().classes('hitech-card w-full flex-grow').style('padding: 16px;'):
                ui.label('LOADED DATA').style('color: #8888a0; font-size: 12px; margin-bottom: 8px;')
                self.data_table_container = ui.column().classes('w-full')
                self._build_empty_data_table()

    def _build_empty_data_table(self):
        """Build empty data table placeholder"""
        self.data_table_container.clear()
        with self.data_table_container:
            with ui.column().classes('w-full items-center justify-center').style('padding: 60px;'):
                ui.label('📊').style('font-size: 48px; opacity: 0.5;')
                ui.label('No data loaded').style('color: #8888a0;')
                ui.label('Import CSV/Excel or generate fake data').style('color: #666; font-size: 12px;')

    def _build_settings_tab(self):
        """Build the settings tab"""
        with ui.scroll_area().classes('w-full h-full'):
            with ui.column().classes('w-full gap-6').style('padding: 20px; max-width: 800px;'):
                # API Settings
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('⚙️ OCTOBROWSER API').style('color: #00d4ff; font-weight: 600; letter-spacing: 1px;')

                    ui.label('API Token').style('color: #8888a0; font-size: 12px;')
                    self.api_token_input = ui.input(
                        value=self.config.get('octobrowser', {}).get('api_token', ''),
                        password=True,
                        placeholder='Enter your API token'
                    ).classes('hitech-input w-full')

                    with ui.row().classes('gap-2'):
                        ui.button('💾 Save', on_click=self.save_api_settings).classes('hitech-btn-primary')
                        ui.button('🔗 Test Connection', on_click=self.test_api_connection).classes('hitech-btn')

                # Profile Settings
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('👤 PROFILE SETTINGS').style('color: #00ff88; font-weight: 600; letter-spacing: 1px;')

                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Default Tags').style('color: #8888a0; font-size: 12px;')
                            ui.input(placeholder='tag1, tag2, tag3').classes('hitech-input w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Profile Notes').style('color: #8888a0; font-size: 12px;')
                            ui.input(placeholder='Auto-generated profile').classes('hitech-input w-full')

                # Fingerprint Settings
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('🎭 FINGERPRINT').style('color: #ffcc00; font-weight: 600; letter-spacing: 1px;')

                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Operating System').style('color: #8888a0; font-size: 12px;')
                            ui.select(options=['Windows', 'macOS', 'Linux'], value='Windows').classes('hitech-select w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('WebRTC').style('color: #8888a0; font-size: 12px;')
                            ui.select(options=['Altered', 'Disabled', 'Real'], value='Altered').classes('hitech-select w-full')

                    with ui.row().classes('w-full gap-4'):
                        ui.checkbox('Canvas Protection', value=True).style('color: #e0e0e5;')
                        ui.checkbox('WebGL Protection', value=True).style('color: #e0e0e5;')
                        ui.checkbox('Fonts Protection', value=True).style('color: #e0e0e5;')

    def _build_logs_tab(self):
        """Build the logs tab"""
        with ui.column().classes('w-full h-full gap-4'):
            with ui.row().classes('w-full items-center justify-between'):
                ui.label('📋 EXECUTION LOGS').style('color: #e0e0e5; font-weight: 600;')
                with ui.row().classes('gap-2'):
                    ui.button('🗑 Clear', on_click=self.clear_logs).classes('hitech-btn')
                    ui.button('💾 Export', on_click=self.export_logs).classes('hitech-btn')

            self.output_area = ui.textarea(
                value='[System] Ready to execute...\n',
                placeholder='Logs will appear here...'
            ).classes('log-viewer w-full flex-grow').style('min-height: 500px; resize: none;')

    def _update_threads_display(self):
        """Update the threads display in sidebar"""
        if not self.threads_container:
            return

        self.threads_container.clear()

        with self.threads_container:
            if not self.threads_data:
                # Empty state
                with ui.column().classes('w-full items-center').style('padding: 40px 20px;'):
                    ui.label('🚀').style('font-size: 48px; opacity: 0.5;')
                    ui.label('No active threads').style('color: #8888a0; font-weight: 600;')
                    ui.label('Configure and run from LAUNCH tab').style('color: #666; font-size: 11px; text-align: center;')
            else:
                for thread_id, data in self.threads_data.items():
                    self._create_thread_card(thread_id, data)

        # Update stats
        total = len(self.threads_data)
        active = sum(1 for t in self.threads_data.values() if t.get('status') == 'running')

        if 'threads' in self.stats_labels:
            self.stats_labels['threads'].set_text(f'THREADS: {total}')
        if 'active' in self.stats_labels:
            self.stats_labels['active'].set_text(f'ACTIVE: {active}')
        if 'indicator' in self.stats_labels:
            color = '#00ff88' if active > 0 else '#666'
            self.stats_labels['indicator'].style(f'color: {color};')

    def _create_thread_card(self, thread_id: str, data: dict):
        """Create a thread card in the sidebar"""
        status = data.get('status', 'pending')
        progress = data.get('progress', 0)

        status_colors = {
            'pending': '#8888a0',
            'running': '#00ff88',
            'completed': '#00d4ff',
            'error': '#ff4466'
        }
        color = status_colors.get(status, '#8888a0')

        with ui.column().classes('thread-card w-full'):
            with ui.row().classes('w-full items-center gap-3'):
                ui.label('●').style(f'color: {color}; font-size: 12px;')
                with ui.column().classes('flex-grow gap-0'):
                    ui.label(f'Thread #{thread_id}').style('color: #e0e0e5; font-size: 12px; font-weight: 600;')
                    ui.label(status.upper()).style(f'color: {color}; font-size: 10px;')

            if status == 'running':
                ui.linear_progress(value=progress).classes('hitech-progress w-full').style('margin-top: 8px;')

    # ========== Action Methods ==========

    def run_script(self, test: bool = False):
        """Run the automation script"""
        threads = 1 if test else int(self.threads_input.value or 1)

        # Add threads
        for i in range(threads):
            thread_id = str(len(self.threads_data) + 1)
            self.threads_data[thread_id] = {'status': 'running', 'progress': 0.3, 'logs': []}

        self._update_threads_display()

        self.add_log(f'[System] Starting {threads} thread(s)...', 'info')
        ui.notify(f'Started {threads} thread(s)', type='positive')

        # TODO: Actual script execution

    def stop_all(self):
        """Stop all running threads"""
        for thread_id in self.threads_data:
            self.threads_data[thread_id]['status'] = 'completed'
        self._update_threads_display()
        self.add_log('[System] All threads stopped', 'warning')
        ui.notify('All threads stopped', type='warning')

    def clear_threads(self):
        """Clear all threads"""
        self.threads_data.clear()
        self._update_threads_display()
        ui.notify('Threads cleared', type='info')

    def add_log(self, message: str, level: str = 'info'):
        """Add a log entry"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f'[{timestamp}] {message}'
        self.log_entries.append(log_entry)

        if self.output_area:
            current = self.output_area.value
            self.output_area.set_value(current + log_entry + '\n')

    def clear_logs(self):
        """Clear all logs"""
        self.log_entries.clear()
        if self.output_area:
            self.output_area.set_value('[System] Logs cleared\n')
        ui.notify('Logs cleared', type='info')

    def export_logs(self):
        """Export logs to file"""
        ui.notify('Export logs (not implemented)', type='info')

    def load_script(self):
        """Load script from file"""
        ui.notify('Load script (not implemented)', type='info')

    def paste_clipboard(self):
        """Paste from clipboard"""
        ui.notify('Paste from clipboard (not implemented)', type='info')

    def generate_script(self):
        """Generate automation script"""
        if self.code_editor:
            code = self.code_editor.value
            # TODO: Generate full script
            if hasattr(self, 'generated_script_area'):
                self.generated_script_area.set_value(f'# Generated script\n\n{code}')
            ui.notify('Script generated', type='positive')

    def save_script(self):
        """Save script to file"""
        ui.notify('Save script (not implemented)', type='info')

    def clear_editor(self):
        """Clear the code editor"""
        if self.code_editor:
            self.code_editor.set_value('# Your automation code here\n\nasync def main(page, data):\n    pass\n')
        ui.notify('Editor cleared', type='info')

    def copy_generated(self):
        """Copy generated script to clipboard"""
        ui.notify('Copy to clipboard (not implemented)', type='info')

    def export_script(self):
        """Export script to file"""
        ui.notify('Export script (not implemented)', type='info')

    def import_csv(self):
        """Import CSV data"""
        ui.notify('Import CSV (not implemented)', type='info')

    def import_excel(self):
        """Import Excel data"""
        ui.notify('Import Excel (not implemented)', type='info')

    def generate_fake_data(self):
        """Generate fake data using Faker"""
        ui.notify('Generate fake data (not implemented)', type='info')

    def load_proxy_list(self):
        """Load proxy list from file"""
        ui.notify('Load proxy list (not implemented)', type='info')

    def save_api_settings(self):
        """Save API settings"""
        if self.api_token_input:
            self.config.setdefault('octobrowser', {})['api_token'] = self.api_token_input.value
            self.save_config()

    def test_api_connection(self):
        """Test API connection"""
        token = self.config.get('octobrowser', {}).get('api_token', '')
        if not token:
            ui.notify('Please enter API token first', type='negative')
            return

        try:
            self.api = OctobrowserAPI(token)
            profiles = self.api.get_profiles()
            ui.notify(f'Connected! Found {len(profiles)} profiles', type='positive')
        except Exception as e:
            ui.notify(f'Connection failed: {e}', type='negative')


def main():
    """Main entry point"""
    app_instance = BrowserAutomatorApp()
    app_instance.build_ui()
    ui.run(
        title='Browser Automator Pro v5.0',
        port=0,  # Random available port
        reload=False,
        show=True,
        dark=True
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
