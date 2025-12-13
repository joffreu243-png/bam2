"""
Human Behavior Coordinator Module

Main class that coordinates all human-like behavior components:
- Mouse movements
- Keyboard input
- Scrolling
- Timing
- Page exploration

This is the main entry point for human-like automation.
"""

import random
import asyncio
from typing import Optional, Any, List

from .config import HumanizeConfig, HumanizeLevel, ExplorationConfig
from .mouse import HumanMouse
from .keyboard import HumanKeyboard
from .scroll import HumanScroll
from .timing import HumanTiming


class HumanBehavior:
    """
    Main coordinator class for human-like browser automation

    Combines all humanize modules into a unified interface.
    Drop-in replacement for standard Playwright actions with
    automatic human-like behavior.

    Usage:
        config = HumanizeConfig.from_level(HumanizeLevel.MODERATE)
        human = HumanBehavior(page, config)

        # Click with mouse movement
        await human.click("#button")

        # Type with realistic delays and typos
        await human.type("#input", "Hello World!")

        # Scroll to element
        await human.scroll_to("#section")

        # Explore page naturally
        await human.explore_page()
    """

    def __init__(self, page: Any, config: Optional[HumanizeConfig] = None):
        """
        Initialize HumanBehavior coordinator

        Args:
            page: Playwright page object
            config: HumanizeConfig instance (defaults to MODERATE)
        """
        self.page = page
        self.config = config or HumanizeConfig.from_level(HumanizeLevel.MODERATE)

        # Initialize sub-modules
        self.mouse = HumanMouse(page, self.config)
        self.keyboard = HumanKeyboard(page, self.config)
        self.scroll = HumanScroll(page, self.config)
        self.timing = HumanTiming(self.config)

    async def click(
        self,
        selector: Optional[str] = None,
        by_role: Optional[str] = None,
        name: Optional[str] = None,
        button: str = "left"
    ) -> bool:
        """
        Human-like click on element

        1. Moves mouse to element via curved path
        2. Brief hesitation before clicking
        3. Realistic mousedown/mouseup timing
        4. Action delay after click

        Args:
            selector: CSS selector
            by_role: Playwright role (e.g., "button", "textbox")
            name: Name for role locator
            button: Mouse button ("left", "right", "middle")

        Returns:
            True if successful
        """
        result = await self.mouse.click(selector, by_role, name, button)

        if result and self.config.enabled:
            await self.timing.delay(self.timing.action_delay())

        return result

    async def double_click(
        self,
        selector: Optional[str] = None,
        by_role: Optional[str] = None,
        name: Optional[str] = None
    ) -> bool:
        """Human-like double-click"""
        result = await self.mouse.double_click(selector, by_role, name)

        if result and self.config.enabled:
            await self.timing.delay(self.timing.action_delay())

        return result

    async def type(
        self,
        selector: Optional[str] = None,
        text: str = "",
        by_role: Optional[str] = None,
        name: Optional[str] = None,
        click_first: bool = True,
        clear_first: bool = True
    ) -> bool:
        """
        Human-like text input

        1. Optionally clicks element first
        2. Clears existing content
        3. Types with variable delays and occasional typos
        4. Thinking pauses during typing
        5. Action delay after typing

        Args:
            selector: CSS selector
            text: Text to type
            by_role: Playwright role
            name: Name for role locator
            click_first: Click element before typing
            clear_first: Clear existing content

        Returns:
            True if successful
        """
        if click_first:
            await self.mouse.move_to(selector, by_role, name)
            await self.timing.delay(self.timing.click_hesitation())

        result = await self.keyboard.type_text(
            selector, text, by_role, name, clear_first
        )

        if result and self.config.enabled:
            await self.timing.delay(self.timing.action_delay())

        return result

    async def fill(
        self,
        selector: Optional[str] = None,
        text: str = "",
        by_role: Optional[str] = None,
        name: Optional[str] = None
    ) -> bool:
        """
        Alias for type() for Playwright compatibility

        Uses human-like typing instead of instant fill.
        """
        return await self.type(selector, text, by_role, name)

    async def scroll_to(
        self,
        selector: Optional[str] = None,
        by_role: Optional[str] = None,
        name: Optional[str] = None
    ) -> bool:
        """
        Human-like scroll to element

        1. Smooth scroll with momentum
        2. Optional overshoot with correction
        3. Reading pauses during scroll

        Args:
            selector: CSS selector
            by_role: Playwright role
            name: Name for role locator

        Returns:
            True if successful
        """
        return await self.scroll.scroll_to_element(selector, by_role, name)

    async def scroll_page(
        self,
        direction: str = 'down',
        amount: Optional[int] = None
    ) -> bool:
        """Scroll page by specified amount"""
        return await self.scroll.scroll_page(direction, amount)

    async def hover(
        self,
        selector: Optional[str] = None,
        by_role: Optional[str] = None,
        name: Optional[str] = None,
        duration_ms: tuple = (500, 1500)
    ) -> bool:
        """Hover over element for specified duration"""
        return await self.mouse.hover(selector, by_role, name, duration_ms)

    async def wait_like_human(self, reason: str = "thinking"):
        """
        Natural pause for various reasons

        Args:
            reason: Type of pause
                - "thinking": Long pause (2-5 seconds)
                - "reading": Medium pause (1-3 seconds)
                - "action": Standard pause (300-1500ms)
                - "micro": Short pause (50-200ms)
        """
        if not self.config.enabled:
            return

        delays = {
            "thinking": self.timing.thinking_delay(),
            "reading": self.timing.page_load_delay(),
            "action": self.timing.action_delay(),
            "micro": self.timing.micro_delay()
        }

        delay_ms = delays.get(reason, delays["action"])
        await self.timing.delay(delay_ms)

    async def explore_page(self, duration_seconds: Optional[float] = None):
        """
        Simulate natural page exploration

        Mimics how a real user explores a new page:
        - Scrolls to see content
        - Hovers over headings
        - Random mouse movements
        - Reading pauses

        Args:
            duration_seconds: Exploration duration (None = auto from config)
        """
        if not self.config.enabled or not self.config.exploration.enabled:
            return

        exploration_config = self.config.exploration

        if duration_seconds is None:
            min_dur, max_dur = exploration_config.duration
            duration_seconds = random.uniform(min_dur, max_dur)

        print(f"[HUMANIZE] Exploring page for ~{duration_seconds:.1f}s...")

        import time
        start_time = time.time()

        # Initial pause (looking at what loaded)
        await self.timing.delay(self.timing.page_load_delay())

        # Scroll to top
        await self.scroll.scroll_to_top()
        await self.timing.delay(self.timing.micro_delay())

        while time.time() - start_time < duration_seconds:
            action = random.choice([
                'scroll_down',
                'scroll_down',  # Weight scroll more heavily
                'hover_heading',
                'random_mouse',
                'pause',
                'scroll_up'
            ])

            if action == 'scroll_down':
                # Scroll down a bit
                scroll_amount = random.randint(150, 400)
                await self.scroll.scroll_page('down', amount=scroll_amount)
                await self.timing.delay(random.randint(300, 800))

            elif action == 'scroll_up':
                # Sometimes scroll back up
                scroll_amount = random.randint(50, 200)
                await self.scroll.scroll_page('up', amount=scroll_amount)
                await self.timing.delay(random.randint(200, 500))

            elif action == 'hover_heading':
                # Try to hover over a heading
                await self._hover_random_heading()

            elif action == 'random_mouse':
                # Random mouse movement
                await self.mouse.random_movement()
                await self.timing.delay(random.randint(200, 600))

            elif action == 'pause':
                # Reading pause
                await self.timing.delay(self.timing.reading_pause())

        print("[HUMANIZE] Page exploration complete")

    async def _hover_random_heading(self):
        """Attempt to hover over a random heading on the page"""
        try:
            # Find visible headings
            headings = await self.page.evaluate('''
                () => {
                    const headings = document.querySelectorAll('h1, h2, h3');
                    const visible = [];
                    headings.forEach((h, i) => {
                        const rect = h.getBoundingClientRect();
                        if (rect.top > 0 && rect.top < window.innerHeight) {
                            visible.push({
                                index: i,
                                text: h.textContent.substring(0, 50)
                            });
                        }
                    });
                    return visible.slice(0, 5);
                }
            ''')

            if headings:
                heading = random.choice(headings)
                heading_selector = f'h1, h2, h3 >> nth={heading["index"]}'

                await self.hover(heading_selector, duration_ms=(300, 800))

        except Exception:
            pass

    async def browse_naturally(self, duration_seconds: float = 30):
        """
        Extended natural browsing simulation

        More comprehensive than explore_page:
        - Longer duration
        - More varied interactions
        - Simulates real browsing session

        Args:
            duration_seconds: Total browsing duration
        """
        if not self.config.enabled:
            return

        import time
        start_time = time.time()
        actions_performed = 0

        print(f"[HUMANIZE] Natural browsing for {duration_seconds}s...")

        while time.time() - start_time < duration_seconds:
            # Vary action frequency
            wait_time = random.randint(1000, 3000)
            await self.timing.delay(wait_time)

            # Choose action based on weighted random
            action = random.choices(
                ['scroll', 'mouse', 'hover_link', 'pause', 'scroll_back'],
                weights=[35, 25, 15, 15, 10],
                k=1
            )[0]

            if action == 'scroll':
                amount = random.randint(200, 600)
                await self.scroll.scroll_page('down', amount=amount)

            elif action == 'mouse':
                await self.mouse.random_movement()

            elif action == 'hover_link':
                await self._hover_random_link()

            elif action == 'pause':
                await self.timing.delay(self.timing.thinking_delay())

            elif action == 'scroll_back':
                amount = random.randint(100, 300)
                await self.scroll.scroll_page('up', amount=amount)

            actions_performed += 1

            # Check if at bottom
            try:
                at_bottom = await self.page.evaluate('''
                    () => (window.innerHeight + window.pageYOffset) >=
                          document.documentElement.scrollHeight - 100
                ''')
                if at_bottom and random.random() < 0.3:
                    # Sometimes scroll back to top
                    await self.scroll.scroll_to_top()
            except:
                pass

        print(f"[HUMANIZE] Natural browsing complete ({actions_performed} actions)")

    async def _hover_random_link(self):
        """Hover over a random visible link"""
        try:
            links = await self.page.evaluate('''
                () => {
                    const links = document.querySelectorAll('a[href]');
                    const visible = [];
                    links.forEach((a, i) => {
                        const rect = a.getBoundingClientRect();
                        if (rect.top > 50 && rect.top < window.innerHeight - 50 &&
                            rect.width > 10 && rect.height > 10) {
                            visible.push(i);
                        }
                    });
                    return visible.slice(0, 10);
                }
            ''')

            if links:
                link_index = random.choice(links)
                link_selector = f'a[href] >> nth={link_index}'
                await self.hover(link_selector, duration_ms=(200, 600))

        except Exception:
            pass

    async def goto_with_exploration(self, url: str):
        """
        Navigate to URL and explore the page

        Combines navigation with natural page exploration.
        """
        await self.page.goto(url)
        await self.timing.delay(self.timing.page_load_delay())
        await self.explore_page()

    async def submit_form(
        self,
        submit_selector: str = 'button[type="submit"]',
        fields: Optional[dict] = None
    ):
        """
        Fill and submit a form with human-like behavior

        Args:
            submit_selector: CSS selector for submit button
            fields: Dictionary of {selector: value} for form fields
        """
        # Fill fields if provided
        if fields:
            for selector, value in fields.items():
                await self.type(selector, str(value))
                await self.timing.delay(self.timing.action_delay())

        # Click submit
        await self.click(submit_selector)


# Convenience function for quick initialization
def create_human_behavior(
    page: Any,
    level: HumanizeLevel = HumanizeLevel.MODERATE
) -> HumanBehavior:
    """
    Create HumanBehavior instance with specified level

    Args:
        page: Playwright page object
        level: Humanize level preset

    Returns:
        Configured HumanBehavior instance
    """
    config = HumanizeConfig.from_level(level)
    return HumanBehavior(page, config)


def create_human_behavior_from_dict(page: Any, config_dict: dict) -> HumanBehavior:
    """
    Create HumanBehavior from dictionary config

    Compatible with GUI settings format.

    Args:
        page: Playwright page object
        config_dict: Configuration dictionary

    Returns:
        Configured HumanBehavior instance
    """
    config = HumanizeConfig.from_dict(config_dict)
    return HumanBehavior(page, config)
