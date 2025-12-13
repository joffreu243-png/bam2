"""
Script Template Generator for Human-Like Behavior

Generates embeddable Python code for use in generated automation scripts.
This module provides code strings that can be injected into generated scripts
without requiring external imports.
"""

from typing import Dict, Any


def generate_humanize_config_code(config: Dict[str, Any]) -> str:
    """
    Generate Python code for humanize configuration constants

    Args:
        config: Humanize configuration dictionary from GUI

    Returns:
        Python code string defining configuration constants
    """
    enabled = config.get('enabled', True)
    typing_speed = config.get('typing_speed', 'normal')
    mouse_speed = config.get('mouse_speed', 'normal')
    scroll_behavior = config.get('scroll_behavior', 'smooth')
    make_typos = config.get('make_typos', True)
    typo_rate = config.get('typo_rate', 0.05)
    page_exploration_enabled = config.get('page_exploration_enabled', True)
    exploration_intensity = config.get('exploration_intensity', 'normal')

    # Calculate speed multipliers
    speed_map = {'slow': 0.7, 'normal': 1.0, 'fast': 1.5}
    typing_multiplier = speed_map.get(typing_speed, 1.0)
    mouse_multiplier = speed_map.get(mouse_speed, 1.0)

    # Calculate delays based on speed
    base_keystroke_delay = (80, 200)
    keystroke_min = int(base_keystroke_delay[0] / typing_multiplier)
    keystroke_max = int(base_keystroke_delay[1] / typing_multiplier)

    base_mouse_delay = 8
    mouse_delay = int(base_mouse_delay / mouse_multiplier)

    return f'''# ============================================================
# HUMANIZE CONFIGURATION
# ============================================================
HUMANIZE_ENABLED = {enabled}
TYPING_SPEED = "{typing_speed}"  # slow, normal, fast
MOUSE_SPEED = "{mouse_speed}"    # slow, normal, fast
SCROLL_BEHAVIOR = "{scroll_behavior}"  # smooth, instant
MAKE_TYPOS = {make_typos}
TYPO_RATE = {typo_rate}
PAGE_EXPLORATION_ENABLED = {page_exploration_enabled}
EXPLORATION_INTENSITY = "{exploration_intensity}"  # light, normal, thorough

# Calculated timing values
KEYSTROKE_DELAY = ({keystroke_min}, {keystroke_max})  # ms between keystrokes
MOUSE_DELAY = {mouse_delay}  # ms between mouse move steps
'''


