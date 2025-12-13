"""
Human-Like Scroll Module

Implements realistic scrolling behavior including:
- Smooth momentum-based scrolling
- Natural overshoot with correction
- Reading pauses
- Variable scroll speed
"""

import random
import math
from typing import Optional, Any, Tuple

from .config import HumanizeConfig, ScrollConfig
from .timing import HumanTiming


class ScrollPhysics:
    """
    Physics-based scroll simulation

    Models realistic scroll behavior with:
    - Momentum (inertia after releasing)
    - Friction (gradual slowdown)
    - Variable acceleration
    """

    @staticmethod
    def calculate_momentum_steps(
        distance: float,
        initial_velocity: float = 50,
        friction: float = 0.85,
        min_velocity: float = 2
    ) -> list:
        """
        Calculate scroll steps with momentum decay

        Args:
            distance: Total distance to scroll
            initial_velocity: Starting velocity (pixels per step)
            friction: Decay factor (0-1, higher = longer momentum)
            min_velocity: Minimum velocity before stopping

        Returns:
            List of (step_distance, delay_ms) tuples
        """
        steps = []
        remaining = abs(distance)
        direction = 1 if distance > 0 else -1
        velocity = initial_velocity

        while remaining > 0 and velocity > min_velocity:
            step = min(velocity, remaining)
            steps.append((step * direction, 30 + random.randint(0, 20)))
            remaining -= step
            velocity *= friction

        # Final step to reach exact target
        if remaining > 0:
            steps.append((remaining * direction, 50))

        return steps


