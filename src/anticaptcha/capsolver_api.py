# -*- coding: utf-8 -*-
"""
CapSolver API Integration Module
Supports: reCAPTCHA v2/v3, hCaptcha, Cloudflare Turnstile, ImageToText
API Docs: https://docs.capsolver.com/
"""

import time
import base64
import requests
from typing import Optional, Dict, Any


class CapSolverAPI:
    """CapSolver API client for solving various captcha types."""

    BASE_URL = "https://api.capsolver.com"

    # Supported captcha types
    CAPTCHA_TYPES = {
        'recaptcha_v2': 'ReCaptchaV2TaskProxyLess',
        'recaptcha_v2_proxy': 'ReCaptchaV2Task',
        'recaptcha_v3': 'ReCaptchaV3TaskProxyLess',
        'recaptcha_v3_proxy': 'ReCaptchaV3Task',
        'hcaptcha': 'HCaptchaTaskProxyLess',
        'hcaptcha_proxy': 'HCaptchaTask',
        'turnstile': 'AntiTurnstileTaskProxyLess',
        'turnstile_proxy': 'AntiTurnstileTask',
        'image_to_text': 'ImageToTextTask',
        'funcaptcha': 'FunCaptchaTaskProxyLess',
        'funcaptcha_proxy': 'FunCaptchaTask',
    }

    def __init__(self, api_key: str):
        """
        Initialize CapSolver client.

        Args:
            api_key: Your CapSolver API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def get_balance(self) -> float:
        """Get account balance."""
        response = self._request('/getBalance', {
            'clientKey': self.api_key
        })
        return response.get('balance', 0)

    def solve_recaptcha_v2(
        self,
        website_url: str,
        website_key: str,
        proxy: Optional[Dict] = None,
        is_invisible: bool = False,
        timeout: int = 120
    ) -> Optional[str]:
        """
        Solve reCAPTCHA v2.

        Args:
            website_url: URL of page with captcha
            website_key: reCAPTCHA site key (data-sitekey)
            proxy: Optional proxy dict {'type': 'http', 'host': '', 'port': '', 'login': '', 'password': ''}
            is_invisible: True if invisible reCAPTCHA
            timeout: Max wait time in seconds

        Returns:
            g-recaptcha-response token or None
        """
        task_type = 'recaptcha_v2_proxy' if proxy else 'recaptcha_v2'

        task = {
            'type': self.CAPTCHA_TYPES[task_type],
            'websiteURL': website_url,
            'websiteKey': website_key,
            'isInvisible': is_invisible
        }

        if proxy:
            task.update(self._format_proxy(proxy))

        return self._solve_task(task, timeout)

    def solve_recaptcha_v3(
        self,
        website_url: str,
        website_key: str,
        page_action: str = '',
        min_score: float = 0.7,
        proxy: Optional[Dict] = None,
        timeout: int = 120
    ) -> Optional[str]:
        """
        Solve reCAPTCHA v3.

        Args:
            website_url: URL of page with captcha
            website_key: reCAPTCHA site key
            page_action: Action parameter for v3
            min_score: Minimum score (0.1-0.9)
            proxy: Optional proxy dict
            timeout: Max wait time

        Returns:
            g-recaptcha-response token or None
        """
        task_type = 'recaptcha_v3_proxy' if proxy else 'recaptcha_v3'

        task = {
            'type': self.CAPTCHA_TYPES[task_type],
            'websiteURL': website_url,
            'websiteKey': website_key,
            'pageAction': page_action,
            'minScore': min_score
        }

        if proxy:
            task.update(self._format_proxy(proxy))

        return self._solve_task(task, timeout)

    def solve_hcaptcha(
        self,
        website_url: str,
        website_key: str,
        proxy: Optional[Dict] = None,
        timeout: int = 120
    ) -> Optional[str]:
        """
        Solve hCaptcha.

        Args:
            website_url: URL of page with captcha
            website_key: hCaptcha site key (data-sitekey)
            proxy: Optional proxy dict
            timeout: Max wait time

        Returns:
            h-captcha-response token or None
        """
        task_type = 'hcaptcha_proxy' if proxy else 'hcaptcha'

        task = {
            'type': self.CAPTCHA_TYPES[task_type],
            'websiteURL': website_url,
            'websiteKey': website_key
        }

        if proxy:
            task.update(self._format_proxy(proxy))

        return self._solve_task(task, timeout)

    def solve_turnstile(
        self,
        website_url: str,
        website_key: str,
        proxy: Optional[Dict] = None,
        timeout: int = 120
    ) -> Optional[str]:
        """
        Solve Cloudflare Turnstile.

        Args:
            website_url: URL of page with captcha
            website_key: Turnstile site key
            proxy: Optional proxy dict
            timeout: Max wait time

        Returns:
            cf-turnstile-response token or None
        """
        task_type = 'turnstile_proxy' if proxy else 'turnstile'

        task = {
            'type': self.CAPTCHA_TYPES[task_type],
            'websiteURL': website_url,
            'websiteKey': website_key
        }

        if proxy:
            task.update(self._format_proxy(proxy))

        return self._solve_task(task, timeout)

    def solve_image(
        self,
        image_base64: str,
        module: str = 'common',
        timeout: int = 60
    ) -> Optional[str]:
        """
        Solve image captcha (ImageToText).

        Args:
            image_base64: Base64 encoded image
            module: Recognition module ('common', 'queueit', etc.)
            timeout: Max wait time

        Returns:
            Recognized text or None
        """
        task = {
            'type': 'ImageToTextTask',
            'body': image_base64,
            'module': module
        }

        result = self._solve_task(task, timeout, result_key='text')
        return result

    def solve_funcaptcha(
        self,
        website_url: str,
        website_public_key: str,
        subdomain: str = '',
        proxy: Optional[Dict] = None,
        timeout: int = 120
    ) -> Optional[str]:
        """
        Solve FunCaptcha (Arkose Labs).

        Args:
            website_url: URL of page
            website_public_key: FunCaptcha public key
            subdomain: FunCaptcha subdomain
            proxy: Optional proxy dict
            timeout: Max wait time

        Returns:
            FunCaptcha token or None
        """
        task_type = 'funcaptcha_proxy' if proxy else 'funcaptcha'

        task = {
            'type': self.CAPTCHA_TYPES[task_type],
            'websiteURL': website_url,
            'websitePublicKey': website_public_key,
        }

        if subdomain:
            task['subdomain'] = subdomain

        if proxy:
            task.update(self._format_proxy(proxy))

        return self._solve_task(task, timeout)

    def _format_proxy(self, proxy: Dict) -> Dict:
        """Format proxy for CapSolver API."""
        return {
            'proxyType': proxy.get('type', 'http'),
            'proxyAddress': proxy.get('host', ''),
            'proxyPort': int(proxy.get('port', 0)),
            'proxyLogin': proxy.get('login', ''),
            'proxyPassword': proxy.get('password', '')
        }

    def _solve_task(
        self,
        task: Dict,
        timeout: int = 120,
        result_key: str = 'gRecaptchaResponse'
    ) -> Optional[str]:
        """
        Create task and wait for solution.

        Args:
            task: Task configuration
            timeout: Max wait time
            result_key: Key in solution dict

        Returns:
            Solution token/text or None
        """
        # Create task
        create_response = self._request('/createTask', {
            'clientKey': self.api_key,
            'task': task
        })

        if 'taskId' not in create_response:
            error = create_response.get('errorDescription', 'Unknown error')
            raise Exception(f"CapSolver createTask failed: {error}")

        task_id = create_response['taskId']

        # Poll for result
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self._request('/getTaskResult', {
                'clientKey': self.api_key,
                'taskId': task_id
            })

            status = result.get('status')

            if status == 'ready':
                solution = result.get('solution', {})
                # Try different response keys
                for key in [result_key, 'gRecaptchaResponse', 'token', 'text']:
                    if key in solution:
                        return solution[key]
                return None

            elif status == 'failed':
                error = result.get('errorDescription', 'Task failed')
                raise Exception(f"CapSolver task failed: {error}")

            # Still processing
            time.sleep(3)

        raise Exception(f"CapSolver timeout after {timeout}s")

    def _request(self, endpoint: str, data: Dict) -> Dict:
        """Make API request."""
        try:
            response = self.session.post(
                f"{self.BASE_URL}{endpoint}",
                json=data,
                timeout=30
            )
            return response.json()
        except Exception as e:
            raise Exception(f"CapSolver API error: {e}")


# Utility functions for generated scripts
def create_capsolver_client(api_key: str) -> CapSolverAPI:
    """Create CapSolver client instance."""
    return CapSolverAPI(api_key)


def solve_captcha_on_page(
    page,  # Playwright page
    capsolver: CapSolverAPI,
    captcha_type: str = 'auto',
    proxy: Optional[Dict] = None
) -> Optional[str]:
    """
    Detect and solve captcha on Playwright page.

    Args:
        page: Playwright page object
        capsolver: CapSolver client
        captcha_type: 'auto', 'recaptcha_v2', 'hcaptcha', 'turnstile'
        proxy: Optional proxy dict

    Returns:
        Solution token or None
    """
    url = page.url

    # Auto-detect captcha type
    if captcha_type == 'auto':
        html = page.content()

        if 'g-recaptcha' in html or 'grecaptcha' in html:
            captcha_type = 'recaptcha_v2'
        elif 'h-captcha' in html or 'hcaptcha' in html:
            captcha_type = 'hcaptcha'
        elif 'cf-turnstile' in html or 'turnstile' in html:
            captcha_type = 'turnstile'
        else:
            print("[CAPTCHA] No captcha detected")
            return None

    # Extract site key
    site_key = None

    if captcha_type == 'recaptcha_v2':
        # Try to find reCAPTCHA site key
        try:
            site_key = page.evaluate('''() => {
                const el = document.querySelector('[data-sitekey]');
                return el ? el.getAttribute('data-sitekey') : null;
            }''')
        except:
            pass

        if site_key:
            print(f"[CAPTCHA] Solving reCAPTCHA v2... sitekey={site_key[:20]}...")
            token = capsolver.solve_recaptcha_v2(url, site_key, proxy)
            if token:
                # Inject token
                page.evaluate(f'''(token) => {{
                    document.querySelector('[name="g-recaptcha-response"]').value = token;
                    if (typeof grecaptcha !== 'undefined' && grecaptcha.enterprise) {{
                        grecaptcha.enterprise.execute();
                    }}
                }}''', token)
            return token

    elif captcha_type == 'hcaptcha':
        try:
            site_key = page.evaluate('''() => {
                const el = document.querySelector('[data-sitekey]');
                return el ? el.getAttribute('data-sitekey') : null;
            }''')
        except:
            pass

        if site_key:
            print(f"[CAPTCHA] Solving hCaptcha... sitekey={site_key[:20]}...")
            token = capsolver.solve_hcaptcha(url, site_key, proxy)
            if token:
                page.evaluate(f'''(token) => {{
                    document.querySelector('[name="h-captcha-response"]').value = token;
                    document.querySelector('[name="g-recaptcha-response"]').value = token;
                }}''', token)
            return token

    elif captcha_type == 'turnstile':
        try:
            site_key = page.evaluate('''() => {
                const el = document.querySelector('[data-sitekey]');
                return el ? el.getAttribute('data-sitekey') : null;
            }''')
        except:
            pass

        if site_key:
            print(f"[CAPTCHA] Solving Turnstile... sitekey={site_key[:20]}...")
            token = capsolver.solve_turnstile(url, site_key, proxy)
            if token:
                page.evaluate(f'''(token) => {{
                    const input = document.querySelector('[name="cf-turnstile-response"]');
                    if (input) input.value = token;
                }}''', token)
            return token

    return None