def generate_humanize_helpers_code() -> str:
    """
    Generate complete humanize helper functions code

    Returns:
        Python code string with all humanize helper functions
    """
    return '''# ============================================================
# HUMANIZE - HUMAN-LIKE BEHAVIOR HELPERS
# ============================================================
import random
import time
import math
from typing import Optional, Tuple, List


class Point:
    """2D point for mouse calculations"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


def human_delay(min_ms: float, max_ms: float):
    """
    Random delay with natural distribution

    Args:
        min_ms: Minimum delay in milliseconds
        max_ms: Maximum delay in milliseconds
    """
    if not HUMANIZE_ENABLED:
        return

    # Use triangular distribution for more natural timing
    delay = random.triangular(min_ms, max_ms, (min_ms + max_ms) / 2)
    time.sleep(delay / 1000.0)


def human_type(page, selector: str, text: str, by_role: str = None, name: str = None):
    """
    Human-like text input with realistic timing and typos

    Features:
    - Variable delays between keystrokes (based on TYPING_SPEED)
    - Thinking pauses (~7% chance for 1-3.5 second pause)
    - Typos with backspace correction (based on TYPO_RATE)
    - Extra delay after spaces

    Args:
        page: Playwright page
        selector: CSS selector or None if using by_role
        text: Text to type
        by_role: Playwright role (e.g., "textbox")
        name: Name for role locator
    """
    if not HUMANIZE_ENABLED:
        if by_role:
            page.get_by_role(by_role, name=name).fill(text)
        else:
            page.locator(selector).fill(text)
        return

    # Get element
    if by_role:
        element = page.get_by_role(by_role, name=name).first
    else:
        element = page.locator(selector).first

    # Click and clear
    element.click()
    element.fill('')

    # Pre-typing pause
    human_delay(200, 500)

    # Type character by character
    for i, char in enumerate(text):
        # Check for typo
        if MAKE_TYPOS and random.random() < TYPO_RATE and char.isalpha():
            # Type wrong character
            wrong_chars = 'qwertyuiopasdfghjklzxcvbnm'
            wrong_char = random.choice(wrong_chars)
            element.type(wrong_char)

            # Realize mistake
            human_delay(100, 400)

            # Backspace
            element.press('Backspace')

            # Pause before correct char
            human_delay(50, 150)

        # Type correct character
        element.type(char)

        # Thinking pause (7% chance)
        if random.random() < 0.07:
            delay = random.uniform(1000, 3500)
            time.sleep(delay / 1000.0)
        else:
            # Normal delay based on TYPING_SPEED
            delay = random.triangular(KEYSTROKE_DELAY[0], KEYSTROKE_DELAY[1],
                                     (KEYSTROKE_DELAY[0] + KEYSTROKE_DELAY[1]) / 2)
            time.sleep(delay / 1000.0)

        # Extra delay after space
        if char == ' ':
            human_delay(100, 400)


def _bezier_point(t: float, p0: Point, p1: Point, p2: Point, p3: Point) -> Point:
    """Calculate point on cubic Bezier curve"""
    u = 1 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t

    x = uuu * p0.x + 3 * uu * t * p1.x + 3 * u * tt * p2.x + ttt * p3.x
    y = uuu * p0.y + 3 * uu * t * p1.y + 3 * u * tt * p2.y + ttt * p3.y

    return Point(x, y)


def _wind_mouse_path(start: Point, end: Point,
                     gravity: float = 9.0, wind: float = 3.0,
                     max_step: float = 10.0) -> List[Tuple[Point, float]]:
    """
    Generate mouse path using WindMouse algorithm

    Adds realistic randomness with "wind" forces pushing cursor off course
    and "gravity" pulling it toward target.
    """
    sqrt2 = math.sqrt(2)
    sqrt3 = math.sqrt(3)
    sqrt5 = math.sqrt(5)

    current = Point(start.x, start.y)
    path = [(current, 0)]

    wind_x = 0.0
    wind_y = 0.0
    velocity_x = 0.0
    velocity_y = 0.0

    target_area = 8.0

    while True:
        distance = current.distance_to(end)
        if distance < 1:
            break

        # Decrease forces near target
        if distance < target_area:
            w = wind * (distance / target_area)
            g = gravity * (distance / target_area)
        else:
            w = wind
            g = gravity

        # Random wind
        wind_x = wind_x / sqrt3 + (random.random() * (w * 2 + 1) - w) / sqrt5
        wind_y = wind_y / sqrt3 + (random.random() * (w * 2 + 1) - w) / sqrt5

        # Direction to target
        if distance > 0:
            direction_x = (end.x - current.x) / distance
            direction_y = (end.y - current.y) / distance
        else:
            direction_x, direction_y = 0, 0

        # Apply gravity
        velocity_x += wind_x + g * direction_x
        velocity_y += wind_y + g * direction_y

        # Limit velocity
        velocity_mag = math.sqrt(velocity_x ** 2 + velocity_y ** 2)
        if velocity_mag > max_step:
            scale = max_step / velocity_mag
            velocity_x *= scale
            velocity_y *= scale
            velocity_mag = max_step

        # Reduce near target
        if velocity_mag > distance:
            velocity_x = (end.x - current.x) * 0.9
            velocity_y = (end.y - current.y) * 0.9

        # Move
        current = Point(current.x + velocity_x, current.y + velocity_y)

        # Calculate delay
        delay = 2.0 + 8.0 * (min(velocity_mag, max_step) / max_step)
        path.append((current, delay))

        if len(path) > 2000:
            break

    path.append((end, 2.0))
    return path


def human_move_to(page, selector: str, by_role: str = None, name: str = None):
    """
    Human-like mouse movement using WindMouse algorithm

    Features:
    - Curved trajectory with random variations
    - Variable speed (slower at start/end per Fitts's Law)
    - Micro-jitter during movement
    - Optional overshoot with correction

    Args:
        page: Playwright page
        selector: CSS selector or None if using by_role
        by_role: Playwright role
        name: Name for role locator
    """
    if not HUMANIZE_ENABLED:
        return

    try:
        # Get element
        if by_role:
            element = page.get_by_role(by_role, name=name)
        else:
            element = page.locator(selector)

        box = element.bounding_box()
        if not box:
            return

        # Target with random offset from center
        offset_x = random.gauss(0, 5)
        offset_y = random.gauss(0, 5)
        max_offset = min(box['width'], box['height']) / 2 - 2
        offset_x = max(-max_offset, min(offset_x, max_offset))
        offset_y = max(-max_offset, min(offset_y, max_offset))

        end_x = box['x'] + box['width'] / 2 + offset_x
        end_y = box['y'] + box['height'] / 2 + offset_y

        # Get current position estimate
        try:
            current_pos = page.evaluate('() => ({ x: window.innerWidth / 2, y: window.innerHeight / 2 })')
            start_x = current_pos.get('x', end_x)
            start_y = current_pos.get('y', end_y)
        except:
            start_x, start_y = end_x, end_y

        start = Point(start_x, start_y)
        end = Point(end_x, end_y)

        # Check for overshoot (15% chance)
        if random.random() < 0.15:
            overshoot_dist = random.randint(10, 30)
            direction = random.uniform(0, 2 * math.pi)
            overshoot_target = Point(
                end.x + math.cos(direction) * overshoot_dist,
                end.y + math.sin(direction) * overshoot_dist
            )

            # Move to overshoot
            path = _wind_mouse_path(start, overshoot_target)
            for point, delay in path:
                jitter_x = random.uniform(-1.5, 1.5)
                jitter_y = random.uniform(-1.5, 1.5)
                page.mouse.move(point.x + jitter_x, point.y + jitter_y)
                time.sleep((delay * MOUSE_DELAY / 8) / 1000.0)

            # Pause
            human_delay(50, 150)

            # Correct to target
            path = _wind_mouse_path(overshoot_target, end)
            for point, delay in path:
                page.mouse.move(point.x, point.y)
                time.sleep((delay * MOUSE_DELAY / 8) / 1000.0)
        else:
            # Direct path
            path = _wind_mouse_path(start, end)
            for point, delay in path:
                jitter_x = random.uniform(-1.5, 1.5)
                jitter_y = random.uniform(-1.5, 1.5)
                page.mouse.move(point.x + jitter_x, point.y + jitter_y)
                time.sleep((delay * MOUSE_DELAY / 8) / 1000.0)

    except Exception as e:
        print(f'[HUMANIZE] [ERROR] human_move_to: {e}')


def human_scroll_to(page, selector: str, by_role: str = None, name: str = None):
    """
    Human-like smooth scroll to element

    Features:
    - Smooth acceleration/deceleration
    - Variable step sizes (50-150px)
    - Overshoot with correction (30% chance)
    - Reading pauses during scroll

    Args:
        page: Playwright page
        selector: CSS selector or None if using by_role
        by_role: Playwright role
        name: Name for role locator
    """
    if not HUMANIZE_ENABLED or SCROLL_BEHAVIOR != 'smooth':
        try:
            if by_role:
                element = page.get_by_role(by_role, name=name)
            else:
                element = page.locator(selector)
            element.scroll_into_view_if_needed()
        except:
            pass
        return

    try:
        # Get element
        if by_role:
            element = page.get_by_role(by_role, name=name)
        else:
            element = page.locator(selector)

        box = element.bounding_box()
        if not box:
            element.scroll_into_view_if_needed()
            return

        current_scroll = page.evaluate('window.pageYOffset')
        target_scroll = box['y'] + current_scroll - 200

        # Overshoot (30% chance)
        overshoot = random.random() < 0.3
        if overshoot:
            overshoot_amount = random.uniform(100, 300)
            target_scroll += overshoot_amount

        # Scroll in steps with momentum
        while abs(current_scroll - target_scroll) > 10:
            step = random.uniform(50, 150)
            if current_scroll < target_scroll:
                current_scroll = min(current_scroll + step, target_scroll)
            else:
                current_scroll = max(current_scroll - step, target_scroll)

            page.evaluate(f'window.scrollTo(0, {current_scroll})')
            human_delay(30, 100)

        # Correct overshoot
        if overshoot:
            real_target = box['y'] + page.evaluate('window.pageYOffset') - 200
            current_scroll = page.evaluate('window.pageYOffset')

            while abs(current_scroll - real_target) > 5:
                step = random.uniform(20, 50)
                if current_scroll < real_target:
                    current_scroll = min(current_scroll + step, real_target)
                else:
                    current_scroll = max(current_scroll - step, real_target)

                page.evaluate(f'window.scrollTo(0, {current_scroll})')
                human_delay(30, 80)

        # Final adjustment
        element.scroll_into_view_if_needed()
        human_delay(100, 300)

    except Exception as e:
        print(f'[HUMANIZE] [ERROR] human_scroll_to: {e}')


def human_click(page, selector: str, by_role: str = None, name: str = None):
    """
    Human-like click with mouse movement

    Combines mouse movement with click action:
    1. Move to element with WindMouse
    2. Brief hesitation
    3. Click with realistic timing

    Args:
        page: Playwright page
        selector: CSS selector or None if using by_role
        by_role: Playwright role
        name: Name for role locator
    """
    if not HUMANIZE_ENABLED:
        if by_role:
            page.get_by_role(by_role, name=name).click()
        else:
            page.click(selector)
        return

    try:
        # Move to element
        human_move_to(page, selector, by_role, name)

        # Hesitation before click
        human_delay(100, 400)

        # Click with hold time
        page.mouse.down()
        human_delay(30, 100)
        page.mouse.up()

        # Post-click delay
        human_delay(300, 800)

    except Exception as e:
        print(f'[HUMANIZE] [ERROR] human_click: {e}')
        # Fallback to standard click
        try:
            if by_role:
                page.get_by_role(by_role, name=name).click()
            else:
                page.click(selector)
        except:
            pass


def explore_page(page):
    """
    Simulate natural page exploration

    Mimics how a real user looks at a new page:
    - Initial pause after load
    - Scrolls to see content
    - Hovers over headings
    - Random mouse movements
    - Reading pauses

    Args:
        page: Playwright page
    """
    if not HUMANIZE_ENABLED or not PAGE_EXPLORATION_ENABLED:
        return

    print("[HUMANIZE] Exploring page...")

    # Duration based on intensity
    duration_map = {
        'light': (2, 5),
        'normal': (4, 10),
        'thorough': (8, 18)
    }
    min_dur, max_dur = duration_map.get(EXPLORATION_INTENSITY, (4, 10))
    duration = random.uniform(min_dur, max_dur)

    import time as time_module
    start_time = time_module.time()

    try:
        # Initial pause
        human_delay(800, 2000)

        # Scroll to top
        page.evaluate('window.scrollTo(0, 0)')
        human_delay(300, 700)

        while time_module.time() - start_time < duration:
            action = random.choice(['scroll', 'scroll', 'hover', 'pause', 'mouse'])

            if action == 'scroll':
                scroll_amount = random.randint(150, 400)
                current_scroll = page.evaluate('window.pageYOffset')
                page.evaluate(f'window.scrollTo(0, {current_scroll + scroll_amount})')
                human_delay(300, 800)

            elif action == 'hover':
                # Try to hover over a heading
                try:
                    headings = page.evaluate("""
                        () => {
                            const h = document.querySelectorAll('h1, h2, h3');
                            const v = [];
                            h.forEach((el, i) => {
                                const r = el.getBoundingClientRect();
                                if (r.top > 0 && r.top < window.innerHeight) {
                                    v.push(i);
                                }
                            });
                            return v.slice(0, 3);
                        }
                    """)
                    if headings:
                        idx = random.choice(headings)
                        human_move_to(page, f'h1, h2, h3 >> nth={idx}')
                        human_delay(300, 800)
                except:
                    pass

            elif action == 'pause':
                human_delay(1000, 2500)

            elif action == 'mouse':
                # Random mouse movement
                try:
                    viewport = page.evaluate('() => ({w: window.innerWidth, h: window.innerHeight})')
                    x = random.randint(100, viewport['w'] - 100)
                    y = random.randint(100, viewport['h'] - 100)
                    page.mouse.move(x, y)
                    human_delay(200, 500)
                except:
                    pass

    except Exception as e:
        print(f'[HUMANIZE] [WARN] explore_page: {e}')

    print("[HUMANIZE] Page exploration complete")
'''


def get_full_humanize_code(config: Dict[str, Any]) -> str:
    """
    Get complete humanize code block for injection into generated scripts

    Args:
        config: Humanize configuration dictionary

    Returns:
        Complete Python code string with config and helpers
    """
    config_code = generate_humanize_config_code(config)
    helpers_code = generate_humanize_helpers_code()
    return config_code + "\n" + helpers_code


# Default config for testing
DEFAULT_HUMANIZE_CONFIG = {
    'enabled': True,
    'typing_speed': 'normal',
    'mouse_speed': 'normal',
    'scroll_behavior': 'smooth',
    'make_typos': True,
    'typo_rate': 0.05,
    'page_exploration_enabled': True,
    'exploration_intensity': 'normal'
}
