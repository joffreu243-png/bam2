"""
Proxy Tunnel - создание локальных туннелей для SOCKS5 прокси с авторизацией.

Chromium не поддерживает SOCKS5 с авторизацией напрямую.
Решение: создаём локальный HTTP прокси который перенаправляет через SOCKS5.

Использование:
    tunnel = ProxyTunnel()
    local_port = tunnel.create_tunnel('socks5://user:pass@host:port')
    # Используем localhost:local_port в Playwright
    tunnel.close_tunnel(local_port)
"""

import subprocess
import socket
import time
import threading
import atexit
from typing import Dict, Optional, Tuple
import re


class ProxyTunnel:
    """Менеджер локальных прокси-туннелей для SOCKS5 с авторизацией."""

    def __init__(self):
        self._tunnels: Dict[int, subprocess.Popen] = {}
        self._port_counter = 10800  # Начальный порт для туннелей
        self._lock = threading.Lock()
        # Регистрируем cleanup при выходе
        atexit.register(self.close_all_tunnels)

    def _find_free_port(self, start_port: int = 10800) -> int:
        """Найти свободный порт."""
        port = start_port
        while port < 65535:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('127.0.0.1', port))
                    return port
                except OSError:
                    port += 1
        raise RuntimeError("No free ports available")

    def _parse_proxy_string(self, proxy_string: str) -> Dict:
        """
        Парсинг строки прокси в компоненты.

        Поддерживаемые форматы:
        - socks5://user:pass@host:port
        - socks5://host:port:user:pass
        - host:port:user:pass (тип по умолчанию socks5)
        - user:pass@host:port
        """
        result = {
            'type': 'socks5',
            'host': '',
            'port': '',
            'user': '',
            'password': ''
        }

        proxy = proxy_string.strip()

        # Убираем протокол
        protocol_match = re.match(r'^(socks5|socks4|http|https)://', proxy, re.IGNORECASE)
        if protocol_match:
            result['type'] = protocol_match.group(1).lower()
            proxy = proxy[len(protocol_match.group(0)):]

        # Формат: user:pass@host:port
        if '@' in proxy:
            auth_part, host_part = proxy.rsplit('@', 1)
            if ':' in auth_part:
                result['user'], result['password'] = auth_part.split(':', 1)
            if ':' in host_part:
                result['host'], result['port'] = host_part.rsplit(':', 1)
            else:
                result['host'] = host_part
        # Формат: host:port:user:pass
        elif proxy.count(':') >= 3:
            parts = proxy.split(':')
            result['host'] = parts[0]
            result['port'] = parts[1]
            result['user'] = parts[2]
            result['password'] = ':'.join(parts[3:])  # Пароль может содержать :
        # Формат: host:port (без авторизации)
        elif ':' in proxy:
            result['host'], result['port'] = proxy.rsplit(':', 1)

        return result

    def create_tunnel(self, proxy_string: str) -> Tuple[int, bool]:
        """
        Создать локальный туннель для прокси.

        Args:
            proxy_string: Строка прокси (socks5://user:pass@host:port)

        Returns:
            Tuple[local_port, needs_tunnel]:
            - local_port: Порт локального туннеля
            - needs_tunnel: True если туннель создан, False если прокси без авторизации
        """
        proxy = self._parse_proxy_string(proxy_string)

        # Если нет авторизации - туннель не нужен
        if not proxy['user'] or not proxy['password']:
            return 0, False

        # Только для SOCKS5 нужен туннель (HTTP/HTTPS работают с auth)
        if proxy['type'] not in ['socks5', 'socks4']:
            return 0, False

        with self._lock:
            local_port = self._find_free_port(self._port_counter)
            self._port_counter = local_port + 1

            # Формируем URL для pproxy
            # pproxy -l http://127.0.0.1:local_port -r socks5://user:pass@host:port
            remote_url = f"{proxy['type']}://{proxy['user']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"

            try:
                # Запускаем pproxy как subprocess
                process = subprocess.Popen(
                    [
                        'python', '-m', 'pproxy',
                        '-l', f'http://127.0.0.1:{local_port}',
                        '-r', remote_url,
                        '-v'  # verbose для отладки
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    # Не показываем окно на Windows
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )

                # Даём время на запуск
                time.sleep(0.5)

                # Проверяем что процесс запустился
                if process.poll() is not None:
                    stderr = process.stderr.read().decode() if process.stderr else ''
                    raise RuntimeError(f"pproxy failed to start: {stderr}")

                self._tunnels[local_port] = process
                print(f"[PROXY TUNNEL] ✅ Created tunnel localhost:{local_port} -> {proxy['type']}://{proxy['host']}:{proxy['port']}")

                return local_port, True

            except FileNotFoundError:
                print("[PROXY TUNNEL] ❌ pproxy not found! Install it: pip install pproxy")
                raise
            except Exception as e:
                print(f"[PROXY TUNNEL] ❌ Failed to create tunnel: {e}")
                raise

    def close_tunnel(self, local_port: int):
        """Закрыть туннель по порту."""
        with self._lock:
            if local_port in self._tunnels:
                process = self._tunnels[local_port]
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception:
                    pass
                del self._tunnels[local_port]
                print(f"[PROXY TUNNEL] Closed tunnel on port {local_port}")

    def close_all_tunnels(self):
        """Закрыть все туннели."""
        with self._lock:
            for port, process in list(self._tunnels.items()):
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except:
                    try:
                        process.kill()
                    except:
                        pass
            self._tunnels.clear()
            print("[PROXY TUNNEL] All tunnels closed")


# Глобальный экземпляр
_tunnel_manager: Optional[ProxyTunnel] = None


def get_tunnel_manager() -> ProxyTunnel:
    """Получить глобальный менеджер туннелей."""
    global _tunnel_manager
    if _tunnel_manager is None:
        _tunnel_manager = ProxyTunnel()
    return _tunnel_manager


def create_proxy_tunnel(proxy_string: str) -> Tuple[str, int]:
    """
    Создать туннель для прокси если нужно.

    Args:
        proxy_string: Строка прокси

    Returns:
        Tuple[proxy_url, tunnel_port]:
        - proxy_url: URL для подключения (localhost или оригинальный)
        - tunnel_port: Порт туннеля (0 если туннель не создан)
    """
    manager = get_tunnel_manager()

    try:
        local_port, needs_tunnel = manager.create_tunnel(proxy_string)

        if needs_tunnel:
            return f'http://127.0.0.1:{local_port}', local_port
        else:
            # Туннель не нужен - возвращаем оригинальный прокси
            return proxy_string, 0

    except Exception as e:
        print(f"[PROXY TUNNEL] Failed: {e}, using original proxy")
        return proxy_string, 0


def close_proxy_tunnel(tunnel_port: int):
    """Закрыть туннель."""
    if tunnel_port > 0:
        manager = get_tunnel_manager()
        manager.close_tunnel(tunnel_port)
