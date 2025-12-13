"""
Human-Like Mouse Movement Module

Implements realistic mouse movement patterns using:
- Cubic Bezier Curves for smooth trajectories
- WindMouse Algorithm for natural path variation
- Fitts's Law for realistic movement duration
- Micro-jitter for human imperfection
"""

import random
import math
import time
from typing import Tuple, List, Optional, Any
from dataclasses import dataclass

from .config import HumanizeConfig, MouseConfig
from .timing import HumanTiming


@dataclass
class Point:
    """2D point with x and y coordinates"""
    x: float
    y: float

    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Point':
        return Point(self.x * scalar, self.y * scalar)


class BezierCurve:
    """
    Cubic Bezier curve implementation for smooth mouse trajectories

    A cubic Bezier curve is defined by 4 control points:
    - P0: Start point
    - P1: First control point (influences curve near start)
    - P2: Second control point (influences curve near end)
    - P3: End point
    """

    @staticmethod
    def cubic_bezier(
        t: float,
        p0: Point,
        p1: Point,
        p2: Point,
        p3: Point
    ) -> Point:
        """
        Calculate point on cubic Bezier curve at parameter t

        Args:
            t: Parameter value 0.0 to 1.0
            p0-p3: Control points

        Returns:
            Point on the curve
        """
        u = 1 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t

        # B(t) = (1-t)^3*P0 + 3*(1-t)^2*t*P1 + 3*(1-t)*t^2*P2 + t^3*P3
        x = uuu * p0.x + 3 * uu * t * p1.x + 3 * u * tt * p2.x + ttt * p3.x
        y = uuu * p0.y + 3 * uu * t * p1.y + 3 * u * tt * p2.y + ttt * p3.y

        return Point(x, y)

    @staticmethod
    def generate_control_points(
        start: Point,
        end: Point,
        curvature: float = 0.5
    ) -> Tuple[Point, Point]:
        """
        Generate natural control points for Bezier curve

        Args:
            start: Starting point
            end: Ending point
            curvature: How much the curve bends (0-1)

        Returns:
            Tuple of two control points (P1, P2)
        """
        distance = start.distance_to(end)

        # Calculate perpendicular offset direction
        dx = end.x - start.x
        dy = end.y - start.y

        # Perpendicular vector (normalized)
        if distance > 0:
            perp_x = -dy / distance
            perp_y = dx / distance
        else:
            perp_x, perp_y = 0, 0

        # Random offset magnitude (perpendicular to line)
        offset1 = random.uniform(-distance * curvature, distance * curvature)
        offset2 = random.uniform(-distance * curvature, distance * curvature)

        # Control point 1: 25-35% along the line with offset
        t1 = random.uniform(0.25, 0.35)
        p1 = Point(
            start.x + dx * t1 + perp_x * offset1,
            start.y + dy * t1 + perp_y * offset1
        )

        # Control point 2: 65-75% along the line with offset
        t2 = random.uniform(0.65, 0.75)
        p2 = Point(
            start.x + dx * t2 + perp_x * offset2,
            start.y + dy * t2 + perp_y * offset2
        )

        return p1, p2

    @staticmethod
    def generate_path(
        start: Point,
        end: Point,
        num_points: int = 20,
        curvature: float = 0.3
    ) -> List[Point]:
        """
        Generate a smooth path from start to end using Bezier curve

        Args:
            start: Starting point
            end: Ending point
            num_points: Number of points in the path
            curvature: How much the curve bends

        Returns:
            List of points forming the path
        """
        p1, p2 = BezierCurve.generate_control_points(start, end, curvature)

        path = []
        for i in range(num_points):
            t = i / (num_points - 1) if num_points > 1 else 0
            point = BezierCurve.cubic_bezier(t, start, p1, p2, end)
            path.append(point)

        return path


