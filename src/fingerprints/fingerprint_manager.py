"""
Fingerprint Manager - управление отпечатками браузера для антидетект режима.
Генерирует и применяет реалистичные fingerprints, привязанные к геолокации прокси.
"""

import json
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone


class FingerprintManager:
    """Менеджер отпечатков браузера для антидетект режима."""

    # Маппинг timezone -> offset в минутах
    TIMEZONE_OFFSETS = {
        # US
        "America/New_York": -300,      # UTC-5
        "America/Chicago": -360,        # UTC-6
        "America/Denver": -420,         # UTC-7
        "America/Los_Angeles": -480,    # UTC-8
        "America/Phoenix": -420,        # UTC-7
        # Europe
        "Europe/London": 0,             # UTC+0
        "Europe/Paris": 60,             # UTC+1
        "Europe/Berlin": 60,            # UTC+1
        "Europe/Moscow": 180,           # UTC+3
        "Europe/Kiev": 120,             # UTC+2
        "Europe/Warsaw": 60,            # UTC+1
        "Europe/Amsterdam": 60,         # UTC+1
        "Europe/Madrid": 60,            # UTC+1
        "Europe/Rome": 60,              # UTC+1
        "Europe/Stockholm": 60,         # UTC+1
        "Europe/Oslo": 60,              # UTC+1
        "Europe/Copenhagen": 60,        # UTC+1
        "Europe/Helsinki": 120,         # UTC+2
        "Europe/Zurich": 60,            # UTC+1
        "Europe/Vienna": 60,            # UTC+1
        "Europe/Brussels": 60,          # UTC+1
        "Europe/Lisbon": 0,             # UTC+0
        "Europe/Prague": 60,            # UTC+1
        "Europe/Athens": 120,           # UTC+2
        "Europe/Bucharest": 120,        # UTC+2
        "Europe/Budapest": 60,          # UTC+1
        "Europe/Dublin": 0,             # UTC+0
        "Europe/Istanbul": 180,         # UTC+3
        "Europe/Minsk": 180,            # UTC+3
        # Asia
        "Asia/Tokyo": 540,              # UTC+9
        "Asia/Seoul": 540,              # UTC+9
        "Asia/Shanghai": 480,           # UTC+8
        "Asia/Hong_Kong": 480,          # UTC+8
        "Asia/Singapore": 480,          # UTC+8
        "Asia/Bangkok": 420,            # UTC+7
        "Asia/Ho_Chi_Minh": 420,        # UTC+7
        "Asia/Jakarta": 420,            # UTC+7
        "Asia/Kuala_Lumpur": 480,       # UTC+8
        "Asia/Manila": 480,             # UTC+8
        "Asia/Kolkata": 330,            # UTC+5:30
        "Asia/Dubai": 240,              # UTC+4
        "Asia/Riyadh": 180,             # UTC+3
        "Asia/Jerusalem": 120,          # UTC+2
        "Asia/Almaty": 360,             # UTC+6
        "Asia/Yekaterinburg": 300,      # UTC+5
        "Asia/Novosibirsk": 420,        # UTC+7
        "Asia/Vladivostok": 600,        # UTC+10
        # Americas
        "America/Toronto": -300,        # UTC-5
        "America/Vancouver": -480,      # UTC-8
        "America/Montreal": -300,       # UTC-5
        "America/Edmonton": -420,       # UTC-7
        "America/Sao_Paulo": -180,      # UTC-3
        "America/Mexico_City": -360,    # UTC-6
        "America/Tijuana": -480,        # UTC-8
        "America/Cancun": -300,         # UTC-5
        "America/Argentina/Buenos_Aires": -180,  # UTC-3
        "America/Santiago": -180,       # UTC-3
        "America/Bogota": -300,         # UTC-5
        # Oceania
        "Australia/Sydney": 660,        # UTC+11
        "Australia/Melbourne": 660,     # UTC+11
        "Australia/Brisbane": 600,      # UTC+10
        "Australia/Perth": 480,         # UTC+8
        "Australia/Adelaide": 630,      # UTC+10:30
        "Pacific/Auckland": 780,        # UTC+13
        # Africa
        "Africa/Johannesburg": 120,     # UTC+2
        "Africa/Cairo": 120,            # UTC+2
    }

    def __init__(self):
        """Инициализация менеджера отпечатков."""
        self.base_path = Path(__file__).parent
        self.geo_db = self._load_json('geo_database.json')
        self.fingerprints_db = self._load_json('fingerprints_database.json')
        self.stealth_script_template = self._load_stealth_script()

    def _load_json(self, filename: str) -> Dict:
        """Загрузка JSON файла."""
        filepath = self.base_path / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_stealth_script(self) -> str:
        """Загрузка шаблона stealth скрипта."""
        script_path = self.base_path / 'stealth' / 'stealth_script.js'
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ''

    def get_country_data(self, country_code: str) -> Optional[Dict]:
        """Получение данных страны по коду."""
        return self.geo_db.get(country_code.upper())

    def get_random_city(self, country_code: str) -> Optional[Dict]:
        """Получение случайного города страны."""
        country = self.get_country_data(country_code)
        if country and country.get('cities'):
            return random.choice(country['cities'])
        return None

    def get_random_fingerprint(self, preferred_os: str = None) -> Dict:
        """Получение случайного fingerprint из базы."""
        fingerprints = self.fingerprints_db.get('fingerprints', [])
        if not fingerprints:
            return self._generate_default_fingerprint()

        if preferred_os:
            filtered = [f for f in fingerprints if f.get('os', '').lower() == preferred_os.lower()]
            if filtered:
                return random.choice(filtered)

        return random.choice(fingerprints)

    def _generate_default_fingerprint(self) -> Dict:
        """Генерация дефолтного fingerprint."""
        return {
            "id": "default",
            "os": "Windows",
            "browser": "Chrome",
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "platform": "Win32",
            "vendor": "Google Inc.",
            "screen": {"width": 1920, "height": 1080, "colorDepth": 24, "pixelRatio": 1},
            "webgl": {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)"},
            "hardwareConcurrency": 8,
            "deviceMemory": 8,
            "maxTouchPoints": 0,
            "languages": ["en-US", "en"],
            "plugins": ["PDF Viewer", "Chrome PDF Viewer", "Chromium PDF Viewer"]
        }

    def generate_fingerprint_for_proxy(
        self,
        country_code: str,
        proxy_string: str = None,
        preferred_os: str = None
    ) -> Dict:
        """
        Генерация fingerprint привязанного к геолокации прокси.

        Args:
            country_code: Код страны (US, RU, DE и т.д.)
            proxy_string: Строка прокси для генерации seed
            preferred_os: Предпочитаемая OS (Windows, MacOS, Linux)

        Returns:
            Dict с полным fingerprint включая geo данные
        """
        # Получаем базовый fingerprint
        base_fp = self.get_random_fingerprint(preferred_os)

        # Получаем данные страны
        country = self.get_country_data(country_code)
        if not country:
            # Fallback на US
            country = self.get_country_data('US') or {
                'timezones': ['America/New_York'],
                'languages': ['en-US', 'en'],
                'accept_language': 'en-US,en;q=0.9',
                'cities': [{'name': 'New York', 'lat': 40.7128, 'lng': -74.0060, 'timezone': 'America/New_York'}]
            }

        # Выбираем случайный город
        city = random.choice(country.get('cities', [{'name': 'Unknown', 'lat': 0, 'lng': 0, 'timezone': country['timezones'][0]}]))

        # Получаем timezone
        timezone_name = city.get('timezone', country['timezones'][0])
        timezone_offset = self.TIMEZONE_OFFSETS.get(timezone_name, 0)

        # Формируем languages из country данных
        languages = country.get('languages', ['en-US', 'en'])

        # Генерируем уникальный seed на основе прокси (для консистентности)
        if proxy_string:
            seed = int(hashlib.md5(proxy_string.encode()).hexdigest()[:8], 16)
            random.seed(seed)

        # Собираем полный fingerprint
        fingerprint = {
            # Базовые параметры из fingerprint DB
            'userAgent': base_fp['userAgent'],
            'platform': base_fp['platform'],
            'vendor': base_fp['vendor'],
            'screen': base_fp['screen'],
            'webgl': base_fp['webgl'],
            'hardwareConcurrency': base_fp['hardwareConcurrency'],
            'deviceMemory': base_fp['deviceMemory'],
            'maxTouchPoints': base_fp['maxTouchPoints'],
            'plugins': base_fp.get('plugins', []),

            # Geo-привязанные параметры
            'languages': languages,
            'acceptLanguage': country.get('accept_language', 'en-US,en;q=0.9'),
            'timezone': timezone_name,
            'timezoneOffset': timezone_offset,
            'locale': country.get('locale', languages[0]),

            # Геолокация
            'latitude': city['lat'],
            'longitude': city['lng'],
            'city': city['name'],
            'country': country_code.upper(),
            'countryName': country.get('name', country_code),
        }

        # Сбрасываем seed
        random.seed()

        return fingerprint

    def generate_stealth_script(self, fingerprint: Dict) -> str:
        """
        Генерация JavaScript кода для применения fingerprint.

        Args:
            fingerprint: Dict с параметрами fingerprint

        Returns:
            JavaScript код для инъекции в страницу
        """
        if not self.stealth_script_template:
            return ''

        script = self.stealth_script_template

        # Заменяем плейсхолдеры
        replacements = {
            '{{USER_AGENT}}': fingerprint['userAgent'],
            '{{PLATFORM}}': fingerprint['platform'],
            '{{VENDOR}}': fingerprint['vendor'],
            '{{LANGUAGES}}': json.dumps(fingerprint['languages']),
            '{{HARDWARE_CONCURRENCY}}': str(fingerprint['hardwareConcurrency']),
            '{{DEVICE_MEMORY}}': str(fingerprint['deviceMemory']),
            '{{MAX_TOUCH_POINTS}}': str(fingerprint['maxTouchPoints']),
            '{{SCREEN_WIDTH}}': str(fingerprint['screen']['width']),
            '{{SCREEN_HEIGHT}}': str(fingerprint['screen']['height']),
            '{{COLOR_DEPTH}}': str(fingerprint['screen']['colorDepth']),
            '{{PIXEL_RATIO}}': str(fingerprint['screen']['pixelRatio']),
            '{{TIMEZONE}}': fingerprint['timezone'],
            '{{TIMEZONE_OFFSET}}': str(fingerprint['timezoneOffset']),
            '{{WEBGL_VENDOR}}': fingerprint['webgl']['vendor'],
            '{{WEBGL_RENDERER}}': fingerprint['webgl']['renderer'],
            '{{PLUGINS}}': json.dumps(fingerprint['plugins']),
            '{{LATITUDE}}': str(fingerprint['latitude']),
            '{{LONGITUDE}}': str(fingerprint['longitude']),
        }

        for placeholder, value in replacements.items():
            script = script.replace(placeholder, value)

        return script

    def get_playwright_context_options(self, fingerprint: Dict) -> Dict:
        """
        Получение опций для Playwright browser context.

        Args:
            fingerprint: Dict с параметрами fingerprint

        Returns:
            Dict с опциями для browser.new_context()
        """
        return {
            'user_agent': fingerprint['userAgent'],
            'viewport': {
                'width': fingerprint['screen']['width'],
                'height': fingerprint['screen']['height'] - 140  # Browser UI
            },
            'screen': {
                'width': fingerprint['screen']['width'],
                'height': fingerprint['screen']['height']
            },
            'device_scale_factor': fingerprint['screen']['pixelRatio'],
            'locale': fingerprint['locale'],
            'timezone_id': fingerprint['timezone'],
            'geolocation': {
                'latitude': fingerprint['latitude'],
                'longitude': fingerprint['longitude']
            },
            'permissions': ['geolocation'],
            'color_scheme': 'light',
            'extra_http_headers': {
                'Accept-Language': fingerprint['acceptLanguage']
            }
        }

    def get_launch_args(self, fingerprint: Dict) -> List[str]:
        """
        Получение аргументов запуска браузера для антидетект.

        Args:
            fingerprint: Dict с параметрами fingerprint

        Returns:
            List аргументов для browser.launch()
        """
        return [
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--disable-dev-shm-usage',
            '--disable-browser-side-navigation',
            '--disable-gpu-sandbox',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-background-networking',
            '--disable-sync',
            '--disable-translate',
            '--hide-scrollbars',
            '--metrics-recording-only',
            '--mute-audio',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            f'--window-size={fingerprint["screen"]["width"]},{fingerprint["screen"]["height"]}',
            f'--lang={fingerprint["languages"][0]}',
        ]

    def generate_fingerprint_code(self, country_code: str, proxy_string: str = None) -> str:
        """
        Генерация Python кода для использования fingerprint в скрипте.

        Args:
            country_code: Код страны
            proxy_string: Строка прокси

        Returns:
            Python код для вставки в генерируемый скрипт
        """
        fp = self.generate_fingerprint_for_proxy(country_code, proxy_string)
        context_options = self.get_playwright_context_options(fp)
        launch_args = self.get_launch_args(fp)
        stealth_script = self.generate_stealth_script(fp)

        code = f'''
# ==================== ANTIDETECT FINGERPRINT ====================
# Country: {fp['countryName']} ({fp['country']})
# City: {fp['city']}
# Timezone: {fp['timezone']}

FINGERPRINT_CONTEXT_OPTIONS = {json.dumps(context_options, indent=4, ensure_ascii=False)}

FINGERPRINT_LAUNCH_ARGS = {json.dumps(launch_args, indent=4)}

STEALTH_SCRIPT = """
{stealth_script}
"""

def apply_stealth(page):
    """Применение stealth скрипта к странице."""
    page.add_init_script(STEALTH_SCRIPT)
    print(f"[ANTIDETECT] Fingerprint applied: {{FINGERPRINT_CONTEXT_OPTIONS.get('locale', 'en-US')}}")
'''
        return code


# Утилиты для экспорта
def get_fingerprint_manager() -> FingerprintManager:
    """Получение singleton экземпляра FingerprintManager."""
    if not hasattr(get_fingerprint_manager, '_instance'):
        get_fingerprint_manager._instance = FingerprintManager()
    return get_fingerprint_manager._instance
