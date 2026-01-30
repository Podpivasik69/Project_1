"""
Utility functions and classes for the game
Following DRY principle and providing reusable components
"""

import pygame
from typing import Tuple, List
from enum import Enum


class Colors:
    """Color constants for consistent theming."""
    
    # Background colors
    SKY_BLUE = (135, 206, 235)
    MIDNIGHT_BLUE = (25, 25, 112)
    DARK_BLUE = (50, 50, 150)
    CORNFLOWER_BLUE = (100, 149, 237)
    
    # UI colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GOLD = (255, 215, 0)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (100, 100, 100)
    YELLOW = (255, 255, 0)
    
    # Game object colors
    PLAYER_BLUE = (100, 150, 255)
    PLATFORM_BROWN = (139, 69, 19)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)


class FontSizes:
    """Font size constants."""
    SMALL = 20
    MEDIUM = 24
    LARGE = 32
    EXTRA_LARGE = 64


class RenderUtils:
    """Utility functions for rendering."""
    
    @staticmethod
    def draw_gradient_background(surface: pygame.Surface, color1: Tuple[int, int, int], 
                               color2: Tuple[int, int, int], width: int, height: int) -> None:
        """
        Draw a vertical gradient background.
        
        Args:
            surface: Surface to draw on
            color1: Top color (RGB)
            color2: Bottom color (RGB)
            width: Width of gradient
            height: Height of gradient
        """
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            color = (r, g, b)
            pygame.draw.line(surface, color, (0, y), (width, y))
    
    @staticmethod
    def create_panel(width: int, height: int, background_color: Tuple[int, int, int], 
                    border_color: Tuple[int, int, int] = None, alpha: int = 180) -> pygame.Surface:
        """
        Create a semi-transparent panel with optional border.
        
        Args:
            width: Panel width
            height: Panel height
            background_color: Background color (RGB)
            border_color: Border color (RGB), None for no border
            alpha: Transparency (0-255)
            
        Returns:
            Panel surface
        """
        panel = pygame.Surface((width, height))
        panel.set_alpha(alpha)
        panel.fill(background_color)
        
        if border_color:
            pygame.draw.rect(panel, border_color, (0, 0, width, height), 2)
        
        return panel
    
    @staticmethod
    def draw_text_with_shadow(surface: pygame.Surface, text: str, font: pygame.font.Font,
                            position: Tuple[int, int], text_color: Tuple[int, int, int],
                            shadow_color: Tuple[int, int, int] = Colors.BLACK,
                            shadow_offset: Tuple[int, int] = (3, 3)) -> None:
        """
        Draw text with shadow effect.
        
        Args:
            surface: Surface to draw on
            text: Text to draw
            font: Font to use
            position: Text position (x, y)
            text_color: Text color (RGB)
            shadow_color: Shadow color (RGB)
            shadow_offset: Shadow offset (x, y)
        """
        # Draw shadow
        shadow_surface = font.render(text, True, shadow_color)
        shadow_rect = shadow_surface.get_rect(center=(position[0] + shadow_offset[0], 
                                                     position[1] + shadow_offset[1]))
        surface.blit(shadow_surface, shadow_rect)
        
        # Draw text
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=position)
        surface.blit(text_surface, text_rect)
    
    @staticmethod
    def draw_stars(surface: pygame.Surface, width: int, height: int, count: int = 50, 
                  seed: int = 42) -> None:
        """
        Draw decorative stars on surface.
        
        Args:
            surface: Surface to draw on
            width: Surface width
            height: Surface height
            count: Number of stars
            seed: Random seed for consistent placement
        """
        import random
        random.seed(seed)
        
        for _ in range(count):
            x = random.randint(0, width)
            y = random.randint(0, height // 2)
            size = random.randint(1, 3)
            brightness = random.randint(100, 255)
            color = (brightness, brightness, brightness)
            pygame.draw.circle(surface, color, (x, y), size)


class MathUtils:
    """Mathematical utility functions."""
    
    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
        """Clamp value between min and max."""
        return max(min_value, min(value, max_value))
    
    @staticmethod
    def lerp(start: float, end: float, t: float) -> float:
        """Linear interpolation between start and end."""
        return start + (end - start) * t
    
    @staticmethod
    def map_range(value: float, from_min: float, from_max: float, 
                 to_min: float, to_max: float) -> float:
        """Map value from one range to another."""
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min


class PerformanceMonitor:
    """Monitor game performance metrics."""
    
    def __init__(self):
        self.frame_count = 0
        self.fps_timer = 0.0
        self.current_fps = 0.0
        self.delta_times: List[float] = []
        self.max_delta_history = 60  # Keep last 60 frames
    
    def update(self, delta_time: float) -> None:
        """Update performance metrics."""
        self.frame_count += 1
        self.fps_timer += delta_time
        
        # Track delta times
        self.delta_times.append(delta_time)
        if len(self.delta_times) > self.max_delta_history:
            self.delta_times.pop(0)
        
        # Update FPS every second
        if self.fps_timer >= 1.0:
            self.current_fps = self.frame_count / self.fps_timer
            self.frame_count = 0
            self.fps_timer = 0.0
    
    def get_fps(self) -> float:
        """Get current FPS."""
        return self.current_fps
    
    def get_average_delta_time(self) -> float:
        """Get average delta time over recent frames."""
        if not self.delta_times:
            return 0.0
        return sum(self.delta_times) / len(self.delta_times)
    
    def get_frame_time_ms(self) -> float:
        """Get current frame time in milliseconds."""
        if not self.delta_times:
            return 0.0
        return self.delta_times[-1] * 1000.0


class InputHelper:
    """Helper functions for input handling."""
    
    @staticmethod
    def get_horizontal_input() -> float:
        """Get horizontal input from keyboard (-1 to 1)."""
        keys = pygame.key.get_pressed()
        horizontal = 0.0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            horizontal -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            horizontal += 1.0
            
        return horizontal
    
    @staticmethod
    def get_jump_input() -> bool:
        """Get jump input from keyboard."""
        keys = pygame.key.get_pressed()
        return keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
    
    @staticmethod
    def get_crouch_input() -> bool:
        """Get crouch input from keyboard."""
        keys = pygame.key.get_pressed()
        return keys[pygame.K_s] or keys[pygame.K_DOWN]


class GameConfig:
    """Game configuration constants."""
    
    # Window settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    TARGET_FPS = 60
    GAME_TITLE = "Ingushetia 2D Platformer"
    
    # Player settings
    PLAYER_SIZE = (48, 72)
    PLAYER_START_POS = (640, 100)
    
    # Physics settings
    GRAVITY = 980.0
    JUMP_FORCE = 400.0
    MOVE_SPEED = 200.0
    
    # Animation settings
    WALK_ANIMATION_SPEED = 8.0
    
    # Debug settings
    SHOW_DEBUG_INFO = True
    SHOW_FPS = True