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
        self.config_path = Path(__file__).parent.parent.parent / 'config.json'
        self.api: Optional[OctobrowserAPI] = None
        self.parser = ScriptParser()
        self.data_parser = SmartDataParser()

        # State
        self.iterations_data: Dict[str, dict] = {}  # Iteration ID -> {status, progress, logs}
        self.running_process = None
        self.current_provider = 'smart_wf'
        self.csv_data_rows = []
        self.log_entries: List[str] = []

        # UI references
        self.code_editor = None
        self.output_area = None
        self.iterations_container = None
        self.stats_labels = {}

        # Script runner
        self.current_runner = None

        # Load config
        self.load_config()

    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                'octobrowser': {'api_base_url': 'https://app.octobrowser.net/api/v2/automation', 'api_token': ''},
                'sms': {'provider': 'daisysms', 'api_key': '', 'service': 'ds'},
                'proxy': {'enabled': False, 'type': 'socks5', 'host': '', 'port': '', 'login': '', 'password': ''},
                'proxy_list': {'proxies': [], 'rotation_mode': 'random', 'default_type': 'socks5'},
                'script_settings': {'output_directory': 'generated_scripts'}
            }

    def save_config(self):
        """Save configuration to config.json"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
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
                    self.stats_labels['iterations'] = ui.label('ITERATIONS: 0').style('color: #e0e0e5; font-size: 12px;')

                # Active count
                with ui.row().classes('items-center gap-2').style('background: #1a1a25; padding: 8px 16px; border: 1px solid #2a2a3a;'):
                    self.stats_labels['active'] = ui.label('ACTIVE: 0').style('color: #00ff88; font-size: 12px;')

                # Variables
                with ui.row().classes('items-center gap-2').style('background: #1a1a25; padding: 8px 16px; border: 1px solid #2a2a3a;'):
                    self.stats_labels['variables'] = ui.label('VARS: 0').style('color: #00d4ff; font-size: 12px;')

            # Theme toggle (placeholder)
            ui.button('◐', on_click=lambda: ui.notify('Theme toggle')).classes('hitech-btn').style('width: 40px; height: 40px;')

    def _build_sidebar(self):
        """Build the left sidebar with iterations"""
        with ui.column().classes('hitech-sidebar').style('width: 280px; height: 100%; padding: 0;'):
            # Header
            with ui.row().classes('w-full items-center justify-between panel-header'):
                ui.label('ITERATIONS').style('color: #e0e0e5; font-weight: 600; letter-spacing: 1px;')
                ui.button('CLEAR', on_click=self.clear_iterations).classes('hitech-btn-danger').style('font-size: 10px; padding: 4px 12px;')

            # Iterations list
            with ui.scroll_area().classes('flex-grow').style('padding: 12px;'):
                self.iterations_container = ui.column().classes('w-full gap-2')
                self._update_iterations_display()

            # Stop all button
            with ui.column().classes('w-full').style('padding: 12px; border-top: 1px solid #2a2a3a;'):
                ui.button('⏹ STOP ALL', on_click=self.stop_all).classes('hitech-btn-danger w-full').style('height: 44px; font-weight: 600;')
                ui.label('✨ Ready to automate').style('color: #8888a0; font-size: 11px; margin-top: 8px;')

    def _build_main_content(self):
        """Build the main content area with tabs"""
        with ui.column().classes('flex-grow').style('background: #0a0a0f; height: 100%;'):
            with ui.tabs().classes('hitech-tabs w-full') as tabs:
                launch_tab = ui.tab('🚀 LAUNCH')
                script_tab = ui.tab('📝 SCRIPT')
                data_tab = ui.tab('📊 DATA')
                proxy_tab = ui.tab('🌐 PROXY')
                captcha_tab = ui.tab('🔓 CAPTCHA')
                settings_tab = ui.tab('⚙️ SETTINGS')
                logs_tab = ui.tab('📋 LOGS')

            with ui.tab_panels(tabs, value=launch_tab).classes('w-full flex-grow').style('background: #0a0a0f;'):
                with ui.tab_panel(launch_tab).style('padding: 20px;'):
                    self._build_launch_tab()

                with ui.tab_panel(script_tab).style('padding: 20px;'):
                    self._build_script_tab()

                with ui.tab_panel(data_tab).style('padding: 20px;'):
                    self._build_data_tab()

                with ui.tab_panel(proxy_tab).style('padding: 20px;'):
                    self._build_proxy_tab()

                with ui.tab_panel(captcha_tab).style('padding: 20px;'):
                    self._build_captcha_tab()

                with ui.tab_panel(settings_tab).style('padding: 20px;'):
                    self._build_settings_tab()

                with ui.tab_panel(logs_tab).style('padding: 20px;'):
                    self._build_logs_tab()

    def _build_launch_tab(self):
        """Build the main launch tab"""
        # Top control panel
        with ui.row().classes('w-full items-center gap-4 hitech-card').style('padding: 16px 20px; margin-bottom: 16px;'):
            # Browser mode selector
            with ui.row().classes('items-center gap-2'):
                ui.label('BROWSER:').style('color: #8888a0; font-size: 12px;')
                self.browser_mode_select = ui.select(
                    options=['Local Chromium', 'Octobrowser API'],
                    value='Local Chromium'
                ).classes('hitech-select').style('width: 160px;')

            # Thread count
            with ui.row().classes('items-center gap-2'):
                ui.label('THREADS:').style('color: #8888a0; font-size: 12px;')
                self.threads_input = ui.number(value=1, min=1, max=100).classes('hitech-input').style('width: 80px;')

            # Provider selector
            with ui.row().classes('items-center gap-2'):
                ui.label('PROVIDER:').style('color: #8888a0; font-size: 12px;')
                providers = self.discover_providers()
                default_provider = 'smart_dynamic' if 'smart_dynamic' in providers else (providers[0] if providers else 'default')
                self.provider_select = ui.select(options=providers, value=default_provider).classes('hitech-select').style('width: 180px;')

            # Headless checkbox
            self.headless_checkbox = ui.checkbox('Headless', value=False).style('color: #e0e0e5;')

            # Antidetect checkbox (only for Local Chromium)
            self.antidetect_checkbox = ui.checkbox('🛡️ Antidetect', value=True).style('color: #00ff88;')
            self.antidetect_checkbox.tooltip('Применять реалистичные fingerprints браузера, привязанные к гео прокси')

            ui.space()

            # Action buttons
            ui.button('🚀 RUN', on_click=self.run_script).classes('hitech-btn-primary').style('height: 40px; padding: 0 24px; font-weight: 600;')
            ui.button('⏹ STOP', on_click=self.stop_all).classes('hitech-btn-danger').style('height: 40px; padding: 0 20px;')
            ui.button('🧪 TEST (1)', on_click=lambda: self.run_script(test=True)).classes('hitech-btn').style('height: 40px; padding: 0 20px;')

        # Main content - two columns with fixed height
        with ui.row().classes('w-full gap-4').style('height: calc(100vh - 180px); min-height: 400px;'):
            # Left: Code editor
            with ui.column().classes('hitech-card').style('flex: 6; height: 100%; padding: 0; display: flex; flex-direction: column; overflow: hidden;'):
                # Code header
                with ui.row().classes('w-full items-center justify-between panel-header').style('flex-shrink: 0;'):
                    ui.label('📝 AUTOMATION CODE').style('color: #e0e0e5; font-weight: 600;')
                    with ui.row().classes('gap-2'):
                        ui.button('📂 Load', on_click=self.load_script).classes('hitech-btn').style('font-size: 11px;')
                        ui.button('📋 Paste', on_click=self.paste_clipboard).classes('hitech-btn').style('font-size: 11px;')
                        ui.button('✨ Generate', on_click=self.generate_script).classes('hitech-btn-primary').style('font-size: 11px;')

                # Code editor - fills remaining space with internal scroll
                default_code = '''# Вставьте код из Playwright Recorder или пишите вручную
# Формат: page.goto(), page.get_by_role().click(), page.fill() и т.д.

page.goto("https://example.com")

# Пример заполнения формы:
# page.get_by_label("Email").fill("test@example.com")
# page.get_by_role("button", name="Submit").click()

# Для вопросов используйте формат:
# ### Текст вопроса на странице
# page.get_by_role("button", name="Ответ").click()
'''
                self.code_editor = ui.textarea(
                    value=default_code,
                    placeholder='Вставьте код из Playwright Recorder...'
                ).classes('hitech-code w-full').style('flex: 1; min-height: 0; resize: none; overflow-y: auto;')

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

    def _build_proxy_tab(self):
        """Build the proxy settings tab"""
        with ui.scroll_area().classes('w-full h-full'):
            with ui.column().classes('w-full gap-6').style('padding: 20px; max-width: 1200px;'):

                # === PROXY MODE SELECTOR ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('🌐 PROXY MODE').style('color: #00d4ff; font-weight: 600; letter-spacing: 1px;')

                    with ui.row().classes('w-full gap-4'):
                        self.proxy_mode_select = ui.select(
                            options=['Disabled', 'Single Proxy', 'Proxy List', '9Proxy API'],
                            value=self._get_current_proxy_mode()
                        ).classes('hitech-select').style('width: 200px;')
                        ui.label('Select how proxies will be used').style('color: #8888a0; font-size: 12px; margin-left: 12px;')

                # === SINGLE PROXY ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('📍 SINGLE PROXY').style('color: #00ff88; font-weight: 600; letter-spacing: 1px;')
                    ui.label('Configure a single proxy for all threads').style('color: #8888a0; font-size: 12px;')

                    with ui.row().classes('w-full gap-4 items-center'):
                        self.proxy_enabled_checkbox = ui.checkbox(
                            'Enable',
                            value=self.config.get('proxy', {}).get('enabled', False)
                        ).style('color: #e0e0e5;')

                        with ui.column().classes('w-32 gap-1'):
                            ui.label('Type').style('color: #8888a0; font-size: 11px;')
                            self.proxy_type_select = ui.select(
                                options=['http', 'https', 'socks5'],
                                value=self.config.get('proxy', {}).get('type', 'http')
                            ).classes('hitech-select w-full')

                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('flex-1 gap-1'):
                            ui.label('Host').style('color: #8888a0; font-size: 11px;')
                            self.proxy_host_input = ui.input(
                                value=self.config.get('proxy', {}).get('host', ''),
                                placeholder='proxy.example.com'
                            ).classes('hitech-input w-full')
                        with ui.column().classes('w-24 gap-1'):
                            ui.label('Port').style('color: #8888a0; font-size: 11px;')
                            self.proxy_port_input = ui.input(
                                value=self.config.get('proxy', {}).get('port', ''),
                                placeholder='8080'
                            ).classes('hitech-input w-full')
                        with ui.column().classes('flex-1 gap-1'):
                            ui.label('Login').style('color: #8888a0; font-size: 11px;')
                            self.proxy_login_input = ui.input(
                                value=self.config.get('proxy', {}).get('login', ''),
                                placeholder='username'
                            ).classes('hitech-input w-full')
                        with ui.column().classes('flex-1 gap-1'):
                            ui.label('Password').style('color: #8888a0; font-size: 11px;')
                            self.proxy_password_input = ui.input(
                                value=self.config.get('proxy', {}).get('password', ''),
                                password=True,
                                placeholder='password'
                            ).classes('hitech-input w-full')

                # === PROXY LIST ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label('📋 PROXY LIST').style('color: #ffcc00; font-weight: 600; letter-spacing: 1px;')
                        ui.button('📂 Load from File', on_click=self.load_proxy_list).classes('hitech-btn').style('font-size: 11px;')

                    ui.label('One proxy per line: host:port:user:pass (без type:// = используется Default Type)').style('color: #8888a0; font-size: 12px;')

                    self.proxy_list_input = ui.textarea(
                        value='\n'.join(self.config.get('proxy_list', {}).get('proxies', [])),
                        placeholder='127.0.0.1:6000:user:pass\n192.168.1.1:3128:admin:secret\nsocks5://explicit.proxy.com:1080'
                    ).classes('hitech-code w-full').style('height: 200px; font-family: monospace;')

                    with ui.row().classes('w-full gap-4 items-center'):
                        with ui.column().classes('gap-1'):
                            ui.label('Default Type').style('color: #8888a0; font-size: 11px;')
                            self.proxy_default_type = ui.select(
                                options=['socks5', 'http', 'https'],
                                value=self.config.get('proxy_list', {}).get('default_type', 'socks5')
                            ).classes('hitech-select').style('width: 120px;')
                            ui.label('для прокси без type://').style('color: #666; font-size: 9px;')

                        with ui.column().classes('gap-1'):
                            ui.label('Rotation Mode').style('color: #8888a0; font-size: 11px;')
                            self.proxy_rotation_select = ui.select(
                                options=['sequential', 'random', 'round-robin'],
                                value=self.config.get('proxy_list', {}).get('rotation_mode', 'random')
                            ).classes('hitech-select').style('width: 150px;')

                        self.proxy_retry_checkbox = ui.checkbox(
                            'Retry on Failure',
                            value=self.config.get('proxy_list', {}).get('retry_on_failure', True)
                        ).style('color: #e0e0e5;')

                        ui.space()
                        with ui.row().classes('items-center gap-2').style('background: #1a1a25; padding: 8px 16px; border: 1px solid #2a2a3a;'):
                            ui.label('Loaded:').style('color: #8888a0; font-size: 11px;')
                            self.proxy_count_label = ui.label('0 proxies').style('color: #00ff88; font-size: 12px; font-weight: 600;')

                # === 9PROXY API ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('🔥 9PROXY API').style('color: #ff6600; font-weight: 600; letter-spacing: 1px;')
                    ui.label('Dynamic residential proxy rotation via 9Proxy API').style('color: #8888a0; font-size: 12px;')

                    with ui.row().classes('w-full gap-4 items-center'):
                        self.nine_proxy_enabled = ui.checkbox(
                            'Enable 9Proxy',
                            value=self.config.get('nine_proxy', {}).get('enabled', False)
                        ).style('color: #e0e0e5;')

                        with ui.column().classes('flex-1 gap-1'):
                            ui.label('API URL').style('color: #8888a0; font-size: 11px;')
                            self.nine_proxy_url = ui.input(
                                value=self.config.get('nine_proxy', {}).get('api_url', 'http://localhost:50000'),
                                placeholder='http://localhost:50000'
                            ).classes('hitech-input w-full')

                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('flex-1 gap-1'):
                            ui.label('Ports (comma separated)').style('color: #8888a0; font-size: 11px;')
                            self.nine_proxy_ports = ui.input(
                                value=','.join(map(str, self.config.get('nine_proxy', {}).get('ports', [6001, 6002, 6003]))),
                                placeholder='6001,6002,6003'
                            ).classes('hitech-input w-full')

                        with ui.column().classes('w-40 gap-1'):
                            ui.label('Strategy').style('color: #8888a0; font-size: 11px;')
                            self.nine_proxy_strategy = ui.select(
                                options=['sequential', 'random'],
                                value=self.config.get('nine_proxy', {}).get('strategy', 'sequential')
                            ).classes('hitech-select w-full')

                        self.nine_proxy_auto_rotate = ui.checkbox(
                            'Auto Rotate',
                            value=self.config.get('nine_proxy', {}).get('auto_rotate', True)
                        ).style('color: #e0e0e5;')

                    # 9Proxy Filters
                    with ui.expansion('🎯 Geo Filters', icon='filter_alt').classes('w-full').style('background: rgba(255,102,0,0.1); border: 1px solid rgba(255,102,0,0.2);'):
                        with ui.row().classes('w-full gap-4'):
                            with ui.column().classes('flex-1 gap-1'):
                                ui.label('Country').style('color: #8888a0; font-size: 11px;')
                                self.nine_proxy_country = ui.input(
                                    value=self.config.get('nine_proxy', {}).get('filters', {}).get('country', ''),
                                    placeholder='US, DE, FR...'
                                ).classes('hitech-input w-full')
                            with ui.column().classes('flex-1 gap-1'):
                                ui.label('State').style('color: #8888a0; font-size: 11px;')
                                self.nine_proxy_state = ui.input(
                                    value=self.config.get('nine_proxy', {}).get('filters', {}).get('state', ''),
                                    placeholder='California, Texas...'
                                ).classes('hitech-input w-full')
                            with ui.column().classes('flex-1 gap-1'):
                                ui.label('City').style('color: #8888a0; font-size: 11px;')
                                self.nine_proxy_city = ui.input(
                                    value=self.config.get('nine_proxy', {}).get('filters', {}).get('city', ''),
                                    placeholder='New York, Los Angeles...'
                                ).classes('hitech-input w-full')
                            with ui.column().classes('flex-1 gap-1'):
                                ui.label('ISP').style('color: #8888a0; font-size: 11px;')
                                self.nine_proxy_isp = ui.input(
                                    value=self.config.get('nine_proxy', {}).get('filters', {}).get('isp', ''),
                                    placeholder='Comcast, Verizon...'
                                ).classes('hitech-input w-full')

                # Save button
                with ui.row().classes('w-full justify-end'):
                    ui.button('💾 SAVE PROXY SETTINGS', on_click=self.save_proxy_settings).classes('hitech-btn-primary').style('padding: 12px 32px; font-weight: 600;')

    def _get_current_proxy_mode(self):
        """Determine current proxy mode from config"""
        # First check if there's a saved proxy_mode
        saved_mode = self.config.get('proxy_mode')
        if saved_mode and saved_mode in ['Disabled', 'Single Proxy', 'Proxy List', '9Proxy API']:
            return saved_mode

        # Otherwise determine from enabled flags
        if self.config.get('nine_proxy', {}).get('enabled', False):
            return '9Proxy API'
        elif self.config.get('proxy_list', {}).get('enabled', False):
            return 'Proxy List'
        elif self.config.get('proxy_list', {}).get('proxies', []):
            return 'Proxy List'  # Has proxies in list
        elif self.config.get('proxy', {}).get('enabled', False):
            return 'Single Proxy'
        return 'Disabled'

    def save_proxy_settings(self):
        """Save proxy settings"""
        try:
            # Get selected proxy mode
            proxy_mode = self.proxy_mode_select.value
            self.config['proxy_mode'] = proxy_mode

            # Set enabled flags based on mode
            single_enabled = (proxy_mode == 'Single Proxy')
            list_enabled = (proxy_mode == 'Proxy List')
            nine_enabled = (proxy_mode == '9Proxy API')

            # Single Proxy
            self.config.setdefault('proxy', {})
            self.config['proxy']['enabled'] = single_enabled
            self.config['proxy']['type'] = self.proxy_type_select.value
            self.config['proxy']['host'] = self.proxy_host_input.value
            self.config['proxy']['port'] = self.proxy_port_input.value
            self.config['proxy']['login'] = self.proxy_login_input.value
            self.config['proxy']['password'] = self.proxy_password_input.value

            # Proxy List
            self.config.setdefault('proxy_list', {})
            proxy_lines = [line.strip() for line in self.proxy_list_input.value.split('\n') if line.strip()]
            self.config['proxy_list']['enabled'] = list_enabled
            self.config['proxy_list']['proxies'] = proxy_lines
            self.config['proxy_list']['default_type'] = self.proxy_default_type.value
            self.config['proxy_list']['rotation_mode'] = self.proxy_rotation_select.value
            self.config['proxy_list']['retry_on_failure'] = self.proxy_retry_checkbox.value

            # 9Proxy
            self.config.setdefault('nine_proxy', {})
            self.config['nine_proxy']['enabled'] = nine_enabled
            self.config['nine_proxy']['api_url'] = self.nine_proxy_url.value
            ports_str = self.nine_proxy_ports.value
            self.config['nine_proxy']['ports'] = [int(p.strip()) for p in ports_str.split(',') if p.strip().isdigit()]
            self.config['nine_proxy']['strategy'] = self.nine_proxy_strategy.value
            self.config['nine_proxy']['auto_rotate'] = self.nine_proxy_auto_rotate.value

            self.config['nine_proxy'].setdefault('filters', {})
            self.config['nine_proxy']['filters']['country'] = self.nine_proxy_country.value
            self.config['nine_proxy']['filters']['state'] = self.nine_proxy_state.value
            self.config['nine_proxy']['filters']['city'] = self.nine_proxy_city.value
            self.config['nine_proxy']['filters']['isp'] = self.nine_proxy_isp.value

            # Save to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            # Update proxy count label
            if hasattr(self, 'proxy_count_label'):
                count = len(proxy_lines)
                self.proxy_count_label.set_text(f'{count} proxies')

            # Also update the checkbox to reflect the mode
            self.proxy_enabled_checkbox.set_value(single_enabled)
            self.nine_proxy_enabled.set_value(nine_enabled)

            ui.notify(f'Proxy settings saved (Mode: {proxy_mode})', type='positive')
        except Exception as e:
            ui.notify(f'Error saving: {e}', type='negative')

    def _build_captcha_tab(self):
        """Build the anti-captcha tab with CapSolver integration"""
        with ui.scroll_area().classes('w-full h-full'):
            with ui.column().classes('w-full gap-6').style('padding: 20px; max-width: 1000px;'):
                # === CAPSOLVER SETTINGS ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    with ui.row().classes('items-center gap-4'):
                        ui.label('🔓 CAPSOLVER ANTI-CAPTCHA').style('color: #ff6b00; font-weight: 600; letter-spacing: 1px;')
                        ui.link('📖 Docs', 'https://docs.capsolver.com/', new_tab=True).style('font-size: 12px;')
                        ui.link('🔑 Get API Key', 'https://dashboard.capsolver.com/', new_tab=True).style('font-size: 12px;')

                    # Enable checkbox
                    with ui.row().classes('items-center gap-4'):
                        self.captcha_enabled_checkbox = ui.checkbox(
                            'Enable Anti-Captcha',
                            value=self.config.get('captcha', {}).get('enabled', False)
                        ).style('color: #e0e0e5;')

                        # Balance display
                        self.captcha_balance_label = ui.label('Balance: $0.00').style('color: #00ff88; font-size: 14px;')

                    # API Key
                    with ui.row().classes('w-full gap-4 items-end'):
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('CapSolver API Key').style('color: #8888a0; font-size: 12px;')
                            self.captcha_api_key_input = ui.input(
                                value=self.config.get('captcha', {}).get('api_key', ''),
                                password=True,
                                placeholder='CAP-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
                            ).classes('hitech-input w-full')

                        ui.button('Check Balance', on_click=self._check_captcha_balance).classes('hitech-btn').style('height: 40px;')

                # === CAPTCHA TYPES ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('🎯 SUPPORTED CAPTCHA TYPES').style('color: #00d4ff; font-weight: 600; letter-spacing: 1px;')

                    with ui.row().classes('w-full gap-6 flex-wrap'):
                        # reCAPTCHA v2
                        with ui.column().classes('gap-2').style('min-width: 200px;'):
                            self.captcha_recaptcha_v2 = ui.checkbox(
                                'reCAPTCHA v2',
                                value=self.config.get('captcha', {}).get('recaptcha_v2', True)
                            ).style('color: #e0e0e5;')
                            ui.label('Google reCAPTCHA checkbox').style('color: #666; font-size: 11px; margin-left: 28px;')

                        # reCAPTCHA v3
                        with ui.column().classes('gap-2').style('min-width: 200px;'):
                            self.captcha_recaptcha_v3 = ui.checkbox(
                                'reCAPTCHA v3',
                                value=self.config.get('captcha', {}).get('recaptcha_v3', True)
                            ).style('color: #e0e0e5;')
                            ui.label('Invisible score-based').style('color: #666; font-size: 11px; margin-left: 28px;')

                        # hCaptcha
                        with ui.column().classes('gap-2').style('min-width: 200px;'):
                            self.captcha_hcaptcha = ui.checkbox(
                                'hCaptcha',
                                value=self.config.get('captcha', {}).get('hcaptcha', True)
                            ).style('color: #e0e0e5;')
                            ui.label('hCaptcha challenges').style('color: #666; font-size: 11px; margin-left: 28px;')

                        # Turnstile
                        with ui.column().classes('gap-2').style('min-width: 200px;'):
                            self.captcha_turnstile = ui.checkbox(
                                'Cloudflare Turnstile',
                                value=self.config.get('captcha', {}).get('turnstile', True)
                            ).style('color: #e0e0e5;')
                            ui.label('Cloudflare protection').style('color: #666; font-size: 11px; margin-left: 28px;')

                        # Image captcha
                        with ui.column().classes('gap-2').style('min-width: 200px;'):
                            self.captcha_image = ui.checkbox(
                                'Image to Text',
                                value=self.config.get('captcha', {}).get('image_to_text', True)
                            ).style('color: #e0e0e5;')
                            ui.label('Classic image captchas').style('color: #666; font-size: 11px; margin-left: 28px;')

                        # FunCaptcha
                        with ui.column().classes('gap-2').style('min-width: 200px;'):
                            self.captcha_funcaptcha = ui.checkbox(
                                'FunCaptcha',
                                value=self.config.get('captcha', {}).get('funcaptcha', True)
                            ).style('color: #e0e0e5;')
                            ui.label('Arkose Labs puzzles').style('color: #666; font-size: 11px; margin-left: 28px;')

                # === SOLVING OPTIONS ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('⚙️ SOLVING OPTIONS').style('color: #00d4ff; font-weight: 600; letter-spacing: 1px;')

                    with ui.row().classes('w-full gap-6'):
                        # Timeout
                        with ui.column().classes('gap-2'):
                            ui.label('Solve Timeout (sec)').style('color: #8888a0; font-size: 12px;')
                            self.captcha_timeout_input = ui.number(
                                value=self.config.get('captcha', {}).get('timeout', 120),
                                min=30, max=300, step=10
                            ).classes('hitech-input').style('width: 100px;')

                        # reCAPTCHA v3 min score
                        with ui.column().classes('gap-2'):
                            ui.label('reCAPTCHA v3 Min Score').style('color: #8888a0; font-size: 12px;')
                            self.captcha_min_score_input = ui.number(
                                value=self.config.get('captcha', {}).get('min_score', 0.7),
                                min=0.1, max=0.9, step=0.1
                            ).classes('hitech-input').style('width: 100px;')

                    # Auto-detect option
                    with ui.row().classes('gap-4 mt-2'):
                        self.captcha_auto_detect = ui.checkbox(
                            'Auto-detect captcha type on page',
                            value=self.config.get('captcha', {}).get('auto_detect', True)
                        ).style('color: #e0e0e5;')

                        self.captcha_use_proxy = ui.checkbox(
                            'Use proxy for solving (faster, but costs more)',
                            value=self.config.get('captcha', {}).get('use_proxy', False)
                        ).style('color: #e0e0e5;')

                    with ui.row().classes('gap-4 mt-2'):
                        self.captcha_click_checkbox = ui.checkbox(
                            'Click checkbox visually after solving (emulate user click)',
                            value=self.config.get('captcha', {}).get('click_checkbox', True)
                        ).style('color: #00ff88;')
                        self.captcha_click_checkbox.tooltip('После решения капчи кликнет по чекбоксу для визуального подтверждения')

                # === USAGE EXAMPLE ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('📝 HOW TO USE IN YOUR CODE').style('color: #00d4ff; font-weight: 600; letter-spacing: 1px;')

                    code_example = '''# Captcha will be solved automatically when detected
# Or you can solve manually:

# Auto-detect and solve any captcha on page
token = solve_captcha(page)

# Solve specific captcha type
token = solve_captcha(page, captcha_type='recaptcha_v2')
token = solve_captcha(page, captcha_type='hcaptcha')
token = solve_captcha(page, captcha_type='turnstile')

# Solve image captcha
text = solve_image_captcha(image_base64)

# Check if captcha exists on page
if has_captcha(page):
    solve_captcha(page)'''

                    ui.code(code_example, language='python').classes('w-full').style('font-size: 12px;')

                # Save button
                with ui.row().classes('w-full justify-end gap-4 mt-4'):
                    ui.button('💾 Save Captcha Settings', on_click=self._save_captcha_settings).classes('hitech-btn-primary').style('height: 40px; padding: 0 24px;')

    async def _check_captcha_balance(self):
        """Check CapSolver balance"""
        try:
            api_key = self.captcha_api_key_input.value
            if not api_key:
                ui.notify('Please enter API key first', type='warning')
                return

            import requests
            response = requests.post(
                'https://api.capsolver.com/getBalance',
                json={'clientKey': api_key},
                timeout=10
            )
            data = response.json()

            if data.get('errorId') == 0:
                balance = data.get('balance', 0)
                self.captcha_balance_label.set_text(f'Balance: ${balance:.2f}')
                ui.notify(f'Balance: ${balance:.2f}', type='positive')
            else:
                error = data.get('errorDescription', 'Unknown error')
                ui.notify(f'Error: {error}', type='negative')
        except Exception as e:
            ui.notify(f'Error checking balance: {e}', type='negative')

    def _save_captcha_settings(self):
        """Save captcha settings to config"""
        try:
            if 'captcha' not in self.config:
                self.config['captcha'] = {}

            self.config['captcha']['enabled'] = self.captcha_enabled_checkbox.value
            self.config['captcha']['api_key'] = self.captcha_api_key_input.value
            self.config['captcha']['recaptcha_v2'] = self.captcha_recaptcha_v2.value
            self.config['captcha']['recaptcha_v3'] = self.captcha_recaptcha_v3.value
            self.config['captcha']['hcaptcha'] = self.captcha_hcaptcha.value
            self.config['captcha']['turnstile'] = self.captcha_turnstile.value
            self.config['captcha']['image_to_text'] = self.captcha_image.value
            self.config['captcha']['funcaptcha'] = self.captcha_funcaptcha.value
            self.config['captcha']['timeout'] = int(self.captcha_timeout_input.value)
            self.config['captcha']['min_score'] = float(self.captcha_min_score_input.value)
            self.config['captcha']['auto_detect'] = self.captcha_auto_detect.value
            self.config['captcha']['use_proxy'] = self.captcha_use_proxy.value
            self.config['captcha']['click_checkbox'] = self.captcha_click_checkbox.value

            self.save_config()
            ui.notify('Captcha settings saved!', type='positive')
        except Exception as e:
            ui.notify(f'Error saving: {e}', type='negative')

    def _build_settings_tab(self):
        """Build the settings tab"""
        with ui.scroll_area().classes('w-full h-full'):
            with ui.column().classes('w-full gap-6').style('padding: 20px; max-width: 1000px;'):
                # === OCTOBROWSER API ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('⚙️ OCTOBROWSER API').style('color: #00d4ff; font-weight: 600; letter-spacing: 1px;')

                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('API Token').style('color: #8888a0; font-size: 12px;')
                            self.api_token_input = ui.input(
                                value=self.config.get('octobrowser', {}).get('api_token', ''),
                                password=True,
                                placeholder='Enter your API token'
                            ).classes('hitech-input w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('API Base URL').style('color: #8888a0; font-size: 12px;')
                            self.api_url_input = ui.input(
                                value=self.config.get('octobrowser', {}).get('api_base_url', 'https://app.octobrowser.net/api/v2/automation'),
                                placeholder='API Base URL'
                            ).classes('hitech-input w-full')

                    with ui.row().classes('gap-2'):
                        ui.button('💾 Save API', on_click=self.save_api_settings).classes('hitech-btn-primary')
                        ui.button('🔗 Test Connection', on_click=self.test_api_connection).classes('hitech-btn')

                # === SMS PROVIDER ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('📱 SMS PROVIDER').style('color: #ff66cc; font-weight: 600; letter-spacing: 1px;')

                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Provider').style('color: #8888a0; font-size: 12px;')
                            self.sms_provider_select = ui.select(
                                options=['daisysms', 'smshub', '5sim', 'sms-activate', 'grizzlysms'],
                                value=self.config.get('sms', {}).get('provider', 'daisysms')
                            ).classes('hitech-select w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('API Key').style('color: #8888a0; font-size: 12px;')
                            self.sms_api_key_input = ui.input(
                                value=self.config.get('sms', {}).get('api_key', ''),
                                password=True,
                                placeholder='SMS API Key'
                            ).classes('hitech-input w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Service Code').style('color: #8888a0; font-size: 12px;')
                            self.sms_service_input = ui.input(
                                value=self.config.get('sms', {}).get('service', 'ds'),
                                placeholder='Service code (ds, go, etc.)'
                            ).classes('hitech-input w-full')

                # === HUMANIZE SETTINGS ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('🤖 HUMANIZE / TIMING').style('color: #ffcc00; font-weight: 600; letter-spacing: 1px;')

                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Typing Delay Min (ms)').style('color: #8888a0; font-size: 12px;')
                            self.typing_min_input = ui.number(
                                value=self.config.get('humanize', {}).get('typing_delay_min', 50),
                                min=10, max=500
                            ).classes('hitech-input w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Typing Delay Max (ms)').style('color: #8888a0; font-size: 12px;')
                            self.typing_max_input = ui.number(
                                value=self.config.get('humanize', {}).get('typing_delay_max', 150),
                                min=50, max=1000
                            ).classes('hitech-input w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Click Delay (ms)').style('color: #8888a0; font-size: 12px;')
                            self.click_delay_input = ui.number(
                                value=self.config.get('humanize', {}).get('click_delay', 500),
                                min=100, max=3000
                            ).classes('hitech-input w-full')

                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Page Load Timeout (s)').style('color: #8888a0; font-size: 12px;')
                            self.page_timeout_input = ui.number(
                                value=self.config.get('humanize', {}).get('page_timeout', 30),
                                min=5, max=120
                            ).classes('hitech-input w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Action Timeout (s)').style('color: #8888a0; font-size: 12px;')
                            self.action_timeout_input = ui.number(
                                value=self.config.get('humanize', {}).get('action_timeout', 10),
                                min=1, max=60
                            ).classes('hitech-input w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Random Delay Range (ms)').style('color: #8888a0; font-size: 12px;')
                            self.random_delay_input = ui.number(
                                value=self.config.get('humanize', {}).get('random_delay', 1000),
                                min=0, max=5000
                            ).classes('hitech-input w-full')

                    with ui.row().classes('w-full gap-4'):
                        self.humanize_mouse_checkbox = ui.checkbox(
                            'Humanize Mouse Movement',
                            value=self.config.get('humanize', {}).get('mouse_movement', True)
                        ).style('color: #e0e0e5;')
                        self.humanize_scroll_checkbox = ui.checkbox(
                            'Random Scrolling',
                            value=self.config.get('humanize', {}).get('random_scroll', False)
                        ).style('color: #e0e0e5;')

                # === PROFILE SETTINGS ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('👤 PROFILE DEFAULTS').style('color: #00d4ff; font-weight: 600; letter-spacing: 1px;')

                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Default Tags (comma-separated)').style('color: #8888a0; font-size: 12px;')
                            self.default_tags_input = ui.input(
                                value=', '.join(self.config.get('octo_defaults', {}).get('tags', [])),
                                placeholder='tag1, tag2, tag3'
                            ).classes('hitech-input w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Profile Notes').style('color: #8888a0; font-size: 12px;')
                            self.default_notes_input = ui.input(
                                value=self.config.get('octo_defaults', {}).get('notes', ''),
                                placeholder='Auto-generated profile'
                            ).classes('hitech-input w-full')

                # === FINGERPRINT SETTINGS ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('🎭 FINGERPRINT').style('color: #ff9900; font-weight: 600; letter-spacing: 1px;')

                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Operating System').style('color: #8888a0; font-size: 12px;')
                            self.fp_os_select = ui.select(
                                options=['win', 'mac', 'linux'],
                                value=self.config.get('fingerprint', {}).get('os', 'win')
                            ).classes('hitech-select w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('WebRTC Mode').style('color: #8888a0; font-size: 12px;')
                            self.fp_webrtc_select = ui.select(
                                options=['altered', 'disabled', 'real'],
                                value=self.config.get('fingerprint', {}).get('webrtc', 'altered')
                            ).classes('hitech-select w-full')

                    with ui.row().classes('w-full gap-4'):
                        self.fp_canvas_checkbox = ui.checkbox(
                            'Canvas Protection',
                            value=self.config.get('fingerprint', {}).get('canvas_protection', True)
                        ).style('color: #e0e0e5;')
                        self.fp_webgl_checkbox = ui.checkbox(
                            'WebGL Protection',
                            value=self.config.get('fingerprint', {}).get('webgl_protection', True)
                        ).style('color: #e0e0e5;')
                        self.fp_fonts_checkbox = ui.checkbox(
                            'Fonts Protection',
                            value=self.config.get('fingerprint', {}).get('fonts_protection', True)
                        ).style('color: #e0e0e5;')

                # === GEOLOCATION ===
                with ui.column().classes('hitech-card w-full gap-4').style('padding: 20px;'):
                    ui.label('📍 GEOLOCATION').style('color: #66ccff; font-weight: 600; letter-spacing: 1px;')

                    with ui.row().classes('w-full gap-4 items-center'):
                        self.geo_enabled_checkbox = ui.checkbox(
                            'Enable Custom Geolocation',
                            value=self.config.get('geolocation', {}).get('enabled', False)
                        ).style('color: #e0e0e5;')

                    with ui.row().classes('w-full gap-4'):
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Latitude').style('color: #8888a0; font-size: 12px;')
                            self.geo_lat_input = ui.input(
                                value=self.config.get('geolocation', {}).get('latitude', ''),
                                placeholder='40.7128'
                            ).classes('hitech-input w-full')
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label('Longitude').style('color: #8888a0; font-size: 12px;')
                            self.geo_lon_input = ui.input(
                                value=self.config.get('geolocation', {}).get('longitude', ''),
                                placeholder='-74.0060'
                            ).classes('hitech-input w-full')

                # === SAVE ALL BUTTON ===
                with ui.row().classes('w-full justify-center gap-4'):
                    ui.button('💾 SAVE ALL SETTINGS', on_click=self.save_all_settings).classes('hitech-btn-primary').style('height: 50px; padding: 0 40px; font-size: 14px;')

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

    def _update_iterations_display(self):
        """Update the iterations display in sidebar"""
        if not self.iterations_container:
            return

        self.iterations_container.clear()

        with self.iterations_container:
            if not self.iterations_data:
                # Empty state
                with ui.column().classes('w-full items-center').style('padding: 40px 20px;'):
                    ui.label('🚀').style('font-size: 48px; opacity: 0.5;')
                    ui.label('No iterations').style('color: #8888a0; font-weight: 600;')
                    ui.label('Run script to see iterations').style('color: #666; font-size: 11px; text-align: center;')
            else:
                for iter_id, data in self.iterations_data.items():
                    self._create_iteration_card(iter_id, data)

        # Update stats
        total = len(self.iterations_data)
        active = sum(1 for t in self.iterations_data.values() if t.get('status') == 'running')

        if 'iterations' in self.stats_labels:
            self.stats_labels['iterations'].set_text(f'ITERATIONS: {total}')
        if 'active' in self.stats_labels:
            self.stats_labels['active'].set_text(f'ACTIVE: {active}')
        if 'indicator' in self.stats_labels:
            color = '#00ff88' if active > 0 else '#666'
            self.stats_labels['indicator'].style(f'color: {color};')

    def _create_iteration_card(self, iter_id: str, data: dict):
        """Create an iteration card in the sidebar - click to show full logs"""
        status = data.get('status', 'pending')
        progress = data.get('progress', 0)
        logs = data.get('logs', [])
        csv_row = data.get('csv_row', iter_id)

        status_colors = {
            'pending': '#8888a0',
            'running': '#00ff88',
            'completed': '#00d4ff',
            'error': '#ff4466'
        }
        color = status_colors.get(status, '#8888a0')

        # Card that opens full log dialog on click
        with ui.card().classes('iteration-card w-full cursor-pointer').style(f'''
            background: rgba(20, 20, 35, 0.6);
            border: 1px solid {color}40;
            border-left: 3px solid {color};
            margin-bottom: 8px;
            padding: 12px;
            transition: all 0.2s;
        ''').on('click', lambda e, lid=iter_id, ldata=data: self._show_iteration_logs(lid, ldata)):
            with ui.row().classes('w-full items-center justify-between'):
                with ui.column().classes('gap-0'):
                    ui.label(f'Iteration #{iter_id}').style('color: #e0e0e5; font-size: 13px; font-weight: 600;')
                    ui.label(f'CSV Row: {csv_row}').style('color: #8888a0; font-size: 10px;')

                with ui.column().classes('items-end gap-0'):
                    ui.label(status.upper()).style(f'color: {color}; font-size: 11px; font-weight: 600;')
                    if logs:
                        ui.label(f'{len(logs)} logs').style('color: #666; font-size: 10px;')

            # Progress bar for running iterations
            if status == 'running':
                ui.linear_progress(value=progress).classes('hitech-progress w-full').style('margin-top: 8px;')

    def _show_iteration_logs(self, iter_id: str, data: dict):
        """Show full logs for an iteration in a dialog"""
        logs = data.get('logs', [])
        status = data.get('status', 'pending')
        csv_row = data.get('csv_row', iter_id)

        status_colors = {
            'pending': '#8888a0',
            'running': '#00ff88',
            'completed': '#00d4ff',
            'error': '#ff4466'
        }
        color = status_colors.get(status, '#8888a0')

        with ui.dialog() as dialog, ui.card().classes('w-full').style('''
            background: #0a0a0f;
            border: 1px solid rgba(0, 212, 255, 0.3);
            max-width: 900px;
            max-height: 80vh;
        '''):
            # Header
            with ui.row().classes('w-full items-center justify-between').style('''
                padding: 16px 20px;
                border-bottom: 1px solid #2a2a3a;
                background: #12121a;
            '''):
                with ui.row().classes('items-center gap-3'):
                    ui.label(f'📋 Iteration #{iter_id}').style('color: #e0e0e5; font-size: 16px; font-weight: 600;')
                    ui.label(f'CSV Row: {csv_row}').style('color: #8888a0; font-size: 12px;')
                    ui.label(status.upper()).style(f'''
                        color: {color};
                        font-size: 11px;
                        font-weight: 600;
                        padding: 4px 12px;
                        background: {color}20;
                        border: 1px solid {color}40;
                    ''')

                ui.button('✕', on_click=dialog.close).classes('hitech-btn').style('padding: 8px 12px;')

            # Logs content
            with ui.scroll_area().classes('w-full').style('height: 500px; padding: 16px;'):
                if logs:
                    for log_line in logs:
                        log_color = '#e0e0e5'
                        if '[ERROR]' in log_line:
                            log_color = '#ff4466'
                        elif '[OK]' in log_line:
                            log_color = '#00ff88'
                        elif '[WARN]' in log_line:
                            log_color = '#ffaa00'
                        elif '[THREAD' in log_line or '###' in log_line:
                            log_color = '#00d4ff'

                        ui.label(log_line).style(f'''
                            color: {log_color};
                            font-size: 12px;
                            font-family: monospace;
                            white-space: pre-wrap;
                            word-break: break-all;
                            line-height: 1.6;
                            padding: 2px 0;
                        ''')
                else:
                    ui.label('No logs available').style('color: #666; font-style: italic;')

        dialog.open()

    # ========== Action Methods ==========

    def save_all_settings(self):
        """Save all settings to config"""
        try:
            # Octobrowser API
            self.config.setdefault('octobrowser', {})
            self.config['octobrowser']['api_token'] = self.api_token_input.value
            self.config['octobrowser']['api_base_url'] = self.api_url_input.value

            # SMS Provider
            self.config.setdefault('sms', {})
            self.config['sms']['provider'] = self.sms_provider_select.value
            self.config['sms']['api_key'] = self.sms_api_key_input.value
            self.config['sms']['service'] = self.sms_service_input.value

            # Note: Proxy settings are saved via save_proxy_settings() in PROXY tab

            # Humanize Settings
            self.config.setdefault('humanize', {})
            self.config['humanize']['typing_delay_min'] = int(self.typing_min_input.value or 50)
            self.config['humanize']['typing_delay_max'] = int(self.typing_max_input.value or 150)
            self.config['humanize']['click_delay'] = int(self.click_delay_input.value or 500)
            self.config['humanize']['page_timeout'] = int(self.page_timeout_input.value or 30)
            self.config['humanize']['action_timeout'] = int(self.action_timeout_input.value or 10)
            self.config['humanize']['random_delay'] = int(self.random_delay_input.value or 1000)
            self.config['humanize']['mouse_movement'] = self.humanize_mouse_checkbox.value
            self.config['humanize']['random_scroll'] = self.humanize_scroll_checkbox.value

            # Profile Defaults
            self.config.setdefault('octo_defaults', {})
            tags = [t.strip() for t in self.default_tags_input.value.split(',') if t.strip()]
            self.config['octo_defaults']['tags'] = tags
            self.config['octo_defaults']['notes'] = self.default_notes_input.value

            # Fingerprint
            self.config.setdefault('fingerprint', {})
            self.config['fingerprint']['os'] = self.fp_os_select.value
            self.config['fingerprint']['webrtc'] = self.fp_webrtc_select.value
            self.config['fingerprint']['canvas_protection'] = self.fp_canvas_checkbox.value
            self.config['fingerprint']['webgl_protection'] = self.fp_webgl_checkbox.value
            self.config['fingerprint']['fonts_protection'] = self.fp_fonts_checkbox.value

            # Geolocation
            self.config.setdefault('geolocation', {})
            self.config['geolocation']['enabled'] = self.geo_enabled_checkbox.value
            self.config['geolocation']['latitude'] = self.geo_lat_input.value
            self.config['geolocation']['longitude'] = self.geo_lon_input.value

            # Save to file
            self.save_config()
            ui.notify('All settings saved successfully!', type='positive')
        except Exception as e:
            ui.notify(f'Error saving settings: {e}', type='negative')

    def run_script(self, test: bool = False):
        """Run the automation script"""
        import importlib
        import tempfile
        import threading

        threads_count = 1 if test else int(self.threads_input.value or 1)
        provider_name = self.provider_select.value
        browser_mode_ui = self.browser_mode_select.value
        headless = self.headless_checkbox.value
        user_code = self.code_editor.value

        # Map UI values to generator values
        browser_mode = 'local_chromium' if browser_mode_ui == 'Local Chromium' else 'octobrowser_api'

        if not user_code.strip():
            ui.notify('Please enter automation code first', type='warning')
            return

        self.add_log(f'[System] Browser mode: {browser_mode_ui} ({browser_mode})')
        self.add_log(f'[System] Provider: {provider_name}')
        self.add_log(f'[System] Threads: {threads_count}')
        self.add_log(f'[System] Headless: {headless}')

        try:
            # Import provider's generator and runner
            generator_module = importlib.import_module(f'src.providers.{provider_name}.generator')
            runner_module = importlib.import_module(f'src.providers.{provider_name}.runner')

            generator = generator_module.Generator()
            self.current_runner = runner_module.Runner()

            # Build config for generator
            nine_proxy_config = self.config.get('nine_proxy', {})
            # Antidetect mode (only for Local Chromium)
            antidetect_enabled = self.antidetect_checkbox.value if browser_mode == 'local_chromium' else False

            gen_config = {
                'api_token': self.config.get('octobrowser', {}).get('api_token', ''),
                'threads_count': threads_count,
                'headless': headless,
                'browser_mode': browser_mode,
                'antidetect_enabled': antidetect_enabled,
                'antidetect_country': 'auto',  # auto = определять по гео прокси
                'proxy': self.config.get('proxy', {}),
                'proxy_list': self.config.get('proxy_list', {}),
                # 9Proxy settings
                'nine_proxy_enabled': nine_proxy_config.get('enabled', False),
                'nine_proxy_api_url': nine_proxy_config.get('api_url', 'http://localhost:50000'),
                'nine_proxy_ports': nine_proxy_config.get('ports', []),
                'nine_proxy_strategy': nine_proxy_config.get('strategy', 'sequential'),
                'nine_proxy_auto_rotate': nine_proxy_config.get('auto_rotate', True),
                'nine_proxy': nine_proxy_config,  # Full config for filters
                'profile': {
                    'tags': self.config.get('octo_defaults', {}).get('tags', []),
                    'notes': self.config.get('octo_defaults', {}).get('notes', ''),
                },
                'fingerprint': self.config.get('fingerprint', {}),
                'humanize': self.config.get('humanize', {}),
                'simulate_typing': self.config.get('humanize', {}).get('mouse_movement', True),
                'typing_delay': self.config.get('humanize', {}).get('typing_delay_min', 50),
                'action_delay': self.config.get('humanize', {}).get('click_delay', 500) / 1000,
                # Captcha settings
                'captcha': self.config.get('captcha', {}),
            }

            # Log proxy mode
            proxy_mode = self.config.get('proxy_mode', 'Disabled')
            self.add_log(f'[System] Proxy mode: {proxy_mode}')
            if proxy_mode == '9Proxy API':
                self.add_log(f'[System] 9Proxy ports: {nine_proxy_config.get("ports", [])}')

            # Generate script
            self.add_log('[System] Generating script...')
            generated_script = generator.generate_script(user_code, gen_config)

            # Save to temp file
            script_dir = Path(__file__).parent.parent.parent / 'generated_scripts'
            script_dir.mkdir(exist_ok=True)
            script_path = script_dir / f'script_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'

            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(generated_script)

            self.add_log(f'[System] Script saved: {script_path.name}')

            # Update generated script tab
            if hasattr(self, 'generated_script_area'):
                self.generated_script_area.set_value(generated_script)

            # Initialize iterations tracking (will be populated as iterations start)
            self.iterations_data.clear()
            self._update_iterations_display()
            self._current_iteration_id = None

            # Set output callback - parse logs by iteration
            def on_output(line):
                import re
                self.add_log(line)

                # Parse ITERATION from log: ITERATION X or [ITERATION X]
                iter_match = re.search(r'ITERATION\s+(\d+)', line)
                if iter_match:
                    iter_id = iter_match.group(1)

                    # Create iteration entry if not exists
                    if iter_id not in self.iterations_data:
                        # Parse CSV row from header: CSV ROW X
                        csv_match = re.search(r'CSV ROW\s+(\d+)', line)
                        csv_row = csv_match.group(1) if csv_match else iter_id
                        self.iterations_data[iter_id] = {
                            'status': 'running',
                            'progress': 0.1,
                            'logs': [],
                            'csv_row': csv_row
                        }

                    self.iterations_data[iter_id]['logs'].append(line)
                    self._current_iteration_id = iter_id

                    # Update status based on keywords
                    if '[OK]' in line:
                        self.iterations_data[iter_id]['progress'] = min(
                            self.iterations_data[iter_id]['progress'] + 0.2, 0.95
                        )
                    elif '[ERROR]' in line or '[FAIL]' in line:
                        self.iterations_data[iter_id]['status'] = 'error'

                    self._update_iterations_display()

                # Also add THREAD logs to current iteration
                elif self._current_iteration_id and self._current_iteration_id in self.iterations_data:
                    if '[THREAD' in line or '[PROXY' in line or '[MARK' in line:
                        self.iterations_data[self._current_iteration_id]['logs'].append(line)

                # Check for iteration completion
                if '[ITERATION' in line and ('[OK]' in line or 'успешно' in line.lower()):
                    iter_match = re.search(r'\[ITERATION\s+(\d+)\]', line)
                    if iter_match:
                        iter_id = iter_match.group(1)
                        if iter_id in self.iterations_data:
                            self.iterations_data[iter_id]['status'] = 'completed'
                            self.iterations_data[iter_id]['progress'] = 1.0
                            self._update_iterations_display()

                elif '[MAIN] ЗАВЕРШЕНО' in line:
                    # All done - mark remaining as completed
                    for iid in self.iterations_data:
                        if self.iterations_data[iid]['status'] == 'running':
                            self.iterations_data[iid]['status'] = 'completed'
                            self.iterations_data[iid]['progress'] = 1.0
                    self._update_iterations_display()

            self.current_runner.set_output_callback(on_output)

            # Run script
            self.add_log('[System] Starting script execution...')
            self.current_runner.run(str(script_path))

            ui.notify(f'Script started ({threads_count} thread(s))', type='positive')

        except Exception as e:
            self.add_log(f'[ERROR] {e}', 'error')
            ui.notify(f'Error: {e}', type='negative')
            import traceback
            traceback.print_exc()

    def stop_all(self):
        """Stop all running iterations"""
        if hasattr(self, 'current_runner') and self.current_runner:
            self.current_runner.stop()

        for iter_id in self.iterations_data:
            if self.iterations_data[iter_id]['status'] == 'running':
                self.iterations_data[iter_id]['status'] = 'error'
        self._update_iterations_display()
        self.add_log('[System] Execution stopped', 'warning')
        ui.notify('Execution stopped', type='warning')

    def clear_iterations(self):
        """Clear all iterations"""
        self.iterations_data.clear()
        self._update_iterations_display()
        ui.notify('Iterations cleared', type='info')

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


def find_free_port():
    """Find a free port on localhost"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def main():
    """Main entry point"""
    port = find_free_port()
    print(f"Starting on port {port}...")

    app_instance = BrowserAutomatorApp()
    app_instance.build_ui()
    ui.run(
        title='Browser Automator Pro v5.0',
        port=port,
        reload=False,
        show=True,
        dark=True
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
