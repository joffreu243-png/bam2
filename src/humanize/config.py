"""
Human-Like Behavior Configuration Module

Provides configuration presets and settings for human-like browser automation.
All timing values are in milliseconds unless otherwise noted.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from enum import Enum


class HumanizeLevel(Enum):
    """Preset levels for human-like behavior intensity"""
    OFF = "off"                # Без humanize - обычная автоматизация
    LIGHT = "light"            # Минимальные задержки - быстро, но не палевно
    MODERATE = "moderate"      # Сбалансированный режим - рекомендуется
    AGGRESSIVE = "aggressive"  # Максимальная имитация - для строгих антиботов
    CUSTOM = "custom"          # Пользовательские настройки


@dataclass
class MouseConfig:
    """Configuration for mouse movement behavior"""
    enabled: bool = True

    # Speed multiplier (0.5 = half speed, 2.0 = double speed)
    speed: float = 1.0

    # Probability of overshooting target and correcting (0.0 - 0.3)
    overshoot_chance: float = 0.15

    # Overshoot distance range in pixels
    overshoot_distance: Tuple[int, int] = (5, 25)

    # Micro-jitter amplitude in pixels during movement (0-5)
    jitter: int = 2

    # Maximum click offset from element center (Gaussian distribution)
    click_offset_max: int = 10

    # Base delay between mouse move steps in ms
    move_step_delay: Tuple[int, int] = (5, 15)

    # Number of points in movement trajectory
    trajectory_points: Tuple[int, int] = (15, 30)

    # WindMouse algorithm parameters
    wind_gravity: float = 9.0     # Притяжение к цели
    wind_wind: float = 3.0        # Случайные отклонения
    wind_min_wait: float = 2.0    # Минимальная задержка между шагами
    wind_max_wait: float = 10.0   # Максимальная задержка между шагами
    wind_max_step: float = 10.0   # Максимальный размер шага
    wind_target_area: float = 8.0 # Размер целевой области


@dataclass
class KeyboardConfig:
    """Configuration for keyboard typing behavior"""
    enabled: bool = True

    # Speed multiplier (0.5 = half speed, 2.0 = double speed)
    speed: float = 1.0

    # Base delay between keystrokes in ms
    keystroke_delay: Tuple[int, int] = (80, 200)

    # Delay range for complex characters (@, #, numbers)
    complex_char_delay: Tuple[int, int] = (150, 350)

    # Probability of making a typo (0.0 - 0.15)
    typo_chance: float = 0.05

    # Delay before correcting typo with backspace
    typo_realize_delay: Tuple[int, int] = (100, 400)

    # Delay after backspace before correct character
    typo_correct_delay: Tuple[int, int] = (50, 150)

    # Probability of "thinking pause" (0.1 - 0.3)
    thinking_pause_chance: float = 0.07

    # Duration of thinking pause in ms
    thinking_pause_duration: Tuple[int, int] = (1000, 3500)

    # Extra delay after spaces (word boundaries)
    space_delay: Tuple[int, int] = (100, 400)

    # Key hold time (time between keydown and keyup)
    key_hold_time: Tuple[int, int] = (30, 100)

    # Chance to use paste instead of typing for long text
    paste_chance_for_long_text: float = 0.0

    # Text length threshold for paste consideration
    paste_threshold_length: int = 50


@dataclass
class ScrollConfig:
    """Configuration for scrolling behavior"""
    enabled: bool = True

    # Speed multiplier
    speed: float = 1.0

    # Scroll step size in pixels
    step_size: Tuple[int, int] = (50, 150)

    # Enable momentum (inertia) effect
    momentum_enabled: bool = True

    # Momentum decay factor (0-1, higher = longer momentum)
    momentum_decay: float = 0.85

    # Jitter in scroll distance
    jitter: int = 15

    # Probability of overshoot and correction
    overshoot_chance: float = 0.3

    # Overshoot distance in pixels
    overshoot_distance: Tuple[int, int] = (50, 200)

    # Delay between scroll steps in ms
    step_delay: Tuple[int, int] = (30, 100)

    # Reading pause probability (when "reading" content)
    reading_pause_chance: float = 0.3

    # Reading pause duration in ms
    reading_pause_duration: Tuple[int, int] = (500, 2000)


@dataclass
class TimingConfig:
    """Configuration for general timing and delays"""
    # Delay between major actions (click, type, etc.)
    action_delay: Tuple[int, int] = (300, 1500)

    # Delay after page loads
    page_load_delay: Tuple[int, int] = (1000, 3000)

    # Long thinking pause
    thinking_delay: Tuple[int, int] = (2000, 5000)

    # Micro delay between related actions
    micro_delay: Tuple[int, int] = (50, 200)

    # Hesitation before clicking (simulates decision making)
    click_hesitation: Tuple[int, int] = (100, 500)

    # Delay before starting to type
    pre_type_delay: Tuple[int, int] = (200, 600)

    # Delay variance factor (adds randomness to all delays)
    variance_factor: float = 0.3


@dataclass
class ExplorationConfig:
    """Configuration for page exploration behavior"""
    enabled: bool = True

    # Intensity level: light, normal, thorough
    intensity: str = "normal"

    # How many headings to potentially look at
    max_headings: int = 3

    # Probability of hovering over links
    link_hover_chance: float = 0.2

    # Exploration duration range in seconds
    duration: Tuple[float, float] = (3.0, 8.0)

    # Chance to scroll during exploration
    scroll_chance: float = 0.6

    # Max scroll distance during exploration (viewport percentage)
    max_scroll_percent: float = 0.5


@dataclass
class HumanizeConfig:
    """
    Main configuration class for human-like behavior

    Usage:
        # From preset
        config = HumanizeConfig.from_level(HumanizeLevel.MODERATE)

        # Custom
        config = HumanizeConfig(
            mouse=MouseConfig(speed=0.8, overshoot_chance=0.2),
            keyboard=KeyboardConfig(typo_chance=0.08)
        )
    """
    # Master switch
    enabled: bool = True

    # Current level (for display/logging)
    level: HumanizeLevel = HumanizeLevel.MODERATE

    # Sub-configurations
    mouse: MouseConfig = field(default_factory=MouseConfig)
    keyboard: KeyboardConfig = field(default_factory=KeyboardConfig)
    scroll: ScrollConfig = field(default_factory=ScrollConfig)
    timing: TimingConfig = field(default_factory=TimingConfig)
    exploration: ExplorationConfig = field(default_factory=ExplorationConfig)

    @classmethod
    def from_level(cls, level: HumanizeLevel) -> 'HumanizeConfig':
        """Create configuration from a preset level"""

        if level == HumanizeLevel.OFF:
            return cls(
                enabled=False,
                level=level,
                mouse=MouseConfig(enabled=False),
                keyboard=KeyboardConfig(enabled=False),
                scroll=ScrollConfig(enabled=False),
                exploration=ExplorationConfig(enabled=False)
            )

        elif level == HumanizeLevel.LIGHT:
            return cls(
                enabled=True,
                level=level,
                mouse=MouseConfig(
                    speed=1.5,
                    overshoot_chance=0.08,
                    jitter=1,
                    trajectory_points=(10, 18)
                ),
                keyboard=KeyboardConfig(
                    speed=1.5,
                    keystroke_delay=(50, 120),
                    typo_chance=0.02,
                    thinking_pause_chance=0.03
                ),
                scroll=ScrollConfig(
                    speed=1.5,
                    momentum_enabled=False,
                    overshoot_chance=0.1,
                    step_delay=(20, 50)
                ),
                timing=TimingConfig(
                    action_delay=(150, 600),
                    page_load_delay=(500, 1500),
                    variance_factor=0.2
                ),
                exploration=ExplorationConfig(
                    enabled=True,
                    intensity="light",
                    duration=(1.5, 3.0)
                )
            )

        elif level == HumanizeLevel.MODERATE:
            # Default balanced settings
            return cls(
                enabled=True,
                level=level,
                mouse=MouseConfig(),
                keyboard=KeyboardConfig(),
                scroll=ScrollConfig(),
                timing=TimingConfig(),
                exploration=ExplorationConfig()
            )

        elif level == HumanizeLevel.AGGRESSIVE:
            return cls(
                enabled=True,
                level=level,
                mouse=MouseConfig(
                    speed=0.7,
                    overshoot_chance=0.25,
                    overshoot_distance=(10, 40),
                    jitter=3,
                    click_offset_max=15,
                    trajectory_points=(25, 45)
                ),
                keyboard=KeyboardConfig(
                    speed=0.7,
                    keystroke_delay=(100, 280),
                    typo_chance=0.08,
                    thinking_pause_chance=0.12,
                    thinking_pause_duration=(1500, 5000),
                    space_delay=(200, 700)
                ),
                scroll=ScrollConfig(
                    speed=0.6,
                    momentum_enabled=True,
                    momentum_decay=0.9,
                    overshoot_chance=0.4,
                    step_delay=(50, 150),
                    reading_pause_chance=0.45
                ),
                timing=TimingConfig(
                    action_delay=(500, 2500),
                    page_load_delay=(1500, 4000),
                    thinking_delay=(3000, 8000),
                    variance_factor=0.4
                ),
                exploration=ExplorationConfig(
                    enabled=True,
                    intensity="thorough",
                    duration=(5.0, 15.0),
                    link_hover_chance=0.35,
                    scroll_chance=0.8
                )
            )

        else:
            # Custom or unknown - return defaults
            return cls(enabled=True, level=level)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HumanizeConfig':
        """
        Create configuration from a dictionary

        Compatible with the existing GUI config format:
        {
            'enabled': True,
            'typing_speed': 'normal',  # slow/normal/fast
            'mouse_speed': 'normal',   # slow/normal/fast
            'scroll_behavior': 'smooth',  # smooth/instant
            'make_typos': True,
            'typo_rate': 0.05,
            'page_exploration_enabled': True,
            'exploration_intensity': 'normal'  # light/normal/thorough
        }
        """
        if not data.get('enabled', True):
            return cls.from_level(HumanizeLevel.OFF)

        # Map speed strings to multipliers
        speed_map = {
            'slow': 0.7,
            'normal': 1.0,
            'fast': 1.5
        }

        mouse_speed = speed_map.get(data.get('mouse_speed', 'normal'), 1.0)
        typing_speed = speed_map.get(data.get('typing_speed', 'normal'), 1.0)

        # Scroll behavior
        scroll_enabled = data.get('scroll_behavior', 'smooth') == 'smooth'

        # Typos
        make_typos = data.get('make_typos', True)
        typo_rate = data.get('typo_rate', 0.05) if make_typos else 0.0

        # Exploration
        exploration_enabled = data.get('page_exploration_enabled', True)
        exploration_intensity = data.get('exploration_intensity', 'normal')

        # Calculate exploration duration based on intensity
        duration_map = {
            'light': (1.5, 4.0),
            'normal': (3.0, 8.0),
            'thorough': (6.0, 15.0)
        }
        exploration_duration = duration_map.get(exploration_intensity, (3.0, 8.0))

        return cls(
            enabled=True,
            level=HumanizeLevel.CUSTOM,
            mouse=MouseConfig(
                enabled=True,
                speed=mouse_speed
            ),
            keyboard=KeyboardConfig(
                enabled=True,
                speed=typing_speed,
                typo_chance=typo_rate
            ),
            scroll=ScrollConfig(
                enabled=scroll_enabled,
                momentum_enabled=scroll_enabled
            ),
            timing=TimingConfig(),
            exploration=ExplorationConfig(
                enabled=exploration_enabled,
                intensity=exploration_intensity,
                duration=exploration_duration
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration to dictionary format"""
        # Map speed multipliers back to strings
        def speed_to_str(speed: float) -> str:
            if speed <= 0.8:
                return 'slow'
            elif speed >= 1.3:
                return 'fast'
            return 'normal'

        return {
            'enabled': self.enabled,
            'level': self.level.value,
            'typing_speed': speed_to_str(self.keyboard.speed),
            'mouse_speed': speed_to_str(self.mouse.speed),
            'scroll_behavior': 'smooth' if self.scroll.enabled else 'instant',
            'make_typos': self.keyboard.typo_chance > 0,
            'typo_rate': self.keyboard.typo_chance,
            'page_exploration_enabled': self.exploration.enabled,
            'exploration_intensity': self.exploration.intensity
        }


# Default configuration instance
DEFAULT_CONFIG = HumanizeConfig.from_level(HumanizeLevel.MODERATE)
