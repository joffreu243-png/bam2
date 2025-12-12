"""
GeoIP Utility - определение геолокации по IP адресу прокси.
Использует бесплатные API для определения страны.
"""

import re
import socket
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse


class GeoIPResolver:
    """Класс для определения геолокации по IP."""

    # Бесплатные GeoIP API (в порядке приоритета)
    GEOIP_APIS = [
        'http://ip-api.com/json/{ip}?fields=status,countryCode,city,lat,lon,timezone',
        'https://ipapi.co/{ip}/json/',
        'https://ipwho.is/{ip}',
    ]

    def __init__(self):
        self._cache: Dict[str, Dict] = {}

    def extract_ip_from_proxy(self, proxy_string: str) -> Optional[str]:
        """
        Извлечение IP адреса из строки прокси.

        Args:
            proxy_string: Строка прокси в любом формате

        Returns:
            IP адрес или None
        """
        if not proxy_string:
            return None

        # Убираем протокол если есть
        proxy = proxy_string.strip()

        # Паттерны для разных форматов
        patterns = [
            # ip:port
            r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+',
            # ip:port:user:pass
            r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+:',
            # user:pass@ip:port
            r'@(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+',
            # protocol://ip:port
            r'://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+',
            # protocol://user:pass@ip:port
            r'://[^@]+@(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+',
            # hostname (попробуем resolve)
            r'^([a-zA-Z0-9\-\.]+):\d+',
        ]

        for pattern in patterns:
            match = re.search(pattern, proxy)
            if match:
                ip_or_host = match.group(1)
                # Проверяем, это IP или hostname
                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip_or_host):
                    return ip_or_host
                else:
                    # Пробуем разрешить hostname
                    try:
                        return socket.gethostbyname(ip_or_host)
                    except socket.gaierror:
                        continue

        return None

    def get_country_from_ip(self, ip: str) -> Optional[str]:
        """
        Получение кода страны по IP (синхронно через requests).

        Args:
            ip: IP адрес

        Returns:
            Код страны (US, RU, DE и т.д.) или None
        """
        if not ip:
            return None

        # Проверяем кеш
        if ip in self._cache:
            return self._cache[ip].get('country_code')

        try:
            import requests

            for api_template in self.GEOIP_APIS:
                try:
                    url = api_template.format(ip=ip)
                    response = requests.get(url, timeout=5)

                    if response.status_code == 200:
                        data = response.json()

                        # ip-api.com формат
                        if 'countryCode' in data:
                            country_code = data['countryCode']
                        # ipapi.co формат
                        elif 'country_code' in data:
                            country_code = data['country_code']
                        # ipwho.is формат
                        elif 'country_code' in data:
                            country_code = data['country_code']
                        else:
                            continue

                        # Сохраняем в кеш
                        self._cache[ip] = {
                            'country_code': country_code,
                            'city': data.get('city'),
                            'lat': data.get('lat') or data.get('latitude'),
                            'lon': data.get('lon') or data.get('longitude'),
                            'timezone': data.get('timezone')
                        }

                        return country_code

                except Exception:
                    continue

        except ImportError:
            pass

        return None

    def get_country_from_proxy(self, proxy_string: str) -> Optional[str]:
        """
        Получение кода страны из прокси строки.

        Args:
            proxy_string: Строка прокси

        Returns:
            Код страны или None
        """
        ip = self.extract_ip_from_proxy(proxy_string)
        if ip:
            return self.get_country_from_ip(ip)
        return None

    def get_full_geo_info(self, proxy_string: str) -> Optional[Dict]:
        """
        Получение полной информации о геолокации.

        Args:
            proxy_string: Строка прокси

        Returns:
            Dict с country_code, city, lat, lon, timezone или None
        """
        ip = self.extract_ip_from_proxy(proxy_string)
        if not ip:
            return None

        # Сначала пробуем получить страну (это заполнит кеш)
        self.get_country_from_ip(ip)

        return self._cache.get(ip)


def detect_country_from_proxy(proxy_string: str) -> str:
    """
    Утилитарная функция для определения страны по прокси.

    Args:
        proxy_string: Строка прокси

    Returns:
        Код страны или 'US' по умолчанию
    """
    resolver = GeoIPResolver()
    country = resolver.get_country_from_proxy(proxy_string)
    return country or 'US'


def generate_geoip_detection_code() -> str:
    """
    Генерация Python кода для определения гео по IP.

    Returns:
        Python код для вставки в генерируемый скрипт
    """
    return '''
# ==================== GEOIP DETECTION ====================

def detect_proxy_country(proxy_string: str) -> str:
    """Определение страны по IP прокси."""
    import re
    import socket

    # Извлекаем IP из прокси
    patterns = [
        r'^(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}):\\d+',
        r'@(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}):\\d+',
        r'://(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}):\\d+',
    ]

    ip = None
    for pattern in patterns:
        match = re.search(pattern, proxy_string)
        if match:
            ip = match.group(1)
            break

    if not ip:
        return 'US'

    try:
        import requests
        response = requests.get(f'http://ip-api.com/json/{ip}?fields=countryCode', timeout=5)
        if response.status_code == 200:
            return response.json().get('countryCode', 'US')
    except:
        pass

    return 'US'
'''