class HumanScroll:
    """
    Human-like scrolling implementation

    Features:
    - Smooth acceleration/deceleration
    - Momentum effect (coasting after scroll gesture)
    - Overshoot with natural correction
    - Reading pauses during scroll
    - Variable step sizes

    Usage:
        scroll = HumanScroll(page, config)
        await scroll.scroll_to_element("#target")
        await scroll.scroll_page("down", amount=500)
    """

    def __init__(self, page: Any, config: HumanizeConfig):
        """
        Initialize HumanScroll

        Args:
            page: Playwright page object
            config: HumanizeConfig instance
        """
        self.page = page
        self.config = config
        self.scroll_config: ScrollConfig = config.scroll
        self.timing = HumanTiming(config)
        self.physics = ScrollPhysics()

    async def _get_current_scroll(self) -> float:
        """Get current scroll position"""
        try:
            return await self.page.evaluate('window.pageYOffset || document.documentElement.scrollTop')
        except:
            return 0

    async def _get_page_height(self) -> float:
        """Get total scrollable page height"""
        try:
            return await self.page.evaluate(
                'Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)'
            )
        except:
            return 1000

    async def _get_viewport_height(self) -> float:
        """Get viewport height"""
        try:
            return await self.page.evaluate('window.innerHeight')
        except:
            return 800

    async def _execute_scroll(self, target_y: float, smooth: bool = True):
        """
        Execute scroll to target Y position

        Args:
            target_y: Target scroll position
            smooth: Use smooth scrolling with momentum
        """
        current_y = await self._get_current_scroll()
        distance = target_y - current_y

        if abs(distance) < 5:
            return

        if not smooth or not self.scroll_config.momentum_enabled:
            # Simple scroll
            await self.page.evaluate(f'window.scrollTo(0, {target_y})')
            return

        # Momentum-based scrolling
        steps = self.physics.calculate_momentum_steps(
            distance,
            initial_velocity=random.randint(*self.scroll_config.step_size),
            friction=self.scroll_config.momentum_decay
        )

        pos = current_y
        for step_distance, delay in steps:
            pos += step_distance

            # Add jitter
            jitter = random.randint(-self.scroll_config.jitter, self.scroll_config.jitter)
            scroll_pos = pos + jitter

            await self.page.evaluate(f'window.scrollTo(0, {scroll_pos})')
            await self.timing.delay(delay)

            # Occasional reading pause
            if self.timing.should_reading_pause():
                await self.timing.delay(self.timing.reading_pause())

        # Ensure we're at exact target
        await self.page.evaluate(f'window.scrollTo(0, {target_y})')

    async def scroll_to_element(
        self,
        selector: Optional[str] = None,
        by_role: Optional[str] = None,
        name: Optional[str] = None,
        offset: int = 200
    ) -> bool:
        """
        Scroll to bring element into view

        Features:
        - Smooth acceleration/deceleration
        - Overshoot with correction (30% chance)
        - Reading pauses
        - Scrolls element to upper portion of viewport

        Args:
            selector: CSS selector
            by_role: Playwright role locator
            name: Name for role locator
            offset: Pixels above element to scroll to

        Returns:
            True if successful
        """
        if not self.config.enabled or not self.scroll_config.enabled:
            # Fall back to standard scroll
            try:
                if by_role and name:
                    await self.page.get_by_role(by_role, name=name).scroll_into_view_if_needed()
                elif selector:
                    await self.page.locator(selector).scroll_into_view_if_needed()
                return True
            except:
                return False

        try:
            # Get element position
            if by_role and name:
                element = self.page.get_by_role(by_role, name=name)
            elif selector:
                element = self.page.locator(selector)
            else:
                return False

            box = await element.bounding_box()
            if not box:
                # Element not visible, try standard scroll
                await element.scroll_into_view_if_needed()
                return True

            current_scroll = await self._get_current_scroll()
            target_scroll = box['y'] + current_scroll - offset

            # Check for overshoot
            if self.timing.should_overshoot_scroll():
                # Overshoot amount
                overshoot_dist = random.randint(*self.scroll_config.overshoot_distance)
                overshoot_direction = 1 if random.random() > 0.5 else -1
                overshoot_target = target_scroll + (overshoot_dist * overshoot_direction)

                # Scroll to overshoot
                await self._execute_scroll(overshoot_target)

                # Pause (realizing overshoot)
                await self.timing.delay(self.timing.micro_delay())

                # Correct with slower, smaller steps
                await self._execute_scroll(target_scroll)
            else:
                await self._execute_scroll(target_scroll)

            # Final adjustment using browser's native scroll
            await element.scroll_into_view_if_needed()
            await self.timing.delay(self.timing.micro_delay())

            return True

        except Exception as e:
            print(f'[HUMANIZE] [ERROR] scroll_to_element: {e}')
            return False

    async def scroll_page(
        self,
        direction: str = 'down',
        amount: Optional[int] = None,
        viewport_percent: Optional[float] = None
    ) -> bool:
        """
        Scroll page by specified amount

        Args:
            direction: 'up' or 'down'
            amount: Scroll distance in pixels (overrides viewport_percent)
            viewport_percent: Scroll by percentage of viewport (0.0-1.0)

        Returns:
            True if successful
        """
        if not self.config.enabled or not self.scroll_config.enabled:
            try:
                viewport_height = await self._get_viewport_height()
                scroll_amount = amount or int(viewport_height * (viewport_percent or 0.8))
                if direction == 'up':
                    scroll_amount = -scroll_amount
                await self.page.evaluate(f'window.scrollBy(0, {scroll_amount})')
                return True
            except:
                return False

        try:
            current_scroll = await self._get_current_scroll()
            viewport_height = await self._get_viewport_height()

            # Calculate scroll amount
            if amount:
                scroll_distance = amount
            elif viewport_percent:
                scroll_distance = int(viewport_height * viewport_percent)
            else:
                # Default: scroll about 80% of viewport
                scroll_distance = int(viewport_height * 0.8)

            # Add jitter to amount
            jitter = random.randint(-self.scroll_config.jitter, self.scroll_config.jitter)
            scroll_distance += jitter

            if direction == 'up':
                scroll_distance = -scroll_distance

            target_scroll = current_scroll + scroll_distance

            # Clamp to valid range
            page_height = await self._get_page_height()
            target_scroll = max(0, min(target_scroll, page_height - viewport_height))

            await self._execute_scroll(target_scroll)

            return True

        except Exception as e:
            print(f'[HUMANIZE] [ERROR] scroll_page: {e}')
            return False

    async def read_scroll(
        self,
        duration_seconds: float = 10,
        direction: str = 'down'
    ):
        """
        Simulate reading/browsing behavior

        Scrolls slowly with frequent pauses, simulating someone
        reading content on the page.

        Args:
            duration_seconds: Total duration of reading behavior
            direction: Primary scroll direction
        """
        if not self.config.enabled or not self.scroll_config.enabled:
            return

        import time
        start_time = time.time()
        viewport_height = await self._get_viewport_height()

        while time.time() - start_time < duration_seconds:
            # Scroll a small amount
            scroll_amount = random.randint(100, 300)
            await self.scroll_page(direction, amount=scroll_amount)

            # Reading pause
            pause_duration = random.randint(1000, 3000)
            await self.timing.delay(pause_duration)

            # Occasionally scroll back up a bit
            if random.random() < 0.2:
                back_amount = random.randint(50, 150)
                await self.scroll_page('up', amount=back_amount)
                await self.timing.delay(random.randint(500, 1500))

            # Check if we've reached the end
            current = await self._get_current_scroll()
            page_height = await self._get_page_height()
            if current >= page_height - viewport_height - 50:
                break

    async def scroll_to_top(self) -> bool:
        """Scroll to top of page with human-like behavior"""
        if not self.config.enabled or not self.scroll_config.enabled:
            await self.page.evaluate('window.scrollTo(0, 0)')
            return True

        try:
            await self._execute_scroll(0)
            return True
        except Exception as e:
            print(f'[HUMANIZE] [ERROR] scroll_to_top: {e}')
            return False

    async def scroll_to_bottom(self) -> bool:
        """Scroll to bottom of page with human-like behavior"""
        try:
            page_height = await self._get_page_height()
            viewport_height = await self._get_viewport_height()
            target = page_height - viewport_height

            if not self.config.enabled or not self.scroll_config.enabled:
                await self.page.evaluate(f'window.scrollTo(0, {target})')
                return True

            await self._execute_scroll(target)
            return True

        except Exception as e:
            print(f'[HUMANIZE] [ERROR] scroll_to_bottom: {e}')
            return False

    async def wheel_scroll(
        self,
        delta_y: int = 100,
        x: Optional[int] = None,
        y: Optional[int] = None
    ):
        """
        Perform mouse wheel scroll at position

        More realistic than programmatic scrolling for some scenarios.

        Args:
            delta_y: Scroll amount (positive = down)
            x: X position for scroll (None = center)
            y: Y position for scroll (None = center)
        """
        try:
            if x is None or y is None:
                viewport = await self.page.evaluate('''
                    () => ({
                        width: window.innerWidth,
                        height: window.innerHeight
                    })
                ''')
                x = x or viewport['width'] // 2
                y = y or viewport['height'] // 2

            await self.page.mouse.wheel(0, delta_y)

        except Exception as e:
            print(f'[HUMANIZE] [WARN] wheel_scroll: {e}')
