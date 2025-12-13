"""
Human-Like Keyboard Module

Implements realistic typing patterns including:
- Variable keystroke timing
- Natural typo generation with correction
- Thinking pauses
- Speed variation for different character types
"""

import random
import string
from typing import Optional, Any, List, Tuple

from .config import HumanizeConfig, KeyboardConfig
from .timing import HumanTiming


# Character categories for variable typing speed
COMPLEX_CHARS = set('@#$%^&*()_+-={}[]|\\:";\'<>,.?/~`')
NUMBER_CHARS = set('0123456789')
UPPERCASE_CHARS = set(string.ascii_uppercase)
SPECIAL_KEYS = {'Shift', 'Control', 'Alt', 'Meta', 'Enter', 'Tab', 'Backspace', 'Delete', 'Escape'}

# Keyboard layout for realistic typo generation (QWERTY)
QWERTY_NEIGHBORS = {
    'q': 'wa12', 'w': 'qeas23', 'e': 'wdrs34', 'r': 'etfs45', 't': 'rygd56',
    'y': 'tuhf67', 'u': 'yijg78', 'i': 'uokh89', 'o': 'iplj90', 'p': 'ol0-[',
    'a': 'qwsz', 's': 'awedxz', 'd': 'swerfxc', 'f': 'dertgcv', 'g': 'frtyhvb',
    'h': 'gtyujbn', 'j': 'hyuiknm', 'k': 'juiolm,', 'l': 'kiop;.,',
    'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn',
    'n': 'bhjm', 'm': 'njk,',
    '1': '2q`', '2': '13qw', '3': '24we', '4': '35er', '5': '46rt',
    '6': '57ty', '7': '68yu', '8': '79ui', '9': '80io', '0': '9-op',
    ' ': ' ', '.': ',l;/', ',': 'mkl.', '/': '.;\''
}

# Common typo patterns (missing or doubled letters)
COMMON_TYPO_PATTERNS = [
    'double_letter',      # 'hello' -> 'helllo'
    'missing_letter',     # 'hello' -> 'helo'
    'adjacent_key',       # 'hello' -> 'hwllo'
    'transposition',      # 'hello' -> 'hlelo'
    'extra_letter',       # 'hello' -> 'hekllo'
]


class TypoGenerator:
    """Generates realistic typos based on keyboard layout and common patterns"""

    @staticmethod
    def get_adjacent_key(char: str) -> str:
        """Get a random adjacent key on QWERTY keyboard"""
        char_lower = char.lower()
        if char_lower in QWERTY_NEIGHBORS:
            neighbors = QWERTY_NEIGHBORS[char_lower]
            wrong_char = random.choice(neighbors)
            # Preserve case
            if char.isupper():
                wrong_char = wrong_char.upper()
            return wrong_char
        # Fallback to random lowercase letter
        return random.choice(string.ascii_lowercase)

    @staticmethod
    def generate_typo(text: str, position: int) -> Tuple[str, str]:
        """
        Generate a typo at given position

        Returns:
            Tuple of (typo_type, wrong_character)
        """
        if position >= len(text):
            return ('adjacent_key', TypoGenerator.get_adjacent_key('a'))

        current_char = text[position]

        # Select typo type based on context and randomness
        typo_type = random.choice(COMMON_TYPO_PATTERNS)

        if typo_type == 'double_letter':
            # Double the current character
            return ('double', current_char)

        elif typo_type == 'missing_letter':
            # Will skip typing this character (handled in keyboard)
            return ('skip', '')

        elif typo_type == 'adjacent_key':
            wrong = TypoGenerator.get_adjacent_key(current_char)
            return ('adjacent', wrong)

        elif typo_type == 'transposition':
            # Will be handled by typing next char first
            return ('transpose', '')

        elif typo_type == 'extra_letter':
            # Add a random nearby letter
            wrong = TypoGenerator.get_adjacent_key(current_char)
            return ('extra', wrong)

        return ('adjacent', TypoGenerator.get_adjacent_key(current_char))


