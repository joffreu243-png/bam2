"""
🚀 auto2tesst v3 - EPIC EDITION
Самый продвинутый Playwright-автотестер 2025 года

НОВЫЕ ФИЧИ:
- CTkTabview архитектура
- Умный парсер данных с Faker
- CSV генератор
- Proxy менеджер
- Полные настройки Octo API
- Цветные логи
- Статусбар с прогрессом
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import json
import os
import threading
import importlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Literal

# Импорты из проекта
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.octobrowser_api import OctobrowserAPI
from src.utils.script_parser import ScriptParser
from src.utils.selenium_ide_parser import SeleniumIDEParser
from src.utils.playwright_parser import PlaywrightParser
from src.utils.data_parser import SmartDataParser
from src.sms.provider_manager import ProviderManager
from src.data.dynamic_field import DynamicFieldManager

# Modern UI Components
from .themes import ModernTheme, ButtonStyles
from .components import ToastManager, DataTab, ProxyTab, OctoAPITab


def discover_providers():
    """Автоопределение провайдеров из папки src/providers/"""
    providers_dir = Path(__file__).parent.parent / 'providers'
    if not providers_dir.exists():
        return ['default_no_otp']

    providers = []
    for item in providers_dir.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            if (item / 'generator.py').exists() and (item / 'runner.py').exists():
                providers.append(item.name)

    return sorted(providers) if providers else ['default_no_otp']


class ModernAppV3(ctk.CTk):
    """
    🎨 auto2tesst v3 - EPIC EDITION

    Коммерческий уровень за $499!
    """

    def __init__(self):
        super().__init__()

        # === НАСТРОЙКИ ОКНА ===
        self.title("auto2tesst v3.0 EPIC - Modern Playwright Automation")
        self.geometry("1600x1000")
        self.minsize(1400, 800)

        # === ТЕМА ===
        ctk.set_appearance_mode("dark")
        self.current_theme = 'dark'
        self.theme = ModernTheme.DARK

        # === ДАННЫЕ ===
        self.config = {}
        self.load_config()

        # === КОМПОНЕНТЫ ===
        self.api: Optional[OctobrowserAPI] = None
        self.available_providers = discover_providers()
        self.current_provider = 'smart_wf' if 'smart_wf' in self.available_providers else self.available_providers[0]
        self.parser = ScriptParser()
        self.side_parser = SeleniumIDEParser()
        otp_enabled = self.config.get('otp', {}).get('enabled', False)
        self.playwright_parser = PlaywrightParser(otp_enabled=otp_enabled)
        if not otp_enabled:
            print("[OTP] OTP handler disabled by config")
        self.data_parser = SmartDataParser()
        self.sms_provider_manager = ProviderManager()
        self.dynamic_field_manager = DynamicFieldManager()

        # Данные импорта
        self.imported_data = None
        self.csv_data_rows = []
        self.csv_file_path = None  # 🔥 Путь к загруженному CSV
        self.csv_embed_mode = True  # 🔥 Режим встраивания CSV в скрипт (True = встроить данные, False = использовать путь)

        # === TOAST MANAGER (создаём ДО create_ui!) ===
        self.toast = ToastManager(self)
        self.toast.place_container(relx=0.98, rely=0.98, anchor="se")

        # === СОЗДАНИЕ UI ===
        self.create_ui()

        # 🔥 КРИТИЧНО: Поднять toast контейнер ПОСЛЕ создания всех виджетов!
        # Иначе CTkTabview и другие виджеты закрывают toast
        self.toast.container.lift()
        print("[MAIN WINDOW] Toast контейнер поднят после create_ui()")

        # === ЗАГРУЗКА НАСТРОЕК ТАЙМАУТОВ ===
        self.load_timeout_settings()

        # === ГОРЯЧИЕ КЛАВИШИ ===
        self.setup_hotkeys()

        # 🔥 АВТОСОХРАНЕНИЕ ПРИ ЗАКРЫТИИ ОКНА
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Показать приветствие (увеличен delay для полной отрисовки окна)
        self.after(1000, lambda: self.toast.success("🚀 auto2tesst v3 EPIC загружен!", duration=3000))

    # ========================================================================
    # КОНФИГУРАЦИЯ
    # ========================================================================

    def load_config(self):
        """Загрузка конфигурации из config.json"""
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        print(f"[MAIN] Загрузка config из: {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            token = self.config.get('octobrowser', {}).get('api_token', '')
            print(f"[MAIN] ✅ Config загружен. Токен: {token[:10]}..." if token else "[MAIN] ✅ Config загружен. Токен пуст")
        except FileNotFoundError:
            # 🔥 СОЗДАТЬ ДЕФОЛТНЫЙ CONFIG И СОХРАНИТЬ В ФАЙЛ
            self.config = {
                'octobrowser': {'api_base_url': 'https://app.octobrowser.net/api/v2/automation', 'api_token': ''},
                'sms': {'provider': 'daisysms', 'api_key': '', 'service': 'ds'},
                'proxy': {'enabled': False, 'type': 'http', 'host': '', 'port': '', 'login': '', 'password': ''},
                'proxy_list': {'proxies': [], 'rotation_mode': 'sequential', 'retry_on_failure': True, 'timeout': 10},
                'octo_defaults': {'tags': [], 'plugins': [], 'notes': ''},
                'fingerprint': {'os': 'win', 'webrtc': 'altered', 'canvas_protection': True, 'webgl_protection': True, 'fonts_protection': True},
                'geolocation': {'enabled': False, 'latitude': '', 'longitude': ''},
                'ui_settings': {'last_csv_path': '', 'automation_framework': 'playwright', 'playwright_target': 'library'},
                'script_settings': {'output_directory': 'generated_scripts', 'default_automation_framework': 'playwright'}
            }
            # СОХРАНИТЬ ДЕФОЛТНЫЙ CONFIG В ФАЙЛ
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                print(f"[CONFIG] Создан новый config.json с дефолтными настройками")
            except Exception as e:
                print(f"[CONFIG ERROR] Не удалось создать config.json: {e}")

    def save_config(self):
        """
        🔥 ЦЕНТРАЛИЗОВАННОЕ СОХРАНЕНИЕ КОНФИГУРАЦИИ

        Все компоненты обновляют self.config в памяти,
        а это единственное место где config.json физически сохраняется.
        """
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        try:
            print(f"[MAIN] === ЦЕНТРАЛИЗОВАННОЕ СОХРАНЕНИЕ CONFIG ===")
            print(f"[MAIN] Путь: {config_path}")

            token = self.config.get('octobrowser', {}).get('api_token', '')
            print(f"[MAIN] Сохраняю токен: {token[:10]}..." if token else "[MAIN] Токен пуст")

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            print(f"[MAIN] ✅ Config.json сохранён успешно!")

            # Проверка
            with open(config_path, 'r', encoding='utf-8') as f:
                check = json.load(f)
            check_token = check.get('octobrowser', {}).get('api_token', '')
            print(f"[MAIN] Проверка: токен в файле = {check_token[:10]}..." if check_token else "[MAIN] Проверка: токен в файле пуст")

            self.toast.success("✅ Настройки сохранены")
        except Exception as e:
            print(f"[MAIN] ❌ ОШИБКА сохранения: {e}")
            import traceback
            traceback.print_exc()
            self.toast.error(f"Ошибка сохранения: {e}")

    def on_closing(self):
        """Обработчик закрытия окна - автосохранение"""
        print("[MAIN] === ЗАКРЫТИЕ ОКНА - АВТОСОХРАНЕНИЕ ===")
        self.save_config()
        print("[MAIN] Уничтожаю окно...")
        self.destroy()

    # ========================================================================
    # СОЗДАНИЕ UI
    # ========================================================================

    def create_ui(self):
        """Создание интерфейса"""
        # 🔥 Конфигурация grid - новый layout с боковой панелью
        self.grid_rowconfigure(0, weight=0)     # Topbar
        self.grid_rowconfigure(1, weight=1)     # Main content with sidebar + tabs
        self.grid_rowconfigure(2, weight=0)     # Statusbar
        self.grid_columnconfigure(0, weight=0)  # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=1)  # Main content (expandable)

        # === ДАННЫЕ ПОТОКОВ ===
        self.threads_data = {}  # {thread_id: {'status': str, 'logs': [], 'progress': float}}
        self.active_threads_count = 0
        self.total_threads_count = 0
        self.variables_count = 0

        # === ВЕРХНЯЯ ПАНЕЛЬ ===
        self.create_top_bar()

        # === ЛЕВАЯ БОКОВАЯ ПАНЕЛЬ (ПОТОКИ) ===
        self.create_sidebar()

        # === ГЛАВНАЯ ОБЛАСТЬ С ТАБАМИ ===
        self.create_main_content()

        # === НИЖНИЙ СТАТУСБАР ===
        self.create_statusbar()

    def create_top_bar(self):
        """Верхняя панель с счётчиками статуса"""
        topbar = ctk.CTkFrame(
            self,
            height=70,
            corner_radius=0,
            fg_color=self.theme['bg_sidebar'],
            border_width=0
        )
        topbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        topbar.grid_columnconfigure(1, weight=1)
        topbar.grid_propagate(False)

        # Логотип
        title_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=24, pady=15, sticky="w")

        logo = ctk.CTkLabel(
            title_frame,
            text="🚀",
            font=(ModernTheme.FONT['family'], 32)
        )
        logo.pack(side="left", padx=(0, 12))

        title_col = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_col.pack(side="left")

        title = ctk.CTkLabel(
            title_col,
            text="Browser Automator Pro",
            font=(ModernTheme.FONT['family'], 22, 'bold'),
            text_color=self.theme['text_primary']
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_col,
            text="Ultimate Playwright Automation Builder",
            font=(ModernTheme.FONT['family'], 11),
            text_color=self.theme['text_secondary']
        )
        subtitle.pack(anchor="w")

        # === СЧЁТЧИКИ СТАТУСА (справа) ===
        stats_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        stats_frame.grid(row=0, column=1, padx=20, sticky="e")

        # Индикатор + Потоков
        self.threads_indicator = ctk.CTkLabel(
            stats_frame,
            text="●",
            font=(ModernTheme.FONT['family'], 12),
            text_color="#666666"
        )
        self.threads_indicator.pack(side="left", padx=(0, 5))

        self.threads_count_label = ctk.CTkLabel(
            stats_frame,
            text="Потоков: 0",
            font=(ModernTheme.FONT['family'], 12),
            text_color=self.theme['text_secondary'],
            fg_color=self.theme['bg_tertiary'],
            corner_radius=8,
            padx=12,
            pady=4
        )
        self.threads_count_label.pack(side="left", padx=(0, 12))

        # Активных
        self.active_count_label = ctk.CTkLabel(
            stats_frame,
            text="Активных: 0",
            font=(ModernTheme.FONT['family'], 12),
            text_color=self.theme['text_secondary'],
            fg_color=self.theme['bg_tertiary'],
            corner_radius=8,
            padx=12,
            pady=4
        )
        self.active_count_label.pack(side="left", padx=(0, 12))

        # Переменных
        self.variables_count_label = ctk.CTkLabel(
            stats_frame,
            text="Переменных: 0",
            font=(ModernTheme.FONT['family'], 12),
            text_color=self.theme['accent_primary'],
            fg_color=self.theme['bg_tertiary'],
            corner_radius=8,
            padx=12,
            pady=4
        )
        self.variables_count_label.pack(side="left", padx=(0, 20))

        # Версия
        version = ctk.CTkLabel(
            stats_frame,
            text="v4.0 Pro",
            font=(ModernTheme.FONT['family'], 11, 'bold'),
            text_color=self.theme['accent_primary']
        )
        version.pack(side="left", padx=(0, 12))

        # Переключатель темы
        theme_switch = ctk.CTkSegmentedButton(
            topbar,
            values=["Dark", "Light"],
            command=self.toggle_theme,
            width=140,
            fg_color=self.theme['bg_tertiary'],
            selected_color=self.theme['accent_primary'],
            font=(ModernTheme.FONT['family'], 11)
        )
        theme_switch.grid(row=0, column=2, padx=24, pady=15, sticky="e")
        theme_switch.set("Dark")
        self.theme_switch = theme_switch

    def create_sidebar(self):
        """Левая боковая панель с потоками"""
        # === SIDEBAR CONTAINER ===
        self.sidebar = ctk.CTkFrame(
            self,
            width=280,
            corner_radius=0,
            fg_color=self.theme['bg_sidebar'],
            border_width=1,
            border_color=self.theme['border_primary']
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(2, weight=1)  # Thread list expandable
        self.sidebar.grid_columnconfigure(0, weight=1)

        # === HEADER: Потоки + Очистить ===
        header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=50)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)

        # Заголовок "Потоки"
        header_label = ctk.CTkLabel(
            header_frame,
            text="Потоки",
            font=(ModernTheme.FONT['family'], 14, 'bold'),
            text_color=self.theme['text_primary']
        )
        header_label.grid(row=0, column=0, padx=16, pady=12, sticky="w")

        # Кнопка "Очистить"
        clear_btn = ctk.CTkButton(
            header_frame,
            text="Очистить",
            width=80,
            height=28,
            corner_radius=6,
            fg_color=self.theme['accent_error'],
            hover_color="#ff4444",
            font=(ModernTheme.FONT['family'], 11),
            command=self.clear_all_threads
        )
        clear_btn.grid(row=0, column=1, padx=12, pady=12, sticky="e")

        # === PLACEHOLDER: Нет активных потоков ===
        self.threads_placeholder = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        self.threads_placeholder.grid(row=1, column=0, sticky="nsew", padx=16, pady=20)

        # Иконка ракеты
        rocket_label = ctk.CTkLabel(
            self.threads_placeholder,
            text="🚀",
            font=(ModernTheme.FONT['family'], 48)
        )
        rocket_label.pack(pady=(40, 10))

        no_threads_label = ctk.CTkLabel(
            self.threads_placeholder,
            text="Нет активных потоков",
            font=(ModernTheme.FONT['family'], 13, 'bold'),
            text_color=self.theme['text_secondary']
        )
        no_threads_label.pack()

        hint_label = ctk.CTkLabel(
            self.threads_placeholder,
            text='Настройте и запустите во вкладке\n"Запуск"',
            font=(ModernTheme.FONT['family'], 11),
            text_color=self.theme['text_secondary'],
            justify="center"
        )
        hint_label.pack(pady=(5, 0))

        # === SCROLLABLE THREAD LIST (hidden initially) ===
        self.threads_list_frame = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            scrollbar_button_color=self.theme['bg_tertiary'],
            scrollbar_button_hover_color=self.theme['accent_primary']
        )
        # Не показываем сразу - будет показан когда появятся потоки

        # === КНОПКА "ОСТАНОВИТЬ ВСЕ" (внизу) ===
        stop_all_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            height=60
        )
        stop_all_frame.grid(row=3, column=0, sticky="sew", padx=12, pady=12)
        stop_all_frame.grid_propagate(False)

        self.stop_all_btn = ctk.CTkButton(
            stop_all_frame,
            text="Остановить все",
            height=44,
            corner_radius=8,
            fg_color=self.theme['accent_error'],
            hover_color="#ff4444",
            font=(ModernTheme.FONT['family'], 13, 'bold'),
            command=self.stop_all_threads
        )
        self.stop_all_btn.pack(fill="x", expand=True)

        # === СТАТУС ВНИЗУ САЙДБАРА ===
        status_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
            height=30
        )
        status_frame.grid(row=4, column=0, sticky="sew", padx=12, pady=(0, 8))

        self.sidebar_status_label = ctk.CTkLabel(
            status_frame,
            text="✨ Готов к работе",
            font=(ModernTheme.FONT['family'], 10),
            text_color=self.theme['text_secondary']
        )
        self.sidebar_status_label.pack(anchor="w")

    def clear_all_threads(self):
        """Очистить все потоки"""
        self.threads_data.clear()
        self.update_threads_display()
        self.toast.info("Потоки очищены")

    def stop_all_threads(self):
        """Остановить все активные потоки"""
        self.stop_script()
        self.toast.warning("Остановка всех потоков...")

    def update_threads_display(self):
        """Обновить отображение потоков в сайдбаре"""
        # Подсчёт
        total = len(self.threads_data)
        active = sum(1 for t in self.threads_data.values() if t.get('status') == 'running')

        # Обновить счётчики в топбаре
        self.threads_count_label.configure(text=f"Потоков: {total}")
        self.active_count_label.configure(text=f"Активных: {active}")

        # Обновить индикатор
        if active > 0:
            self.threads_indicator.configure(text_color="#00ff00")  # Зелёный
        else:
            self.threads_indicator.configure(text_color="#666666")  # Серый

        # Показать placeholder или список
        if total == 0:
            self.threads_placeholder.grid(row=1, column=0, sticky="nsew", padx=16, pady=20)
            self.threads_list_frame.grid_forget()
        else:
            self.threads_placeholder.grid_forget()
            self.threads_list_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
            self._rebuild_threads_list()

    def _rebuild_threads_list(self):
        """Перестроить список потоков"""
        # Очистить старые виджеты
        for widget in self.threads_list_frame.winfo_children():
            widget.destroy()

        # Создать карточки для каждого потока
        for thread_id, data in self.threads_data.items():
            self._create_thread_card(thread_id, data)

    def _create_thread_card(self, thread_id: str, data: dict):
        """Создать карточку потока"""
        status = data.get('status', 'pending')
        progress = data.get('progress', 0)

        # Цвет статуса
        status_colors = {
            'pending': self.theme['text_secondary'],
            'running': self.theme['accent_success'],
            'completed': self.theme['accent_info'],
            'error': self.theme['accent_error']
        }
        status_color = status_colors.get(status, self.theme['text_secondary'])

        # Карточка
        card = ctk.CTkFrame(
            self.threads_list_frame,
            fg_color=self.theme['bg_tertiary'],
            corner_radius=8,
            height=60
        )
        card.pack(fill="x", pady=4)
        card.pack_propagate(False)

        # Индикатор статуса
        indicator = ctk.CTkLabel(
            card,
            text="●",
            font=(ModernTheme.FONT['family'], 14),
            text_color=status_color
        )
        indicator.pack(side="left", padx=(12, 8))

        # Информация
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=8)

        thread_label = ctk.CTkLabel(
            info_frame,
            text=f"Поток #{thread_id}",
            font=(ModernTheme.FONT['family'], 11, 'bold'),
            text_color=self.theme['text_primary']
        )
        thread_label.pack(anchor="w")

        status_label = ctk.CTkLabel(
            info_frame,
            text=status.capitalize(),
            font=(ModernTheme.FONT['family'], 10),
            text_color=status_color
        )
        status_label.pack(anchor="w")

        # Прогресс-бар (если running)
        if status == 'running':
            progress_bar = ctk.CTkProgressBar(
                card,
                width=60,
                height=8,
                corner_radius=4,
                fg_color=self.theme['bg_secondary'],
                progress_color=self.theme['accent_success']
            )
            progress_bar.pack(side="right", padx=12)
            progress_bar.set(progress)

    def add_thread(self, thread_id: str, status: str = 'pending'):
        """Добавить поток"""
        self.threads_data[thread_id] = {
            'status': status,
            'logs': [],
            'progress': 0
        }
        self.update_threads_display()

    def update_thread(self, thread_id: str, status: str = None, progress: float = None, log: str = None):
        """Обновить данные потока"""
        if thread_id in self.threads_data:
            if status:
                self.threads_data[thread_id]['status'] = status
            if progress is not None:
                self.threads_data[thread_id]['progress'] = progress
            if log:
                self.threads_data[thread_id]['logs'].append(log)
            self.update_threads_display()

    def update_variables_count(self, count: int):
        """Обновить счётчик переменных"""
        self.variables_count = count
        self.variables_count_label.configure(text=f"Переменных: {count}")

    def get_red_flags_patterns(self) -> list:
        """Получить список паттернов Red Flags"""
        if not hasattr(self, 'red_flags_textbox'):
            return []
        text = self.red_flags_textbox.get("1.0", "end-1c").strip()
        if not text:
            return []
        # Разбить по строкам и отфильтровать пустые
        patterns = [line.strip() for line in text.split('\n') if line.strip()]
        return patterns

    def create_main_content(self):
        """Главная область с CTkTabview"""
        # Main container - теперь в column 1 (справа от sidebar)
        main_container = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.theme['bg_primary']
        )
        main_container.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # === CTkTabview ===
        self.tabview = ctk.CTkTabview(
            main_container,
            corner_radius=16,
            fg_color=self.theme['bg_secondary'],
            segmented_button_fg_color=self.theme['bg_tertiary'],
            segmented_button_selected_color=self.theme['accent_primary'],
            segmented_button_selected_hover_color=self.theme['bg_hover'],
            segmented_button_unselected_color=self.theme['bg_tertiary'],
            segmented_button_unselected_hover_color=self.theme['bg_hover'],
            text_color=self.theme['text_primary']
        )
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)

        # Добавить вкладки (стиль Browser Automator Pro)
        self.tab_edit = self.tabview.add("🚀 Запуск")
        self.tab_recorder = self.tabview.add("📹 Recorder")
        self.tab_script = self.tabview.add("📝 Скрипт")
        self.tab_data = self.tabview.add("📊 Переменные")
        self.tab_proxies = self.tabview.add("🌐 Хелперы")
        self.tab_octo = self.tabview.add("⚙️ Настройки")
        self.tab_logs = self.tabview.add("📋 Логи")

        # Настроить вкладки
        self.setup_edit_tab()
        self.setup_recorder_tab()
        self.setup_script_tab()
        self.setup_data_tab()
        self.setup_proxies_tab()
        self.setup_octo_tab()
        self.setup_logs_tab()

    def setup_edit_tab(self):
        """Настроить главную вкладку Запуск - НОВЫЙ ДИЗАЙН"""
        tab = self.tab_edit
        tab.grid_columnconfigure(0, weight=3)  # Левая колонка (код) - 60%
        tab.grid_columnconfigure(1, weight=2)  # Правая колонка (настройки) - 40%
        tab.grid_rowconfigure(1, weight=1)     # Основной контент растягивается

        # ========== ВЕРХНЯЯ ПАНЕЛЬ УПРАВЛЕНИЯ ==========
        top_panel = ctk.CTkFrame(
            tab,
            fg_color=self.theme['bg_tertiary'],
            corner_radius=12,
            height=80
        )
        top_panel.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 8))
        top_panel.grid_propagate(False)
        top_panel.grid_columnconfigure(1, weight=1)

        # Количество потоков
        threads_frame = ctk.CTkFrame(top_panel, fg_color="transparent")
        threads_frame.grid(row=0, column=0, padx=16, pady=20, sticky="w")

        ctk.CTkLabel(
            threads_frame,
            text="Количество потоков:",
            font=(ModernTheme.FONT['family'], 12),
            text_color=self.theme['text_primary']
        ).pack(side="left", padx=(0, 8))

        self.threads_count_var = tk.StringVar(value="1")
        ctk.CTkEntry(
            threads_frame,
            textvariable=self.threads_count_var,
            width=60,
            height=36,
            font=(ModernTheme.FONT['family'], 12)
        ).pack(side="left")

        # Провайдер
        provider_frame = ctk.CTkFrame(top_panel, fg_color="transparent")
        provider_frame.grid(row=0, column=1, padx=16, pady=20, sticky="w")

        self.provider_selector = ctk.CTkComboBox(
            provider_frame,
            values=self.available_providers,
            width=180,
            height=36,
            font=(ModernTheme.FONT['family'], 11),
            state="readonly",
            command=self.on_provider_changed,
            fg_color=self.theme['accent_primary'],
            button_color=self.theme['accent_secondary']
        )
        self.provider_selector.set(self.current_provider)
        self.provider_selector.pack(side="left")

        # Кнопки запуска
        buttons_frame = ctk.CTkFrame(top_panel, fg_color="transparent")
        buttons_frame.grid(row=0, column=2, padx=16, pady=20, sticky="e")

        self.run_btn = ctk.CTkButton(
            buttons_frame,
            text="🚀 Запустить",
            width=130,
            height=40,
            corner_radius=10,
            fg_color=self.theme['accent_success'],
            font=(ModernTheme.FONT['family'], 12, 'bold'),
            command=self.start_script
        )
        self.run_btn.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            buttons_frame,
            text="⏹️ Тест (1 поток)",
            width=130,
            height=40,
            corner_radius=10,
            fg_color=self.theme['bg_secondary'],
            font=(ModernTheme.FONT['family'], 11),
            command=lambda: self.start_script(test_mode=True)
        ).pack(side="left")

        # ========== ЛЕВАЯ КОЛОНКА: КОД ==========
        left_panel = ctk.CTkFrame(
            tab,
            fg_color=self.theme['bg_tertiary'],
            corner_radius=12
        )
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(16, 8), pady=8)
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)

        # Заголовок левой панели
        left_header = ctk.CTkFrame(left_panel, fg_color="transparent", height=50)
        left_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 0))
        left_header.grid_propagate(False)

        ctk.CTkLabel(
            left_header,
            text="📝 Код автоматизации",
            font=(ModernTheme.FONT['family'], 14, 'bold'),
            text_color=self.theme['text_primary']
        ).pack(side="left")

        # Кнопки для кода
        code_buttons = ctk.CTkFrame(left_header, fg_color="transparent")
        code_buttons.pack(side="right")

        ctk.CTkButton(
            code_buttons,
            text="📂 Загрузить",
            width=100,
            height=32,
            corner_radius=8,
            fg_color=self.theme['accent_info'],
            font=(ModernTheme.FONT['family'], 10),
            command=self.import_from_file
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            code_buttons,
            text="📋 Вставить",
            width=100,
            height=32,
            corner_radius=8,
            fg_color=self.theme['accent_secondary'],
            font=(ModernTheme.FONT['family'], 10),
            command=self.import_from_clipboard
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            code_buttons,
            text="✨ Генерация",
            width=100,
            height=32,
            corner_radius=8,
            fg_color=self.theme['accent_primary'],
            font=(ModernTheme.FONT['family'], 10),
            command=self.generate_playwright_script
        ).pack(side="left", padx=2)

        # Редактор кода
        self.code_editor = ctk.CTkTextbox(
            left_panel,
            font=('Consolas', 12),
            fg_color=self.theme['bg_secondary'],
            text_color=self.theme['text_primary'],
            wrap="none",
            corner_radius=8
        )
        self.code_editor.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)

        # Placeholder текст
        self.code_editor.insert("1.0", '''# Вставьте сюда ваш Playwright код
# Пример:
# page.goto("https://example.com")
# page.fill("#email", data["email"])
# page.click("button[type='submit']")
''')

        # ========== ПРАВАЯ КОЛОНКА: НАСТРОЙКИ (СКРОЛЛИРУЕМАЯ) ==========
        right_panel = ctk.CTkScrollableFrame(
            tab,
            fg_color=self.theme['bg_tertiary'],
            corner_radius=12,
            scrollbar_button_color=self.theme['bg_secondary'],
            scrollbar_button_hover_color=self.theme['accent_primary']
        )
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=8)
        right_panel.grid_columnconfigure(0, weight=1)

        # === ЦЕЛЕВОЙ URL ===
        self._create_settings_section(right_panel, "🎯 ЦЕЛЕВОЙ URL", 0)
        url_frame = ctk.CTkFrame(right_panel, fg_color=self.theme['bg_secondary'], corner_radius=8)
        url_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))

        self.target_url_var = tk.StringVar(value="https://www.wikipedia.org")
        ctk.CTkEntry(
            url_frame,
            textvariable=self.target_url_var,
            height=36,
            font=(ModernTheme.FONT['family'], 11),
            placeholder_text="https://example.com"
        ).pack(fill="x", padx=8, pady=8)

        ctk.CTkLabel(
            url_frame,
            text="💡 URL автоматически берётся из Recorder. Переменные: {{random_number}}",
            font=(ModernTheme.FONT['family'], 9),
            text_color=self.theme['accent_warning']
        ).pack(anchor="w", padx=8, pady=(0, 8))

        # === ПАРАМЕТРЫ ВЫПОЛНЕНИЯ ===
        self._create_settings_section(right_panel, "⚙️ ПАРАМЕТРЫ ВЫПОЛНЕНИЯ", 2)
        params_frame = ctk.CTkFrame(right_panel, fg_color=self.theme['bg_secondary'], corner_radius=8)
        params_frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 12))
        params_frame.grid_columnconfigure(1, weight=1)

        # Таймаут
        ctk.CTkLabel(params_frame, text="Таймаут (сек):", font=(ModernTheme.FONT['family'], 11)).grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.click_timeout_var = tk.StringVar(value="60")
        ctk.CTkEntry(params_frame, textvariable=self.click_timeout_var, width=80).grid(row=0, column=1, padx=8, pady=8, sticky="w")

        # Задержка
        ctk.CTkLabel(params_frame, text="Задержка между потоками:", font=(ModernTheme.FONT['family'], 11)).grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.action_delay_var = tk.StringVar(value="2000")
        delay_frame = ctk.CTkFrame(params_frame, fg_color="transparent")
        delay_frame.grid(row=1, column=1, padx=8, pady=8, sticky="w")
        ctk.CTkEntry(delay_frame, textvariable=self.action_delay_var, width=80).pack(side="left")
        ctk.CTkLabel(delay_frame, text="мс (мин. 2 сек!)", font=(ModernTheme.FONT['family'], 9), text_color=self.theme['text_secondary']).pack(side="left", padx=5)

        # Чекбоксы
        self.close_on_error_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            params_frame, text="Закрывать при ошибке / red flag",
            variable=self.close_on_error_var,
            font=(ModernTheme.FONT['family'], 11),
            fg_color=self.theme['accent_error']
        ).grid(row=2, column=0, columnspan=2, padx=8, pady=4, sticky="w")

        self.humanize_enabled_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            params_frame, text="Человекоподобный режим",
            variable=self.humanize_enabled_var,
            font=(ModernTheme.FONT['family'], 11),
            fg_color=self.theme['accent_success']
        ).grid(row=3, column=0, columnspan=2, padx=8, pady=(4, 8), sticky="w")

        # === ПРОКСИ ===
        self._create_settings_section(right_panel, "🌐 ПРОКСИ", 4)
        proxy_frame = ctk.CTkFrame(right_panel, fg_color=self.theme['bg_secondary'], corner_radius=8)
        proxy_frame.grid(row=5, column=0, sticky="ew", padx=12, pady=(0, 12))

        self.use_proxy_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            proxy_frame, text="Использовать прокси",
            variable=self.use_proxy_var,
            font=(ModernTheme.FONT['family'], 11)
        ).pack(anchor="w", padx=8, pady=8)

        self.delete_proxy_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            proxy_frame, text="Удалять прокси после использования",
            variable=self.delete_proxy_var,
            font=(ModernTheme.FONT['family'], 11),
            fg_color=self.theme['accent_error']
        ).pack(anchor="w", padx=8, pady=(0, 8))

        # Путь к файлу прокси
        proxy_path_frame = ctk.CTkFrame(proxy_frame, fg_color="transparent")
        proxy_path_frame.pack(fill="x", padx=8, pady=(0, 8))
        ctk.CTkLabel(proxy_path_frame, text="Файл:", font=(ModernTheme.FONT['family'], 10)).pack(side="left")
        self.proxy_file_var = tk.StringVar(value="/home/qwe/varimp/browser-automator/pr")
        ctk.CTkEntry(proxy_path_frame, textvariable=self.proxy_file_var, width=200, height=28).pack(side="left", padx=5)
        ctk.CTkButton(proxy_path_frame, text="📁", width=28, height=28, command=self.browse_proxy_file).pack(side="left")

        # === RED FLAGS ===
        self._create_settings_section(right_panel, "🚩 RED FLAGS (АВТО-ЗАКРЫТИЕ)", 6)
        red_flags_frame = ctk.CTkFrame(right_panel, fg_color=self.theme['bg_secondary'], corner_radius=8)
        red_flags_frame.grid(row=7, column=0, sticky="ew", padx=12, pady=(0, 12))

        self.red_flags_enabled_var = tk.BooleanVar(value=True)
        self.red_flags_textbox = ctk.CTkTextbox(
            red_flags_frame,
            height=120,
            font=('Consolas', 10),
            fg_color=self.theme['bg_tertiary'],
            corner_radius=6
        )
        self.red_flags_textbox.pack(fill="x", padx=8, pady=8)
        self.red_flags_textbox.insert("1.0", "captcha\nblocked\nforbidden\nrate limit\ntoo many requests\naccess denied\nsuspicious activity\nverify you are human\nplease try again later\ntemporarily unavailable")

        # === CSV ДАННЫЕ ===
        self._create_settings_section(right_panel, "📊 CSV ДАННЫЕ", 8)
        csv_frame = ctk.CTkFrame(right_panel, fg_color=self.theme['bg_secondary'], corner_radius=8)
        csv_frame.grid(row=9, column=0, sticky="ew", padx=12, pady=(0, 12))

        csv_buttons = ctk.CTkFrame(csv_frame, fg_color="transparent")
        csv_buttons.pack(fill="x", padx=8, pady=8)

        self.csv_status_label = ctk.CTkLabel(
            csv_buttons,
            text="Не загружен",
            font=(ModernTheme.FONT['family'], 11),
            text_color=self.theme['accent_error']
        )
        self.csv_status_label.pack(side="left")

        ctk.CTkButton(
            csv_buttons,
            text="📊 Загрузить CSV",
            width=130,
            height=32,
            corner_radius=8,
            fg_color=self.theme['accent_warning'],
            command=self.load_csv
        ).pack(side="right")

        ctk.CTkButton(
            csv_buttons,
            text="✨ Автопарсинг",
            width=110,
            height=32,
            corner_radius=8,
            fg_color=self.theme['accent_success'],
            command=self.auto_parse_data_from_editor
        ).pack(side="right", padx=5)

        # Лимит итераций
        iterations_frame = ctk.CTkFrame(csv_frame, fg_color="transparent")
        iterations_frame.pack(fill="x", padx=8, pady=(0, 8))
        ctk.CTkLabel(iterations_frame, text="Лимит итераций:", font=(ModernTheme.FONT['family'], 10)).pack(side="left")
        self.max_iterations_var = tk.StringVar(value="")
        ctk.CTkEntry(iterations_frame, textvariable=self.max_iterations_var, width=60, placeholder_text="все").pack(side="left", padx=5)
        ctk.CTkLabel(iterations_frame, text="(пусто = все строки)", font=(ModernTheme.FONT['family'], 9), text_color=self.theme['text_secondary']).pack(side="left")

        # ========== НИЖНЯЯ ПАНЕЛЬ: STOP + ЛИМИТ ==========
        bottom_panel = ctk.CTkFrame(
            tab,
            fg_color="transparent",
            height=60
        )
        bottom_panel.grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 16))
        bottom_panel.grid_propagate(False)

        self.stop_btn = ctk.CTkButton(
            bottom_panel,
            text="⏹️ ОСТАНОВИТЬ",
            width=200,
            height=44,
            corner_radius=10,
            fg_color=self.theme['accent_error'],
            state="disabled",
            font=(ModernTheme.FONT['family'], 12, 'bold'),
            command=self.stop_script
        )
        self.stop_btn.pack(side="left")
        self.stop_btn_main = self.stop_btn

        ctk.CTkButton(
            bottom_panel,
            text="💾 Сохранить скрипт",
            width=150,
            height=44,
            corner_radius=10,
            fg_color=self.theme['accent_info'],
            font=(ModernTheme.FONT['family'], 11),
            command=self.save_script
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            bottom_panel,
            text="🗑️ Очистить логи",
            width=130,
            height=44,
            corner_radius=10,
            fg_color=self.theme['accent_secondary'],
            font=(ModernTheme.FONT['family'], 11),
            command=self.clear_logs
        ).pack(side="left")

        # Инициализация дополнительных переменных для совместимости
        self._init_compatibility_vars()

    def _create_settings_section(self, parent, title: str, row: int):
        """Создать заголовок секции настроек"""
        header = ctk.CTkFrame(parent, fg_color="transparent", height=30)
        header.grid(row=row, column=0, sticky="ew", padx=12, pady=(12, 4))

        ctk.CTkLabel(
            header,
            text=title,
            font=(ModernTheme.FONT['family'], 12, 'bold'),
            text_color=self.theme['accent_error'] if 'RED' in title else self.theme['accent_primary']
        ).pack(side="left")

    def _init_compatibility_vars(self):
        """Инициализация переменных для совместимости со старым кодом"""
        # Переменные которые используются в generate_playwright_script
        if not hasattr(self, 'navigation_timeout_var'):
            self.navigation_timeout_var = tk.StringVar(value="15")
        if not hasattr(self, 'simulate_typing_var'):
            self.simulate_typing_var = tk.BooleanVar(value=True)
        if not hasattr(self, 'typing_delay_var'):
            self.typing_delay_var = tk.StringVar(value="100")
        if not hasattr(self, 'network_patterns_var'):
            self.network_patterns_var = tk.StringVar(value="")
        if not hasattr(self, 'disposable_profiles_var'):
            self.disposable_profiles_var = tk.BooleanVar(value=False)
        if not hasattr(self, 'typing_speed_var'):
            self.typing_speed_var = tk.StringVar(value="normal")
        if not hasattr(self, 'mouse_speed_var'):
            self.mouse_speed_var = tk.StringVar(value="normal")
        if not hasattr(self, 'scroll_behavior_var'):
            self.scroll_behavior_var = tk.StringVar(value="smooth")
        if not hasattr(self, 'make_typos_var'):
            self.make_typos_var = tk.BooleanVar(value=True)
        if not hasattr(self, 'typo_rate_var'):
            self.typo_rate_var = tk.StringVar(value="0.05")
        if not hasattr(self, 'page_exploration_enabled_var'):
            self.page_exploration_enabled_var = tk.BooleanVar(value=True)
        if not hasattr(self, 'exploration_intensity_var'):
            self.exploration_intensity_var = tk.StringVar(value="normal")

    def browse_proxy_file(self):
        """Выбрать файл с прокси"""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Выберите файл с прокси",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            self.proxy_file_var.set(filepath)
            self.toast.success(f"Файл прокси: {filepath}")

    def setup_recorder_tab(self):
        """Настроить вкладку Recorder"""
        tab = self.tab_recorder
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Заголовок
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=24)

        ctk.CTkLabel(
            header,
            text="📹 Recorder - Запись действий браузера",
            font=(ModernTheme.FONT['family'], 16, 'bold'),
            text_color=self.theme['text_primary']
        ).pack(side="left")

        # Кнопки управления
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        self.record_btn = ctk.CTkButton(
            btn_frame,
            text="🔴 Начать запись",
            width=150,
            height=40,
            corner_radius=10,
            fg_color=self.theme['accent_error'],
            font=(ModernTheme.FONT['family'], 12, 'bold'),
            command=self.start_recording
        )
        self.record_btn.pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="⏹️ Остановить",
            width=120,
            height=40,
            corner_radius=10,
            fg_color=self.theme['accent_secondary'],
            font=(ModernTheme.FONT['family'], 12),
            command=self.stop_recording
        ).pack(side="left", padx=5)

        # Область для записанных действий
        recorder_frame = ctk.CTkFrame(
            tab,
            fg_color=self.theme['bg_tertiary'],
            corner_radius=12,
            border_width=1,
            border_color=self.theme['border_primary']
        )
        recorder_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        recorder_frame.grid_columnconfigure(0, weight=1)
        recorder_frame.grid_rowconfigure(0, weight=1)

        self.recorder_textbox = ctk.CTkTextbox(
            recorder_frame,
            font=('Consolas', 11),
            fg_color=self.theme['bg_tertiary'],
            text_color=self.theme['text_primary'],
            wrap="none"
        )
        self.recorder_textbox.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.recorder_textbox.insert("1.0", "# Записанные действия появятся здесь\n# Нажмите 'Начать запись' для начала\n")

    def start_recording(self):
        """Начать запись действий"""
        self.toast.info("🔴 Запись начата...")
        self.record_btn.configure(text="🔴 Идёт запись...", fg_color="#ff4444")

    def stop_recording(self):
        """Остановить запись"""
        self.toast.success("⏹️ Запись остановлена")
        self.record_btn.configure(text="🔴 Начать запись", fg_color=self.theme['accent_error'])

    def setup_script_tab(self):
        """Настроить вкладку Скрипт"""
        tab = self.tab_script
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Заголовок
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=24)

        ctk.CTkLabel(
            header,
            text="📝 Скрипт - Редактор сгенерированного кода",
            font=(ModernTheme.FONT['family'], 16, 'bold'),
            text_color=self.theme['text_primary']
        ).pack(side="left")

        # Кнопки
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="💾 Сохранить",
            width=120,
            height=40,
            corner_radius=10,
            fg_color=self.theme['accent_info'],
            font=(ModernTheme.FONT['family'], 12),
            command=self.save_script
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="📋 Копировать",
            width=120,
            height=40,
            corner_radius=10,
            fg_color=self.theme['accent_secondary'],
            font=(ModernTheme.FONT['family'], 12),
            command=self.copy_script
        ).pack(side="left", padx=5)

        # Редактор скрипта
        script_frame = ctk.CTkFrame(
            tab,
            fg_color=self.theme['bg_tertiary'],
            corner_radius=12,
            border_width=1,
            border_color=self.theme['border_primary']
        )
        script_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        script_frame.grid_columnconfigure(0, weight=1)
        script_frame.grid_rowconfigure(0, weight=1)

        self.script_textbox = ctk.CTkTextbox(
            script_frame,
            font=('Consolas', 11),
            fg_color=self.theme['bg_tertiary'],
            text_color=self.theme['text_primary'],
            wrap="none"
        )
        self.script_textbox.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.script_textbox.insert("1.0", "# Сгенерированный скрипт появится здесь\n# Используйте вкладку 'Запуск' для генерации\n")

    def copy_script(self):
        """Копировать скрипт в буфер обмена"""
        script = self.script_textbox.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(script)
        self.toast.success("📋 Скрипт скопирован")

    def setup_data_tab(self):
        """Настроить вкладку Data"""
        self.data_tab_widget = DataTab(self.tab_data, self.theme, self.toast)
        self.data_tab_widget.pack(fill="both", expand=True)

    def setup_proxies_tab(self):
        """Настроить вкладку Proxies"""
        # 🔥 Передаём callback для централизованного сохранения
        self.proxy_tab_widget = ProxyTab(
            self.tab_proxies,
            self.theme,
            self.config,
            self.toast,
            save_callback=self.save_config  # ← ЕДИНСТВЕННОЕ МЕСТО сохранения config.json
        )
        self.proxy_tab_widget.pack(fill="both", expand=True)

    def setup_octo_tab(self):
        """Настроить вкладку Octo API"""
        print(f"[MAIN] setup_octo_tab(): config id = {id(self.config)}")
        token = self.config.get('octobrowser', {}).get('api_token', '')
        print(f"[MAIN] Передаю config с токеном: {token[:10]}..." if token else "[MAIN] Передаю config с пустым токеном")
        # 🔥 Передаём callback для централизованного сохранения
        self.octo_tab_widget = OctoAPITab(
            self.tab_octo,
            self.theme,
            self.config,
            self.toast,
            save_callback=self.save_config  # ← ЕДИНСТВЕННОЕ МЕСТО сохранения config.json
        )
        self.octo_tab_widget.pack(fill="both", expand=True)

    def setup_logs_tab(self):
        """Настроить вкладку Logs"""
        tab = self.tab_logs
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # Control buttons
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent", height=60)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=24)
        btn_frame.grid_propagate(False)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear Logs",
            command=self.clear_logs,
            height=44,
            width=150,
            corner_radius=12,
            fg_color=self.theme['accent_error'],
            font=(ModernTheme.FONT['family'], 12, 'bold')
        ).pack(side="right")

        # Logs display
        log_container = ctk.CTkFrame(
            tab,
            corner_radius=16,
            fg_color=self.theme['bg_tertiary'],
            border_width=1,
            border_color=self.theme['border_primary']
        )
        log_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        log_container.grid_columnconfigure(0, weight=1)
        log_container.grid_rowconfigure(0, weight=1)

        self.log_textbox = ctk.CTkTextbox(
            log_container,
            font=('Consolas', 11),
            fg_color=self.theme['bg_tertiary'],
            text_color=self.theme['text_primary'],
            wrap="word",
            border_width=0
        )
        self.log_textbox.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        # Configure tags for colored logs
        self.setup_log_tags()

    def setup_log_tags(self):
        """Настроить теги для цветных логов"""
        self.log_textbox.tag_config("INFO", foreground=self.theme['log_info'])
        self.log_textbox.tag_config("SUCCESS", foreground=self.theme['log_success'])
        self.log_textbox.tag_config("ERROR", foreground=self.theme['log_error'])
        self.log_textbox.tag_config("WARNING", foreground=self.theme['log_warning'])
        self.log_textbox.tag_config("DATA", foreground=self.theme['log_smart'])
        self.log_textbox.tag_config("API", foreground=self.theme['accent_primary'])
        self.log_textbox.tag_config("SMART", foreground=self.theme['log_smart'])

    def create_statusbar(self):
        """Нижний статусбар"""
        statusbar = ctk.CTkFrame(
            self,
            height=50,
            corner_radius=0,
            fg_color=self.theme['bg_sidebar'],
            border_width=1,
            border_color=self.theme['border_primary']
        )
        statusbar.grid(row=2, column=0, columnspan=2, sticky="ew")  # Span both columns
        statusbar.grid_propagate(False)
        statusbar.grid_columnconfigure(1, weight=1)

        # Status label
        self.status_label = ctk.CTkLabel(
            statusbar,
            text="✨ Готов к работе",
            font=(ModernTheme.FONT['family'], 11),
            text_color=self.theme['text_primary']
        )
        self.status_label.grid(row=0, column=0, padx=24, pady=12, sticky="w")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            statusbar,
            width=300,
            height=12,
            corner_radius=6,
            fg_color=self.theme['bg_tertiary'],
            progress_color=self.theme['accent_primary']
        )
        self.progress_bar.grid(row=0, column=1, padx=24, pady=12, sticky="e")
        self.progress_bar.set(0)

        # Версия справа
        version_label = ctk.CTkLabel(
            statusbar,
            text="v4.0 Pro",
            font=(ModernTheme.FONT['family'], 11, 'bold'),
            text_color=self.theme['accent_primary']
        )
        version_label.grid(row=0, column=2, padx=24, pady=12, sticky="e")

    # ========================================================================
    # ИМПОРТ КОДА
    # ========================================================================

    def import_from_file(self):
        """Импорт из файла"""
        filepath = filedialog.askopenfilename(
            title="Select Playwright Python file",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()

                self.process_imported_code(code)
                self.toast.success(f"✅ Импортирован: {Path(filepath).name}")
            except Exception as e:
                self.toast.error(f"Ошибка чтения: {e}")

    def import_from_clipboard(self):
        """Импорт из буфера"""
        try:
            code = self.clipboard_get()
            if code.strip():
                self.process_imported_code(code)
                self.toast.success("✅ Код импортирован из буфера")
            else:
                self.toast.warning("Буфер обмена пуст")
        except Exception as e:
            self.toast.error(f"Ошибка: {e}")

    def process_imported_code(self, code: str):
        """
        Обработка импортированного кода

        НОВАЯ ФИЧА: Автоматический парсинг данных!
        """
        try:
            # Определить тип
            if code.strip().startswith('{'):
                result = self.side_parser.parse_side_json(code)
            else:
                result = self.playwright_parser.parse_playwright_code(code)

            self.imported_data = result

            # Показать в редакторе
            self.code_editor.delete("1.0", "end")
            self.code_editor.insert("1.0", result.get('converted_code', code))

            # 🔥 АВТОМАТИЧЕСКИЙ ПАРСИНГ ДАННЫХ
            self.auto_parse_data(code)

            self.append_log(f"[INFO] Импортирован код с {len(result.get('actions', []))} действиями", "INFO")
            self.toast.success(f"Найдено {len(result.get('actions', []))} действий")

        except Exception as e:
            self.toast.error(f"Ошибка парсинга: {e}")
            self.append_log(f"[ERROR] {e}", "ERROR")

    def auto_parse_data(self, code: str):
        """
        🔥 АВТОМАТИЧЕСКИЙ ПАРСИНГ ДАННЫХ ИЗ КОДА

        Это ЛЕГЕНДАРНАЯ функция!
        """
        try:
            # Парсить .fill() действия
            fields = self.data_parser.parse_fill_actions(code)

            if not fields:
                self.append_log("[DATA] Данные для CSV не найдены", "DATA")
                return

            # Генерировать CSV данные
            headers, rows = self.data_parser.generate_csv_data(fields, num_rows=10)

            # Установить в Data Tab
            self.data_tab_widget.set_data(headers, rows)

            self.append_log(f"[DATA] Сгенерировано {len(rows)} строк с {len(headers)} полями", "DATA")
            self.append_log(f"[SMART] Автоопределение типов: {', '.join(set(f['type'] for f in fields))}", "SMART")

            self.toast.success(f"🎯 Умный парсинг: {len(fields)} полей → {len(rows)} строк CSV!")

        except Exception as e:
            self.append_log(f"[ERROR] Ошибка парсинга данных: {e}", "ERROR")

    def auto_parse_data_from_editor(self):
        """
        Автопарсинг данных из редактора кода в CSV

        Вызывается кнопкой "✨ Автопарсинг → CSV" в ШАГ 2
        """
        code = self.code_editor.get("1.0", "end-1c")

        if not code or not code.strip():
            self.toast.warning("⚠️ Сначала вставьте код автоматизации!")
            return

        # Проверить что это не пустой шаблон
        if code.strip().startswith("# Пример") or len(code.strip()) < 50:
            self.toast.warning("⚠️ Вставьте реальный код Playwright с действиями")
            return

        self.toast.info("🔍 Анализирую код...")
        self.append_log("[AUTOPARSE] Запущен автопарсинг данных из кода", "INFO")

        # Вызвать основную функцию парсинга
        self.auto_parse_data(code)

    # ========================================================================
    # ГЕНЕРАЦИЯ СКРИПТА
    # ========================================================================

    def _parse_network_patterns(self, patterns_str: str) -> list:
        """
        Парсит паттерны Network Capture в новом формате

        Формат: pattern:field1,field2; pattern2:field3
        Примеры:
            - "validate:external_id,user_id" → [{'pattern': 'validate', 'fields': ['external_id', 'user_id']}]
            - "validate:external_id; quotes:price" → [..., ...]
            - "validate" → [{'pattern': 'validate', 'fields': []}]  # без полей = весь response

        Returns:
            List[Dict] с ключами 'pattern' и 'fields'
        """
        if not patterns_str or not patterns_str.strip():
            return []

        result = []
        # Разделяем по точке с запятой (разные паттерны)
        pattern_groups = [p.strip() for p in patterns_str.split(';') if p.strip()]

        for group in pattern_groups:
            if ':' in group:
                # Формат: pattern:field1,field2
                pattern, fields_str = group.split(':', 1)
                pattern = pattern.strip()
                fields = [f.strip() for f in fields_str.split(',') if f.strip()]
                result.append({
                    'pattern': pattern,
                    'fields': fields
                })
            else:
                # Старый формат: просто pattern (без полей)
                pattern = group.strip()
                result.append({
                    'pattern': pattern,
                    'fields': []
                })

        return result

    def generate_playwright_script(self):
        """Генерация Playwright скрипта"""
        print("[DEBUG] generate_playwright_script() вызван")  # DEBUG

        try:
            # 🔥 ПОЛУЧИТЬ НАСТРОЙКИ ПРОФИЛЯ ИЗ OCTO API TAB
            profile_config = self.octo_tab_widget.get_profile_config()

            # Собрать конфигурацию из всех табов
            csv_path = self.config.get('ui_settings', {}).get('last_csv_path', 'data.csv')
            if not csv_path or csv_path.strip() == '':
                csv_path = 'data.csv'  # Default если пусто

            # 🔥 ПОЛУЧИТЬ НАСТРОЙКИ 9PROXY
            nine_proxy_config = self.config.get('nine_proxy', {})
            nine_proxy_manager = self.proxy_tab_widget.get_9proxy_manager()

            # Подготовить порты если 9Proxy включен
            nine_proxy_ports = []
            threads_count = int(self.threads_count_var.get()) if self.threads_count_var.get().isdigit() else 1

            # Дебаг информация
            print(f"[9PROXY DEBUG] nine_proxy_config: {nine_proxy_config}")
            print(f"[9PROXY DEBUG] nine_proxy_manager: {nine_proxy_manager}")
            print(f"[9PROXY DEBUG] manager.proxy_pool: {len(nine_proxy_manager.proxy_pool) if nine_proxy_manager and hasattr(nine_proxy_manager, 'proxy_pool') else 'N/A'}")

            nine_proxy_enabled = nine_proxy_config.get('enabled', False)
            nine_proxy_api_url = nine_proxy_config.get('api_url', 'http://localhost:50000')
            nine_proxy_strategy = nine_proxy_config.get('rotation', {}).get('strategy', 'sequential')
            nine_proxy_auto_rotate = nine_proxy_config.get('rotation', {}).get('auto_rotate', True)

            if nine_proxy_enabled and nine_proxy_manager and hasattr(nine_proxy_manager, 'proxy_pool') and len(nine_proxy_manager.proxy_pool) > 0:
                print(f"[9PROXY] ✅ Включен! Настраиваю {threads_count} портов...")
                print(f"[9PROXY] API URL: {nine_proxy_api_url}")
                print(f"[9PROXY] Стратегия: {nine_proxy_strategy}, Авто-ротация: {nine_proxy_auto_rotate}")
                print(f"[9PROXY] Прокси в пуле: {len(nine_proxy_manager.proxy_pool)}")

                # 🔥 9Proxy возвращает готовые порты - просто используем номера из пула
                # Берём порты из proxy_pool (они уже в формате 127.0.0.1:6000)
                nine_proxy_ports = []
                for proxy in nine_proxy_manager.proxy_pool[:threads_count]:
                    if isinstance(proxy, dict) and 'port' in proxy:
                        nine_proxy_ports.append(proxy['port'])
                    elif isinstance(proxy, str) and ':' in proxy:
                        # Парсим "127.0.0.1:6000" → 6000
                        port = int(proxy.split(':')[1])
                        nine_proxy_ports.append(port)

                # Если портов недостаточно - зациклим (используем уже собранные порты)
                if len(nine_proxy_ports) < threads_count and len(nine_proxy_ports) > 0:
                    original_count = len(nine_proxy_ports)
                    while len(nine_proxy_ports) < threads_count:
                        # Берём порт по модулю от количества уже собранных портов
                        port_index = len(nine_proxy_ports) % original_count
                        nine_proxy_ports.append(nine_proxy_ports[port_index])

                print(f"[9PROXY] Порты для потоков: {nine_proxy_ports}")
            elif nine_proxy_enabled:
                print(f"[9PROXY] ⚠️ Включен в настройках, но:")
                if not nine_proxy_manager:
                    print(f"[9PROXY]    - Менеджер не инициализирован")
                elif not hasattr(nine_proxy_manager, 'proxy_pool'):
                    print(f"[9PROXY]    - У менеджера нет атрибута proxy_pool")
                elif len(nine_proxy_manager.proxy_pool) == 0:
                    print(f"[9PROXY]    - Пул прокси пустой. Нажмите 'Fetch Proxies' во вкладке Proxies")
                nine_proxy_enabled = False  # Отключаем если условия не выполнены
            else:
                print(f"[9PROXY] ❌ Отключен в настройках")

            # 🔥 КРЕАТИВНОЕ РЕШЕНИЕ: CSV данные или путь
            config = {
                'api_token': self.config.get('octobrowser', {}).get('api_token', ''),
                'csv_filename': csv_path,
                'csv_data': self.csv_data_rows if self.csv_data_rows else None,  # 🔥 Встроенные данные
                'csv_embed_mode': self.csv_embed_mode,  # 🔥 Режим встраивания
                'target': 'library',  # По умолчанию library mode
                'use_proxy': self.config.get('proxy', {}).get('enabled', False),
                'proxy': self.config.get('proxy', {}),
                'proxy_list': self.config.get('proxy_list', {}),  # 🔥 СПИСОК ПРОКСИ ДЛЯ РОТАЦИИ
                'use_sms': False,  # Пока отключено
                'sms': self.config.get('sms', {}),
                # 🔥 ДОБАВЛЯЕМ НАСТРОЙКИ ПРОФИЛЯ
                'profile': profile_config,
                # 🔥 СИМУЛЯЦИЯ ВВОДА ТЕКСТА
                'simulate_typing': self.simulate_typing_var.get(),
                'typing_delay': int(self.typing_delay_var.get()) if self.typing_delay_var.get().isdigit() else 100,
                # 🔥 ЗАДЕРЖКА МЕЖДУ ДЕЙСТВИЯМИ (КЛИКИ, ЗАПОЛНЕНИЯ)
                'action_delay': float(self.action_delay_var.get()) if self.action_delay_var.get().replace('.', '', 1).isdigit() else 0.5,
                # 🔥 МНОГОПОТОЧНОСТЬ
                'threads_count': threads_count,
                # 🎯 ЛИМИТ ИТЕРАЦИЙ (None = все строки CSV)
                'max_iterations': int(self.max_iterations_var.get()) if self.max_iterations_var.get().strip() and self.max_iterations_var.get().isdigit() else None,
                # 🌐 NETWORK CAPTURE - парсинг нового формата pattern:field1,field2
                'network_capture_patterns': self._parse_network_patterns(self.network_patterns_var.get()),
                # 🔥🔥🔥 КРИТИЧНО: 9PROXY НАСТРОЙКИ 🔥🔥🔥
                'nine_proxy': nine_proxy_config,
                'nine_proxy_enabled': nine_proxy_enabled,  # Используем вычисленное значение
                'nine_proxy_ports': nine_proxy_ports,  # [6001, 6002, ...]
                'nine_proxy_api_url': nine_proxy_api_url,
                'nine_proxy_strategy': nine_proxy_strategy,
                'nine_proxy_auto_rotate': nine_proxy_auto_rotate,
                # 🗑️ ОДНОРАЗОВЫЕ ПРОФИЛИ
                'disposable_profiles': self.disposable_profiles_var.get(),
                # 🤖 HUMANIZE (антидетект)
                'humanize': {
                    'enabled': self.humanize_enabled_var.get(),
                    'typing_speed': self.typing_speed_var.get(),
                    'mouse_speed': self.mouse_speed_var.get(),
                    'scroll_behavior': self.scroll_behavior_var.get(),
                    'make_typos': self.make_typos_var.get(),
                    'typo_rate': float(self.typo_rate_var.get()) if self.typo_rate_var.get().replace('.', '', 1).isdigit() else 0.05,
                    'page_exploration_enabled': self.page_exploration_enabled_var.get(),
                    'exploration_intensity': self.exploration_intensity_var.get()
                },
                # 🚩 RED FLAGS (АВТО-ЗАКРЫТИЕ)
                'red_flags': {
                    'enabled': self.red_flags_enabled_var.get(),
                    'patterns': self.get_red_flags_patterns()
                }
            }

            print(f"[DEBUG] API Token: {config['api_token'][:10]}..." if config['api_token'] else "[DEBUG] API Token: пуст")
            print(f"[DEBUG] Profile config: tags={profile_config.get('tags')}, os={profile_config.get('fingerprint', {}).get('os')}")
            print(f"[DEBUG] 9Proxy передаётся в генератор:")
            print(f"[DEBUG]   - nine_proxy_enabled: {config['nine_proxy_enabled']}")
            print(f"[DEBUG]   - nine_proxy_ports: {config['nine_proxy_ports']}")
            print(f"[DEBUG]   - nine_proxy_api_url: {config['nine_proxy_api_url']}")
            print(f"[DEBUG]   - nine_proxy_strategy: {config['nine_proxy_strategy']}")
            print(f"[DEBUG]   - nine_proxy_auto_rotate: {config['nine_proxy_auto_rotate']}")

            # Проверка токена
            if not config['api_token']:
                self.toast.warning("⚠️ Введите API Token во вкладке Octo API")
                return

            # Получить пользовательский код из редактора или использовать placeholder
            user_code = self.code_editor.get("1.0", "end-1c").strip()
            if not user_code:
                # Если редактор пуст, используем placeholder код
                user_code = '''    # ==== ВАШ КОД АВТОМАТИЗАЦИИ ЗДЕСЬ ====
    # Примеры:
    # page.goto("https://example.com")
    # page.fill("#username", "myuser")
    # page.click("button[type='submit']")
    # page.wait_for_load_state("networkidle")

    print(f"[ITERATION {iteration_number}] Начало автоматизации")
    page.goto("https://example.com")
    print(f"[SUCCESS] Страница загружена")
'''

            print(f"[DEBUG] Длина user_code: {len(user_code)} символов")  # DEBUG

            # Динамический импорт провайдера
            selected_provider = self.provider_selector.get()
            self.append_log(f"[INFO] Генерация Playwright скрипта (Provider: {selected_provider})...", "INFO")

            try:
                # Принудительная перезагрузка модуля (для применения изменений без перезапуска GUI)
                generator_module = importlib.import_module(f"src.providers.{selected_provider}.generator")
                importlib.reload(generator_module)  # Перезагрузить модуль с диска
                generator = generator_module.Generator()
                generated_script = generator.generate_script(user_code, config)
            except Exception as e:
                self.append_log(f"[ERROR] Не удалось загрузить провайдер {selected_provider}: {e}", "ERROR")
                self.toast.error(f"❌ Ошибка загрузки провайдера: {e}")
                return

            # Вставить в редактор
            self.code_editor.delete("1.0", "end")
            self.code_editor.insert("1.0", generated_script)

            self.append_log("[SUCCESS] ✅ Скрипт сгенерирован успешно!", "SUCCESS")
            self.toast.success("✅ Playwright скрипт сгенерирован!")

        except Exception as e:
            print(f"[DEBUG] Ошибка генерации: {e}")  # DEBUG
            import traceback
            traceback.print_exc()  # DEBUG
            self.toast.error(f"❌ Ошибка генерации: {e}")
            self.append_log(f"[ERROR] {e}", "ERROR")

    # ========================================================================
    # ЗАПУСК СКРИПТА
    # ========================================================================

    def start_script(self):
        """Запуск скрипта"""
        print("[DEBUG] start_script() вызван")  # DEBUG
        code = self.code_editor.get("1.0", "end-1c").strip()
        print(f"[DEBUG] Длина кода в редакторе: {len(code)} символов")  # DEBUG

        if not code:
            print("[DEBUG] Редактор пуст! Нужно сгенерировать скрипт")  # DEBUG
            self.toast.error("⚠️ Редактор пуст! Сначала напишите код или сгенерируйте скрипт")
            return

        # 🔥 АВТОГЕНЕРАЦИЯ: Если в коде нет Octobrowser обертки, сгенерировать автоматически
        if 'check_local_api' not in code and 'create_profile' not in code:
            print("[DEBUG] Код не содержит Octobrowser обертку - запускаю автогенерацию...")
            self.toast.info("⚙️ Генерирую полный скрипт...")
            self.generate_playwright_script()
            # После генерации берем новый код
            code = self.code_editor.get("1.0", "end-1c").strip()
            if not code:
                self.toast.error("❌ Ошибка генерации скрипта")
                return

        try:
            # Сохранить скрипт
            output_dir = Path(self.config['script_settings']['output_directory'])
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script_path = output_dir / f"auto2tesst_{timestamp}.py"

            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(code)

            self.append_log(f"[INFO] Скрипт сохранен: {script_path}", "INFO")

            # UI обновление
            self.run_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            if hasattr(self, 'stop_btn_main'):
                self.stop_btn_main.configure(state="normal")
            self.status_label.configure(text="▶️ Running...")
            self.progress_bar.set(0.5)

            # Динамический импорт runner из провайдера
            selected_provider = self.provider_selector.get()
            try:
                runner_module = importlib.import_module(f"src.providers.{selected_provider}.runner")
                runner = runner_module.Runner()
                runner.set_output_callback(self.append_log)
                runner.run(str(script_path))
                self.current_runner = runner
            except Exception as e:
                self.toast.error(f"❌ Ошибка загрузки runner: {e}")
                self.append_log(f"[ERROR] {e}", "ERROR")
                self.script_finished()
                return

            self.toast.info("▶️ Скрипт запущен")

        except Exception as e:
            self.toast.error(f"Ошибка запуска: {e}")
            self.append_log(f"[ERROR] {e}", "ERROR")

    def stop_script(self):
        """Остановка скрипта"""
        try:
            if hasattr(self, 'current_runner'):
                self.current_runner.stop()
            self.toast.warning("⏹️ Скрипт остановлен")
            self.append_log("[WARNING] Скрипт остановлен пользователем", "WARNING")
            self.script_finished()
        except Exception as e:
            self.toast.error(f"Ошибка остановки: {e}")

    def on_provider_changed(self, selected_provider):
        """Обработчик смены провайдера"""
        self.current_provider = selected_provider
        self.append_log(f"[INFO] Провайдер изменен: {selected_provider}", "INFO")
        print(f"[PROVIDER] Выбран провайдер: {selected_provider}")

    def script_finished(self):
        """Завершение скрипта"""
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        if hasattr(self, 'stop_btn_main'):
            self.stop_btn_main.configure(state="disabled")
        self.status_label.configure(text="⚡ Ready")
        self.progress_bar.set(0)

    def save_script(self):
        """Сохранить скрипт"""
        code = self.code_editor.get("1.0", "end-1c")
        if not code.strip():
            self.toast.warning("Нечего сохранять")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save Script",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.toast.success(f"💾 Сохранено: {Path(filepath).name}")
            except Exception as e:
                self.toast.error(f"Ошибка сохранения: {e}")

    def reload_script(self):
        """Перезагрузить скрипт"""
        if self.imported_data:
            code = self.imported_data.get('converted_code', '')
            self.code_editor.delete("1.0", "end")
            self.code_editor.insert("1.0", code)
            self.toast.info("🔄 Скрипт перезагружен")
        else:
            self.toast.warning("Нет импортированного кода")

    def load_csv(self):
        """🔥 Загрузить CSV файл с данными"""
        filepath = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filepath:
            return

        try:
            import csv
            # Читаем CSV
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                self.toast.warning("⚠️ CSV файл пуст")
                return

            # Обработка пустых значений - заменить None и пустые значения на пустые строки
            # Это критично для json.dumps в генераторе, который не работает с None
            for row in rows:
                for key in row:
                    if row[key] is None or row[key] == '':
                        row[key] = ''
                    else:
                        # Конвертировать все значения в строки
                        row[key] = str(row[key]).strip()

            # Сохраняем данные
            self.csv_data_rows = rows
            self.csv_file_path = filepath

            # Сохраняем в конфигурацию
            if 'ui_settings' not in self.config:
                self.config['ui_settings'] = {}
            self.config['ui_settings']['last_csv_path'] = filepath
            self.save_config()

            # Уведомление
            filename = Path(filepath).name
            self.toast.success(f"📂 Загружено: {filename} ({len(rows)} строк)")
            self.append_log(f"[CSV] Загружен файл: {filename}, строк: {len(rows)}", "SUCCESS")

            # Обновить статус в интерфейсе
            if hasattr(self, 'csv_status_label'):
                self.csv_status_label.configure(
                    text=f"✅ {filename} ({len(rows)} строк)",
                    text_color=self.theme['accent_success']
                )

            # Показать первую строку для проверки
            if rows:
                fields = list(rows[0].keys())
                self.append_log(f"[CSV] Поля: {', '.join(fields)}", "DATA")

        except Exception as e:
            self.toast.error(f"❌ Ошибка загрузки CSV: {e}")
            self.append_log(f"[ERROR] CSV: {e}", "ERROR")

    # ========================================================================
    # ЛОГИ
    # ========================================================================

    def append_log(self, message: str, tag: str = "INFO"):
        """
        Добавить сообщение в лог с цветом

        Args:
            message: Сообщение
            tag: Тег для цвета (INFO, SUCCESS, ERROR, WARNING, DATA, API, SMART)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}\n"

        self.log_textbox.insert("end", formatted, tag)
        self.log_textbox.see("end")

    def clear_logs(self):
        """Очистить логи"""
        self.log_textbox.delete("1.0", "end")
        self.toast.info("Логи очищены")

    # ========================================================================
    # ДРУГОЕ
    # ========================================================================

    def apply_timeout_template(self, template_name: str):
        """
        Применить шаблон таймаутов

        Args:
            template_name: Название шаблона (very_fast, fast, normal, slow)
        """
        templates = {
            "very_fast": {
                "click": 5,
                "navigation": 8,
                "delay": 0.3,
                "name": "Очень быстро"
            },
            "fast": {
                "click": 7,
                "navigation": 12,
                "delay": 0.5,
                "name": "Быстро"
            },
            "normal": {
                "click": 10,
                "navigation": 15,
                "delay": 0.8,
                "name": "Нормально"
            },
            "slow": {
                "click": 15,
                "navigation": 25,
                "delay": 1.5,
                "name": "Медленно"
            }
        }

        if template_name not in templates:
            return

        template = templates[template_name]

        # Применить значения
        self.click_timeout_var.set(str(template["click"]))
        self.navigation_timeout_var.set(str(template["navigation"]))
        self.action_delay_var.set(str(template["delay"]))

        # Сохранить в конфиг
        if 'timeouts' not in self.config:
            self.config['timeouts'] = {}

        self.config['timeouts'] = {
            'click_timeout': template["click"],
            'navigation_timeout': template["navigation"],
            'action_delay': template["delay"],
            'template': template_name
        }

        self.save_config()
        self.toast.success(f"✅ Шаблон применен: {template['name']}")
        self.append_log(f"[SETTINGS] Шаблон таймаутов: {template['name']}", "INFO")

    def load_timeout_settings(self):
        """Загрузить настройки таймаутов из конфигурации"""
        timeouts = self.config.get('timeouts', {})

        click_timeout = timeouts.get('click_timeout', 10)
        navigation_timeout = timeouts.get('navigation_timeout', 15)
        action_delay = timeouts.get('action_delay', 0.5)

        self.click_timeout_var.set(str(click_timeout))
        self.navigation_timeout_var.set(str(navigation_timeout))
        self.action_delay_var.set(str(action_delay))

        template = timeouts.get('template')
        if template:
            self.append_log(f"[SETTINGS] Загружены таймауты: {template}", "INFO")

    def toggle_theme(self, value):
        """Переключить тему"""
        if "Dark" in value:
            ctk.set_appearance_mode("dark")
            self.toast.info("Темная тема 🌙")
        else:
            ctk.set_appearance_mode("light")
            self.toast.info("Светлая тема ☀️")

    def setup_hotkeys(self):
        """Горячие клавиши"""
        self.bind("<Control-i>", lambda e: self.import_from_file())
        self.bind("<Control-r>", lambda e: self.start_script())
        self.bind("<Escape>", lambda e: self.stop_script() if self.stop_btn.cget("state") == "normal" else None)
        self.bind("<Control-s>", lambda e: self.save_script())
        self.bind("<Control-l>", lambda e: self.clear_logs())


# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    """Запуск приложения"""
    print("=" * 60)
    print("🚀 auto2tesst v3.0 EPIC EDITION")
    print("=" * 60)
    print("✨ Умный парсер данных с Faker")
    print("📊 CSV генератор")
    print("🌐 Proxy менеджер")
    print("🐙 Полные настройки Octo API")
    print("📋 Цветные логи")
    print("=" * 60)

    app = ModernAppV3()
    app.mainloop()


if __name__ == "__main__":
    main()
