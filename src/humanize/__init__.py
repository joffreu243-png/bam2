"""
Human-Like Behavior Module for Playwright Automation

This module provides realistic human-like behavior simulation for browser
automation, helping avoid detection by anti-bot systems.

Components:
- HumanBehavior: Main coordinator class (recommended entry point)
- HumanMouse: Mouse movement with Bezier curves and WindMouse algorithm
- HumanKeyboard: Typing with realistic delays and typos
- HumanScroll: Smooth scrolling with momentum
- HumanTiming: Delay generation with various distributions
- HumanizeConfig: Configuration with preset levels

Quick Start:
    from src.humanize import HumanBehavior, HumanizeConfig, HumanizeLevel

    # Create with preset level
    config = HumanizeConfig.from_level(HumanizeLevel.MODERATE)
    human = HumanBehavior(page, config)

    # Use for automation
    await human.click("#button")
    await human.type("#input", "Hello World!")
    await human.scroll_to("#section")
    await human.explore_page()

Or with convenience function:
    from src.humanize import create_human_behavior, HumanizeLevel

    human = create_human_behavior(page, HumanizeLevel.AGGRESSIVE)

Features:
    - Bezier curve mouse movements with WindMouse algorithm
    - Fitts's Law for realistic movement timing
    - Variable keystroke delays with typo simulation
    - Momentum-based smooth scrolling
    - Page exploration simulation
    - Configurable via presets or custom settings
    - Compatible with existing GUI config format

Presets:
    - OFF: No humanization (standard automation)
    - LIGHT: Minimal delays, fast but not robotic
    - MODERATE: Balanced settings (recommended)
    - AGGRESSIVE: Maximum human-likeness for strict anti-bots
    - CUSTOM: Use your own configuration
"""

# Configuration
from .config import (
    HumanizeConfig,
    HumanizeLevel,
    MouseConfig,
    KeyboardConfig,
    ScrollConfig,
    TimingConfig,
    ExplorationConfig,
    DEFAULT_CONFIG,
)

# Core modules
from .timing import HumanTiming, human_delay_sync, human_delay_async
from .mouse import HumanMouse, BezierCurve, WindMouse, FittsLaw, Point
from .keyboard import HumanKeyboard, TypoGenerator
from .scroll import HumanScroll, ScrollPhysics

# Main coordinator
from .behavior import (
    HumanBehavior,
    create_human_behavior,
    create_human_behavior_from_dict,
)

__version__ = "1.0.0"

__all__ = [
    # Config
    "HumanizeConfig",
    "HumanizeLevel",
    "MouseConfig",
    "KeyboardConfig",
    "ScrollConfig",
    "TimingConfig",
    "ExplorationConfig",
    "DEFAULT_CONFIG",
    # Timing
    "HumanTiming",
    "human_delay_sync",
    "human_delay_async",
    # Mouse
    "HumanMouse",
    "BezierCurve",
    "WindMouse",
    "FittsLaw",
    "Point",
    # Keyboard
    "HumanKeyboard",
    "TypoGenerator",
    # Scroll
    "HumanScroll",
    "ScrollPhysics",
    # Behavior (main)
    "HumanBehavior",
    "create_human_behavior",
    "create_human_behavior_from_dict",
]