class HumanKeyboard:
    """
    Human-like keyboard input simulation

    Features:
    - Variable keystroke timing based on character complexity
    - Natural typo generation with backspace correction
    - Thinking pauses during typing
    - Speed variation for familiar vs. unfamiliar words
    - Realistic key hold times

    Usage:
        keyboard = HumanKeyboard(page, config)
        await keyboard.type_text("#input", "Hello World!")
    """

    def __init__(self, page: Any, config: HumanizeConfig):
        """
        Initialize HumanKeyboard

        Args:
            page: Playwright page object
            config: HumanizeConfig instance
        """
        self.page = page
        self.config = config
        self.keyboard_config: KeyboardConfig = config.keyboard
        self.timing = HumanTiming(config)
        self.typo_generator = TypoGenerator()

    def _is_complex_char(self, char: str) -> bool:
        """Check if character is complex (requires more time to type)"""
        return (
            char in COMPLEX_CHARS or
            char in NUMBER_CHARS or
            char.isupper()
        )

    def _get_char_delay(self, char: str, prev_char: Optional[str] = None) -> int:
        """
        Get delay for typing a specific character

        Factors:
        - Character complexity
        - Previous character (same finger?)
        - Speed multiplier from config
        """
        if self._is_complex_char(char):
            delay = self.timing.complex_char_delay()
        else:
            delay = self.timing.keystroke_delay()

        # Extra delay if same character as previous (same finger)
        if prev_char and prev_char.lower() == char.lower():
            delay = int(delay * 1.2)

        return delay

    async def type_text(
        self,
        selector: Optional[str] = None,
        text: str = "",
        by_role: Optional[str] = None,
        name: Optional[str] = None,
        clear_first: bool = True
    ) -> bool:
        """
        Type text with human-like characteristics

        Features:
        - Variable delays between keystrokes (80-200ms base)
        - Acceleration on familiar character sequences
        - Slowdown on complex characters (@, #, etc.)
        - Random typos with backspace correction
        - Thinking pauses every 5-15 characters
        - Extra delay after spaces

        Args:
            selector: CSS selector for input element
            text: Text to type
            by_role: Playwright role locator
            name: Name for role locator
            clear_first: Whether to clear existing content first

        Returns:
            True if successful
        """
        if not text:
            return True

        if not self.config.enabled or not self.keyboard_config.enabled:
            # Fall back to standard fill
            try:
                if by_role and name:
                    await self.page.get_by_role(by_role, name=name).fill(text)
                elif selector:
                    await self.page.locator(selector).fill(text)
                return True
            except Exception as e:
                print(f'[HUMANIZE] [ERROR] type_text (fallback): {e}')
                return False

        try:
            # Get element
            if by_role and name:
                element = self.page.get_by_role(by_role, name=name).first
            elif selector:
                element = self.page.locator(selector).first
            else:
                print('[HUMANIZE] [ERROR] type_text: No selector provided')
                return False

            # Click to focus
            await element.click()

            # Clear if requested
            if clear_first:
                await element.fill('')

            # Pre-typing pause
            await self.timing.delay(self.timing.pre_type_delay())

            # Type character by character
            prev_char = None
            chars_since_pause = 0
            i = 0

            while i < len(text):
                char = text[i]

                # Check for thinking pause
                chars_since_pause += 1
                if chars_since_pause >= random.randint(5, 15) and self.timing.should_thinking_pause():
                    await self.timing.delay(self.timing.get_typing_thinking_pause())
                    chars_since_pause = 0

                # Check for typo
                if self.timing.should_typo() and char.isalpha():
                    await self._make_typo(element, char)

                # Type the correct character
                await self._type_char(element, char)

                # Character-specific delay
                delay = self._get_char_delay(char, prev_char)
                await self.timing.delay(delay)

                # Extra delay after space (word boundary)
                if char == ' ':
                    await self.timing.delay(self.timing.get_space_delay())

                prev_char = char
                i += 1

            return True

        except Exception as e:
            print(f'[HUMANIZE] [ERROR] type_text: {e}')
            return False

    async def _type_char(self, element: Any, char: str):
        """Type a single character with realistic timing"""
        hold_time = self.timing.get_key_hold_time()

        # Use page.keyboard for more control
        await self.page.keyboard.press(char, delay=hold_time)

    async def _make_typo(self, element: Any, correct_char: str):
        """
        Simulate making and correcting a typo

        1. Type wrong character
        2. Pause (realizing mistake)
        3. Backspace
        4. Pause (before correction)
        """
        # Get wrong character
        wrong_char = self.typo_generator.get_adjacent_key(correct_char)

        # Type wrong character
        await self._type_char(element, wrong_char)

        # Pause - realizing mistake
        await self.timing.delay(self.timing.get_typo_realize_delay())

        # Backspace
        await self.page.keyboard.press('Backspace')

        # Pause before correct character
        await self.timing.delay(self.timing.get_typo_correct_delay())

    async def press_key(
        self,
        key: str,
        modifiers: Optional[List[str]] = None
    ) -> bool:
        """
        Press a single key with realistic timing

        Args:
            key: Key to press (e.g., 'Enter', 'Tab', 'a')
            modifiers: Optional modifiers ['Shift', 'Control', 'Alt']

        Returns:
            True if successful
        """
        if not self.config.enabled or not self.keyboard_config.enabled:
            try:
                if modifiers:
                    key_combo = '+'.join(modifiers + [key])
                    await self.page.keyboard.press(key_combo)
                else:
                    await self.page.keyboard.press(key)
                return True
            except Exception as e:
                print(f'[HUMANIZE] [ERROR] press_key (fallback): {e}')
                return False

        try:
            hold_time = self.timing.get_key_hold_time()

            if modifiers:
                # Press modifiers
                for mod in modifiers:
                    await self.page.keyboard.down(mod)

            # Press main key
            await self.page.keyboard.press(key, delay=hold_time)

            if modifiers:
                # Release modifiers in reverse order
                for mod in reversed(modifiers):
                    await self.page.keyboard.up(mod)

            return True

        except Exception as e:
            print(f'[HUMANIZE] [ERROR] press_key: {e}')
            return False

    async def paste_text(
        self,
        selector: Optional[str] = None,
        text: str = "",
        by_role: Optional[str] = None,
        name: Optional[str] = None
    ) -> bool:
        """
        Paste text using clipboard (Ctrl+V)

        Sometimes people copy-paste instead of typing,
        especially for long text or URLs.

        Args:
            selector: CSS selector
            text: Text to paste
            by_role: Playwright role locator
            name: Name for role locator

        Returns:
            True if successful
        """
        try:
            # Get element and focus
            if by_role and name:
                element = self.page.get_by_role(by_role, name=name).first
            elif selector:
                element = self.page.locator(selector).first
            else:
                return False

            await element.click()

            # Set clipboard content
            await self.page.evaluate(f'''
                navigator.clipboard.writeText({repr(text)})
            ''')

            # Small delay before paste
            await self.timing.delay(self.timing.micro_delay())

            # Paste with Ctrl+V
            await self.press_key('v', ['Control'])

            return True

        except Exception as e:
            # Fallback: just fill the field
            print(f'[HUMANIZE] [WARN] paste_text fallback: {e}')
            try:
                if by_role and name:
                    await self.page.get_by_role(by_role, name=name).fill(text)
                elif selector:
                    await self.page.locator(selector).fill(text)
                return True
            except:
                return False

    async def clear_field(
        self,
        selector: Optional[str] = None,
        by_role: Optional[str] = None,
        name: Optional[str] = None
    ) -> bool:
        """
        Clear a text field using keyboard (Ctrl+A, Backspace)

        More human-like than programmatic clearing.
        """
        try:
            # Focus element
            if by_role and name:
                element = self.page.get_by_role(by_role, name=name).first
            elif selector:
                element = self.page.locator(selector).first
            else:
                return False

            await element.click()

            # Select all with Ctrl+A
            await self.press_key('a', ['Control'])

            await self.timing.delay(self.timing.micro_delay())

            # Delete with Backspace
            await self.page.keyboard.press('Backspace')

            return True

        except Exception as e:
            print(f'[HUMANIZE] [ERROR] clear_field: {e}')
            return False

    def should_paste_instead(self, text: str) -> bool:
        """
        Determine if text should be pasted instead of typed

        Based on:
        - Text length
        - Paste probability setting
        - Text contains special patterns (URLs, emails)
        """
        if not self.keyboard_config.paste_chance_for_long_text:
            return False

        if len(text) < self.keyboard_config.paste_threshold_length:
            return False

        # Check for URL or email patterns
        is_url_or_email = (
            text.startswith('http://') or
            text.startswith('https://') or
            '@' in text and '.' in text
        )

        if is_url_or_email:
            # Higher chance to paste URLs and emails
            return random.random() < (self.keyboard_config.paste_chance_for_long_text * 2)

        return random.random() < self.keyboard_config.paste_chance_for_long_text