class WindMouse:
    """
    WindMouse Algorithm Implementation

    This algorithm simulates natural mouse movement by adding:
    - "Wind": Random forces that push the cursor off course
    - "Gravity": Force that pulls the cursor toward the target

    Reference: Based on the BenLand100 WindMouse algorithm
    """

    @staticmethod
    def generate_path(
        start: Point,
        end: Point,
        gravity: float = 9.0,
        wind: float = 3.0,
        min_wait: float = 2.0,
        max_wait: float = 10.0,
        max_step: float = 10.0,
        target_area: float = 8.0
    ) -> List[Tuple[Point, float]]:
        """
        Generate mouse movement path using WindMouse algorithm

        Args:
            start: Starting position
            end: Target position
            gravity: Force pulling toward target (higher = more direct)
            wind: Random force magnitude (higher = more wandering)
            min_wait: Minimum wait between steps (ms)
            max_wait: Maximum wait between steps (ms)
            max_step: Maximum distance per step
            target_area: Radius around target to slow down

        Returns:
            List of (Point, delay_ms) tuples
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

        while True:
            distance = current.distance_to(end)

            if distance < 1:
                break

            # Decrease wind and gravity near target
            if distance < target_area:
                w = wind * (distance / target_area)
                g = gravity * (distance / target_area)
            else:
                w = wind
                g = gravity

            # Wind changes direction randomly
            wind_x = wind_x / sqrt3 + (random.random() * (w * 2 + 1) - w) / sqrt5
            wind_y = wind_y / sqrt3 + (random.random() * (w * 2 + 1) - w) / sqrt5

            # Calculate direction to target
            if distance > 0:
                direction_x = (end.x - current.x) / distance
                direction_y = (end.y - current.y) / distance
            else:
                direction_x, direction_y = 0, 0

            # Add gravity toward target
            velocity_x += wind_x + g * direction_x
            velocity_y += wind_y + g * direction_y

            # Calculate velocity magnitude
            velocity_mag = math.sqrt(velocity_x ** 2 + velocity_y ** 2)

            # Limit step size
            if velocity_mag > max_step:
                scale = max_step / velocity_mag
                velocity_x *= scale
                velocity_y *= scale
                velocity_mag = max_step

            # Reduce velocity near target for precision
            if velocity_mag > distance:
                velocity_x = (end.x - current.x) * 0.9
                velocity_y = (end.y - current.y) * 0.9

            # Move
            current = Point(
                current.x + velocity_x,
                current.y + velocity_y
            )

            # Calculate delay based on step size
            step_size = math.sqrt(velocity_x ** 2 + velocity_y ** 2)
            if step_size > 0:
                delay = min_wait + (max_wait - min_wait) * (step_size / max_step)
            else:
                delay = min_wait

            path.append((current, delay))

            # Safety limit
            if len(path) > 2000:
                break

        # Final point at exact target
        path.append((end, min_wait))

        return path


class FittsLaw:
    """
    Fitts's Law Implementation

    Fitts's Law predicts that the time required to move to a target
    is a function of the distance to and size of the target:

    MT = a + b * log2(D/W + 1)

    Where:
    - MT: Movement time
    - D: Distance to target
    - W: Width of target
    - a, b: Constants (empirically determined)
    """

    # Empirical constants (based on human studies)
    A_COEFFICIENT = 50  # Base time in ms
    B_COEFFICIENT = 150  # Scaling factor

    @staticmethod
    def movement_time(distance: float, target_width: float) -> float:
        """
        Calculate expected movement time using Fitts's Law

        Args:
            distance: Distance to target in pixels
            target_width: Width of target in pixels

        Returns:
            Expected movement time in milliseconds
        """
        if target_width <= 0:
            target_width = 1

        if distance <= 0:
            return FittsLaw.A_COEFFICIENT

        # Index of Difficulty
        id_value = math.log2(distance / target_width + 1)

        # Movement Time
        mt = FittsLaw.A_COEFFICIENT + FittsLaw.B_COEFFICIENT * id_value

        return mt

    @staticmethod
    def steps_for_movement(distance: float, target_width: float) -> int:
        """
        Calculate recommended number of steps for smooth movement

        Args:
            distance: Distance to target
            target_width: Width of target

        Returns:
            Recommended number of steps
        """
        mt = FittsLaw.movement_time(distance, target_width)

        # Aim for ~10-15ms per step for smooth movement
        steps = int(mt / 12)

        # Clamp to reasonable range
        return max(10, min(steps, 100))


class HumanMouse:
    """
    Main class for human-like mouse movements

    Combines Bezier curves, WindMouse algorithm, and Fitts's Law
    for realistic mouse automation.

    Usage:
        mouse = HumanMouse(page, config)
        await mouse.move_to("#button")
        await mouse.click("#submit")
    """

    def __init__(self, page: Any, config: HumanizeConfig):
        """
        Initialize HumanMouse

        Args:
            page: Playwright page object
            config: HumanizeConfig instance
        """
        self.page = page
        self.config = config
        self.mouse_config: MouseConfig = config.mouse
        self.timing = HumanTiming(config)
        self._current_position: Optional[Point] = None

    async def _get_current_position(self) -> Point:
        """Get current mouse position (or estimate from viewport center)"""
        if self._current_position:
            return self._current_position

        try:
            # Estimate from viewport center
            viewport = await self.page.evaluate('''
                () => ({
                    x: window.innerWidth / 2,
                    y: window.innerHeight / 2
                })
            ''')
            return Point(viewport['x'], viewport['y'])
        except Exception:
            return Point(500, 300)

    async def _get_element_bounds(
        self,
        selector: Optional[str] = None,
        by_role: Optional[str] = None,
        name: Optional[str] = None
    ) -> Optional[dict]:
        """Get bounding box of element"""
        try:
            if by_role and name:
                element = self.page.get_by_role(by_role, name=name)
            elif selector:
                element = self.page.locator(selector)
            else:
                return None

            box = await element.bounding_box()
            return box
        except Exception:
            return None

    def _get_click_offset(self, box: dict) -> Point:
        """
        Calculate click position with natural offset from center

        Uses Gaussian distribution - most clicks near center,
        occasional clicks toward edges.
        """
        max_offset = self.mouse_config.click_offset_max

        # Gaussian distribution for more clicks near center
        offset_x = random.gauss(0, max_offset / 2)
        offset_y = random.gauss(0, max_offset / 2)

        # Clamp to element bounds
        max_x = (box['width'] / 2) - 2
        max_y = (box['height'] / 2) - 2

        offset_x = max(-max_x, min(offset_x, max_x))
        offset_y = max(-max_y, min(offset_y, max_y))

        return Point(
            box['x'] + box['width'] / 2 + offset_x,
            box['y'] + box['height'] / 2 + offset_y
        )

    def _add_jitter(self, point: Point) -> Point:
        """Add micro-jitter to a point"""
        jitter = self.mouse_config.jitter

        if jitter <= 0:
            return point

        jitter_x = random.uniform(-jitter, jitter)
        jitter_y = random.uniform(-jitter, jitter)

        return Point(point.x + jitter_x, point.y + jitter_y)

    def _generate_trajectory(
        self,
        start: Point,
        end: Point,
        target_width: float = 50
    ) -> List[Tuple[Point, float]]:
        """
        Generate complete movement trajectory

        Uses WindMouse for natural paths with Fitts's Law timing.
        """
        distance = start.distance_to(end)

        # Use Fitts's Law for movement duration estimation
        movement_time = FittsLaw.movement_time(distance, target_width)
        num_steps = FittsLaw.steps_for_movement(distance, target_width)

        # Apply speed multiplier
        speed = self.mouse_config.speed
        if speed > 0:
            movement_time /= speed
            num_steps = int(num_steps / speed)

        num_steps = max(10, min(num_steps, 100))

        # Generate path using WindMouse
        path = WindMouse.generate_path(
            start, end,
            gravity=self.mouse_config.wind_gravity,
            wind=self.mouse_config.wind_wind,
            min_wait=self.mouse_config.wind_min_wait,
            max_wait=self.mouse_config.wind_max_wait,
            max_step=self.mouse_config.wind_max_step,
            target_area=self.mouse_config.wind_target_area
        )

        # Add jitter to each point
        result = []
        for point, delay in path:
            jittered = self._add_jitter(point)
            result.append((jittered, delay))

        return result

    async def move_to(
        self,
        selector: Optional[str] = None,
        by_role: Optional[str] = None,
        name: Optional[str] = None,
        offset: Optional[Point] = None
    ) -> bool:
        """
        Move mouse to element with human-like trajectory

        Features:
        - Bezier/WindMouse curved path
        - Fitts's Law timing
        - Micro-jitter during movement
        - Optional overshoot with correction
        - Variable speed (slower at start/end)

        Args:
            selector: CSS selector
            by_role: Playwright role locator
            name: Name for role locator
            offset: Custom offset from element center

        Returns:
            True if successful, False otherwise
        """
        if not self.config.enabled or not self.mouse_config.enabled:
            return True

        try:
            # Get element bounds
            box = await self._get_element_bounds(selector, by_role, name)
            if not box:
                print(f'[HUMANIZE] [WARN] move_to: Element not found')
                return False

            # Get current and target positions
            start = await self._get_current_position()

            if offset:
                target = Point(
                    box['x'] + box['width'] / 2 + offset.x,
                    box['y'] + box['height'] / 2 + offset.y
                )
            else:
                target = self._get_click_offset(box)

            # Check for overshoot
            if self.timing.should_overshoot_mouse():
                # Overshoot past target
                overshoot_dist = random.randint(*self.mouse_config.overshoot_distance)
                direction = random.uniform(0, 2 * math.pi)

                overshoot_target = Point(
                    target.x + math.cos(direction) * overshoot_dist,
                    target.y + math.sin(direction) * overshoot_dist
                )

                # Move to overshoot point
                await self._execute_movement(start, overshoot_target, box['width'])

                # Pause (realizing overshoot)
                await self.timing.delay(self.timing.micro_delay())

                # Correct to actual target
                await self._execute_movement(overshoot_target, target, box['width'])
            else:
                # Direct movement
                await self._execute_movement(start, target, box['width'])

            self._current_position = target
            return True

        except Exception as e:
            print(f'[HUMANIZE] [ERROR] move_to: {e}')
            return False

    async def _execute_movement(
        self,
        start: Point,
        end: Point,
        target_width: float
    ):
        """Execute the actual mouse movement"""
        trajectory = self._generate_trajectory(start, end, target_width)

        for point, delay in trajectory:
            await self.page.mouse.move(point.x, point.y)
            if delay > 0:
                await self.timing.delay(delay)

    async def click(
        self,
        selector: Optional[str] = None,
        by_role: Optional[str] = None,
        name: Optional[str] = None,
        button: str = "left"
    ) -> bool:
        """
        Perform human-like click on element

        Features:
        - Move to element first
        - Random offset from center
        - Hesitation before click
        - Realistic mousedown/mouseup timing

        Args:
            selector: CSS selector
            by_role: Playwright role locator
            name: Name for role locator
            button: Mouse button ("left", "right", "middle")

        Returns:
            True if successful
        """
        if not self.config.enabled or not self.mouse_config.enabled:
            # Fall back to standard click
            try:
                if by_role and name:
                    await self.page.get_by_role(by_role, name=name).click()
                elif selector:
                    await self.page.click(selector)
                return True
            except Exception as e:
                print(f'[HUMANIZE] [ERROR] click (fallback): {e}')
                return False

        try:
            # Move to element
            moved = await self.move_to(selector, by_role, name)
            if not moved:
                return False

            # Hesitation before click
            await self.timing.delay(self.timing.click_hesitation())

            # Perform click with realistic timing
            hold_time = self.timing.get_key_hold_time()

            await self.page.mouse.down(button=button)
            await self.timing.delay(hold_time)
            await self.page.mouse.up(button=button)

            return True

        except Exception as e:
            print(f'[HUMANIZE] [ERROR] click: {e}')
            return False

    async def double_click(
        self,
        selector: Optional[str] = None,
        by_role: Optional[str] = None,
        name: Optional[str] = None
    ) -> bool:
        """
        Perform human-like double-click

        Features realistic interval between clicks (50-150ms).
        """
        if not self.config.enabled or not self.mouse_config.enabled:
            try:
                if by_role and name:
                    await self.page.get_by_role(by_role, name=name).dblclick()
                elif selector:
                    await self.page.dblclick(selector)
                return True
            except Exception as e:
                print(f'[HUMANIZE] [ERROR] double_click (fallback): {e}')
                return False

        try:
            # Move to element
            moved = await self.move_to(selector, by_role, name)
            if not moved:
                return False

            # First click
            hold_time = self.timing.get_key_hold_time()
            await self.page.mouse.down()
            await self.timing.delay(hold_time)
            await self.page.mouse.up()

            # Interval between clicks (50-150ms typical for double-click)
            interval = random.randint(50, 150)
            await self.timing.delay(interval)

            # Second click
            await self.page.mouse.down()
            await self.timing.delay(hold_time)
            await self.page.mouse.up()

            return True

        except Exception as e:
            print(f'[HUMANIZE] [ERROR] double_click: {e}')
            return False

    async def hover(
        self,
        selector: Optional[str] = None,
        by_role: Optional[str] = None,
        name: Optional[str] = None,
        duration_ms: Optional[Tuple[int, int]] = None
    ) -> bool:
        """
        Hover over element for specified duration

        Args:
            selector: CSS selector
            by_role: Playwright role locator
            name: Name for role locator
            duration_ms: (min, max) hover duration in ms

        Returns:
            True if successful
        """
        if duration_ms is None:
            duration_ms = (500, 1500)

        try:
            moved = await self.move_to(selector, by_role, name)
            if not moved:
                return False

            hover_time = random.randint(*duration_ms)
            await self.timing.delay(hover_time)

            return True

        except Exception as e:
            print(f'[HUMANIZE] [ERROR] hover: {e}')
            return False

    async def random_movement(self, bounds: Optional[dict] = None):
        """
        Perform random mouse movement within bounds

        Useful for "idle" behavior simulation.
        """
        try:
            if bounds is None:
                viewport = await self.page.evaluate('''
                    () => ({
                        width: window.innerWidth,
                        height: window.innerHeight
                    })
                ''')
                bounds = {'x': 0, 'y': 0, **viewport}

            start = await self._get_current_position()
            target = Point(
                random.uniform(bounds['x'] + 50, bounds['x'] + bounds['width'] - 50),
                random.uniform(bounds['y'] + 50, bounds['y'] + bounds['height'] - 50)
            )

            await self._execute_movement(start, target, 100)
            self._current_position = target

        except Exception as e:
            print(f'[HUMANIZE] [WARN] random_movement: {e}')
