"""
Human-Like Timing Module

Provides realistic timing and delay functions with various probability distributions.
All times are in milliseconds unless otherwise noted.
"""

import random
import time
import math
from typing import Tuple, Optional, Callable

from .config import HumanizeConfig, TimingConfig


class HumanTiming:
    """
    Provides realistic timing delays for human-like automation

    Features:
    - Multiple probability distributions (uniform, gaussian, triangular)
    - Configurable variance for all delays
    - Speed multiplier support
    - Time-of-day fatigue simulation (optional)

    Usage:
        timing = HumanTiming(config)
        await timing.delay(timing.action_delay())
        await timing.delay(timing.random_delay(500, 1500))
    """

    def __init__(self, config: HumanizeConfig):
        self.config = config
        self.timing_config: TimingConfig = config.timing
        self._last_action_time: float = 0

    def _apply_variance(self, base_ms: int, variance: Optional[float] = None) -> int:
        """
        Apply random variance to a base delay value

        Uses a gaussian distribution for more natural timing.
        """
        if variance is None:
            variance = self.timing_config.variance_factor

        if variance <= 0:
            return base_ms

        # Gaussian variance around the base value
        std_dev = base_ms * variance
        result = random.gauss(base_ms, std_dev)

        # Clamp to reasonable bounds (50% - 200% of base)
        return max(int(base_ms * 0.5), min(int(result), int(base_ms * 2.0)))

    def random_delay(
        self,
        min_ms: int,
        max_ms: int,
        distribution: str = "triangular"
    ) -> int:
        """
        Generate a random delay with specified distribution

        Args:
            min_ms: Minimum delay in milliseconds
            max_ms: Maximum delay in milliseconds
            distribution: Type of distribution
                - "uniform": Equal probability across range
                - "gaussian": Normal distribution (peak in middle)
                - "triangular": Triangular distribution (peak in middle)
                - "exponential": Exponential distribution (more short delays)

        Returns:
            Delay in milliseconds
        """
        if min_ms >= max_ms:
            return min_ms

        if distribution == "uniform":
            return random.randint(min_ms, max_ms)

        elif distribution == "gaussian":
            # Mean at center, std dev covers ~95% of range
            mean = (min_ms + max_ms) / 2
            std_dev = (max_ms - min_ms) / 4
            result = random.gauss(mean, std_dev)
            return max(min_ms, min(int(result), max_ms))

        elif distribution == "triangular":
            # Peak slightly past center (more realistic)
            mode = min_ms + (max_ms - min_ms) * 0.55
            return int(random.triangular(min_ms, max_ms, mode))

        elif distribution == "exponential":
            # More short delays, fewer long ones
            # Lambda controls the rate (higher = shorter average)
            lam = 2.0 / (max_ms - min_ms)
            result = min_ms + random.expovariate(lam)
            return max(min_ms, min(int(result), max_ms))

        else:
            return random.randint(min_ms, max_ms)

    def action_delay(self) -> int:
        """
        Get delay for between major actions (clicks, typing sequences, etc.)

        This is the main "breathing room" delay between distinct actions.
        """
        if not self.config.enabled:
            return 0

        min_ms, max_ms = self.timing_config.action_delay
        base = self.random_delay(min_ms, max_ms, "triangular")
        return self._apply_variance(base)

    def page_load_delay(self) -> int:
        """
        Get delay after page loads

        Simulates time spent observing that the page has loaded.
        """
        if not self.config.enabled:
            return 0

        min_ms, max_ms = self.timing_config.page_load_delay
        return self.random_delay(min_ms, max_ms, "triangular")

    def thinking_delay(self) -> int:
        """
        Get a longer "thinking" delay

        Simulates decision-making or reading.
        """
        if not self.config.enabled:
            return 0

        min_ms, max_ms = self.timing_config.thinking_delay
        return self.random_delay(min_ms, max_ms, "gaussian")

    def micro_delay(self) -> int:
        """
        Get a very short delay between related actions

        Used for sub-actions that should happen quickly but not instantly.
        """
        if not self.config.enabled:
            return 0

        min_ms, max_ms = self.timing_config.micro_delay
        return self.random_delay(min_ms, max_ms, "uniform")

    def click_hesitation(self) -> int:
        """
        Get delay before clicking (simulates aiming/decision)

        Models the brief hesitation before committing to a click.
        """
        if not self.config.enabled:
            return 0

        min_ms, max_ms = self.timing_config.click_hesitation
        return self.random_delay(min_ms, max_ms, "exponential")

    def pre_type_delay(self) -> int:
        """
        Get delay before starting to type

        Simulates focusing on the input field before typing.
        """
        if not self.config.enabled:
            return 0

        min_ms, max_ms = self.timing_config.pre_type_delay
        return self.random_delay(min_ms, max_ms, "triangular")

    def keystroke_delay(self) -> int:
        """Get delay between keystrokes during typing"""
        if not self.config.enabled or not self.config.keyboard.enabled:
            return 0

        min_ms, max_ms = self.config.keyboard.keystroke_delay
        base = self.random_delay(min_ms, max_ms, "triangular")

        # Apply speed multiplier
        speed = self.config.keyboard.speed
        if speed > 0:
            base = int(base / speed)

        return base

    def complex_char_delay(self) -> int:
        """Get delay for complex characters that require more effort"""
        if not self.config.enabled or not self.config.keyboard.enabled:
            return 0

        min_ms, max_ms = self.config.keyboard.complex_char_delay
        return self.random_delay(min_ms, max_ms, "gaussian")

    def mouse_step_delay(self) -> int:
        """Get delay between mouse movement steps"""
        if not self.config.enabled or not self.config.mouse.enabled:
            return 0

        min_ms, max_ms = self.config.mouse.move_step_delay
        base = self.random_delay(min_ms, max_ms, "uniform")

        # Apply speed multiplier
        speed = self.config.mouse.speed
        if speed > 0:
            base = int(base / speed)

        return base

    def scroll_step_delay(self) -> int:
        """Get delay between scroll steps"""
        if not self.config.enabled or not self.config.scroll.enabled:
            return 0

        min_ms, max_ms = self.config.scroll.step_delay
        base = self.random_delay(min_ms, max_ms, "uniform")

        # Apply speed multiplier
        speed = self.config.scroll.speed
        if speed > 0:
            base = int(base / speed)

        return base

    def reading_pause(self) -> int:
        """Get delay for reading pause during scrolling"""
        if not self.config.enabled or not self.config.scroll.enabled:
            return 0

        min_ms, max_ms = self.config.scroll.reading_pause_duration
        return self.random_delay(min_ms, max_ms, "gaussian")

    def should_thinking_pause(self) -> bool:
        """Check if a thinking pause should occur (probability-based)"""
        if not self.config.enabled or not self.config.keyboard.enabled:
            return False
        return random.random() < self.config.keyboard.thinking_pause_chance

    def should_reading_pause(self) -> bool:
        """Check if a reading pause should occur during scroll"""
        if not self.config.enabled or not self.config.scroll.enabled:
            return False
        return random.random() < self.config.scroll.reading_pause_chance

    def should_typo(self) -> bool:
        """Check if a typo should occur (probability-based)"""
        if not self.config.enabled or not self.config.keyboard.enabled:
            return False
        return random.random() < self.config.keyboard.typo_chance

    def should_overshoot_mouse(self) -> bool:
        """Check if mouse should overshoot target"""
        if not self.config.enabled or not self.config.mouse.enabled:
            return False
        return random.random() < self.config.mouse.overshoot_chance

    def should_overshoot_scroll(self) -> bool:
        """Check if scroll should overshoot target"""
        if not self.config.enabled or not self.config.scroll.enabled:
            return False
        return random.random() < self.config.scroll.overshoot_chance

    async def delay(self, ms: int):
        """
        Execute an async delay

        Args:
            ms: Delay in milliseconds
        """
        if ms <= 0:
            return

        import asyncio
        await asyncio.sleep(ms / 1000.0)

    def delay_sync(self, ms: int):
        """
        Execute a synchronous delay

        Args:
            ms: Delay in milliseconds
        """
        if ms <= 0:
            return
        time.sleep(ms / 1000.0)

    def get_typing_thinking_pause(self) -> int:
        """Get duration for typing thinking pause"""
        if not self.config.enabled or not self.config.keyboard.enabled:
            return 0

        min_ms, max_ms = self.config.keyboard.thinking_pause_duration
        return self.random_delay(min_ms, max_ms, "gaussian")

    def get_typo_realize_delay(self) -> int:
        """Get delay for realizing a typo was made"""
        if not self.config.enabled or not self.config.keyboard.enabled:
            return 0

        min_ms, max_ms = self.config.keyboard.typo_realize_delay
        return self.random_delay(min_ms, max_ms, "triangular")

    def get_typo_correct_delay(self) -> int:
        """Get delay before typing correct character after backspace"""
        if not self.config.enabled or not self.config.keyboard.enabled:
            return 0

        min_ms, max_ms = self.config.keyboard.typo_correct_delay
        return self.random_delay(min_ms, max_ms, "uniform")

    def get_space_delay(self) -> int:
        """Get extra delay after typing a space"""
        if not self.config.enabled or not self.config.keyboard.enabled:
            return 0

        min_ms, max_ms = self.config.keyboard.space_delay
        return self.random_delay(min_ms, max_ms, "triangular")

    def get_key_hold_time(self) -> int:
        """Get duration to hold a key before releasing"""
        if not self.config.enabled or not self.config.keyboard.enabled:
            return 50  # Default minimal hold time

        min_ms, max_ms = self.config.keyboard.key_hold_time
        return self.random_delay(min_ms, max_ms, "uniform")


def human_delay_sync(min_ms: float, max_ms: float, enabled: bool = True):
    """
    Standalone synchronous delay function (backward compatible)

    For use in generated scripts without full HumanTiming class.
    """
    if not enabled:
        return

    delay_seconds = random.uniform(min_ms, max_ms) / 1000.0
    time.sleep(delay_seconds)


async def human_delay_async(min_ms: float, max_ms: float, enabled: bool = True):
    """
    Standalone async delay function

    For use in async generated scripts.
    """
    if not enabled:
        return

    import asyncio
    delay_seconds = random.uniform(min_ms, max_ms) / 1000.0
    await asyncio.sleep(delay_seconds)
