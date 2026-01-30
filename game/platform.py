"""
Platform Module
Static platforms for the Ingushetia 2D Platformer with texture support
"""

import pygame
from typing import List, Tuple, Optional
from game.physics import Vector2D
from game.collision import Collider, CollisionLayer, PhysicsBody
from game.assets import asset_manager
from game.utils import Colors


class Platform:
    """
    Enhanced platform with texture support and improved rendering.
    Static platform that doesn't move or respond to physics.
    """
    
    def __init__(self, position: Vector2D, size: Vector2D, 
                 platform_type: str = "default", 
                 color: Tuple[int, int, int] = None):
        """
        Initialize platform.
        
        Args:
            position: Platform center position
            size: Platform width and height
            platform_type: Type of platform for texture loading
            color: Fallback color if texture not available
        """
        self.position = position
        self.size = size
        self.platform_type = platform_type
        self.color = color or Colors.PLATFORM_BROWN
        self.border_color = (101, 50, 14)  # Darker brown for border
        
        # Load texture
        self.texture = self._load_texture()
        
        # Create a physics body that never moves
        self.physics_body = PhysicsBody(
            position=Vector2D(position.x, position.y),
            velocity=Vector2D.zero(),
            acceleration=Vector2D.zero(),
            mass=float('inf'),  # Infinite mass - never moves
            gravity_scale=0.0,  # No gravity
            friction=1.0,
            drag=0.0
        )
        
        # Create collider
        self.collider = Collider(
            physics_body=self.physics_body,
            size=size,
            layer=CollisionLayer.PLATFORM,
            is_trigger=False
        )
        
        # Platform should never move
        self._lock_position()
    
    def _load_texture(self) -> Optional[pygame.Surface]:
        """Load platform texture from assets."""
        try:
            texture = asset_manager.get_platform_texture(
                self.platform_type, 
                (int(self.size.x), int(self.size.y))
            )
            return texture
        except Exception as e:
            print(f"Failed to load platform texture '{self.platform_type}': {e}")
            return None
    
    def _lock_position(self) -> None:
        """Lock platform position so it never moves."""
        # Override physics body methods to prevent movement
        original_integrate = self.physics_body.integrate
        original_apply_force = self.physics_body.apply_force
        original_apply_impulse = self.physics_body.apply_impulse
        
        def locked_integrate(delta_time, gravity=None):
            # Do nothing - platform never moves
            pass
        
        def locked_apply_force(force):
            # Do nothing - platform never moves
            pass
        
        def locked_apply_impulse(impulse):
            # Do nothing - platform never moves
            pass
        
        self.physics_body.integrate = locked_integrate
        self.physics_body.apply_force = locked_apply_force
        self.physics_body.apply_impulse = locked_apply_impulse
    
    def get_rect(self) -> pygame.Rect:
        """Get platform rectangle for rendering."""
        return pygame.Rect(
            self.position.x - self.size.x / 2,
            self.position.y - self.size.y / 2,
            self.size.x,
            self.size.y
        )
    
    def render(self, surface: pygame.Surface, camera_offset: Vector2D = None) -> None:
        """
        Render the platform with texture support.
        
        Args:
            surface: Surface to render on
            camera_offset: Camera offset for world-to-screen conversion
        """
        if camera_offset is None:
            camera_offset = Vector2D.zero()
        
        # Calculate screen position
        screen_pos = self.position - camera_offset
        
        # Create platform rectangle
        platform_rect = pygame.Rect(
            screen_pos.x - self.size.x / 2,
            screen_pos.y - self.size.y / 2,
            self.size.x,
            self.size.y
        )
        
        # Render with texture if available, otherwise use colored rectangle
        if self.texture:
            surface.blit(self.texture, platform_rect)
        else:
            # Draw platform with gradient effect
            self._draw_gradient_rect(surface, platform_rect, self.color, self.border_color)
            
            # Draw border
            pygame.draw.rect(surface, self.border_color, platform_rect, 2)
            
            # Add some texture lines
            self._draw_texture_lines(surface, platform_rect)
    
    def _draw_gradient_rect(self, surface: pygame.Surface, rect: pygame.Rect, 
                           color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> None:
        """Draw a rectangle with vertical gradient."""
        # Simple gradient by drawing horizontal lines with interpolated colors
        for y in range(rect.height):
            # Interpolate between color1 and color2
            ratio = y / rect.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            line_color = (r, g, b)
            pygame.draw.line(surface, line_color, 
                           (rect.left, rect.top + y), 
                           (rect.right, rect.top + y))
    
    def _draw_texture_lines(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw texture lines on platform for fallback rendering."""
        # Draw some horizontal lines for wood texture
        line_color = (80, 40, 10)
        
        # Draw a few horizontal lines
        for i in range(2, rect.height - 2, 6):
            pygame.draw.line(surface, line_color,
                           (rect.left + 5, rect.top + i),
                           (rect.right - 5, rect.top + i), 1)


class PlatformManager:
    """
    Enhanced platform manager with improved level generation.
    """
    
    def __init__(self):
        self.platforms: List[Platform] = []
    
    def add_platform(self, position: Vector2D, size: Vector2D, 
                    platform_type: str = "default",
                    color: Tuple[int, int, int] = None) -> Platform:
        """
        Add a platform to the manager.
        
        Args:
            position: Platform position
            size: Platform size
            platform_type: Type of platform for texture loading
            color: Platform color (optional)
            
        Returns:
            Created platform
        """
        platform = Platform(position, size, platform_type, color)
        self.platforms.append(platform)
        return platform
    
    def get_colliders(self) -> List[Collider]:
        """Get all platform colliders for collision system."""
        return [platform.collider for platform in self.platforms]
    
    def render_all(self, surface: pygame.Surface, camera_offset: Vector2D = None) -> None:
        """Render all platforms."""
        for platform in self.platforms:
            platform.render(surface, camera_offset)
    
    def clear(self) -> None:
        """Remove all platforms."""
        self.platforms.clear()
    
    def create_test_level(self, window_width: int, window_height: int) -> None:
        """Create an enhanced test level with varied platform types."""
        self.clear()
        
        # Ground platform - main foundation
        self.add_platform(
            Vector2D(window_width // 2, window_height - 40),
            Vector2D(window_width - 100, 30),
            "ground",
            (101, 67, 33)  # Dark brown for ground
        )
        
        # Left side platforms - ascending
        self.add_platform(
            Vector2D(200, window_height - 150),
            Vector2D(120, 25),
            "wood",
            (139, 69, 19)  # Medium brown
        )
        
        self.add_platform(
            Vector2D(150, window_height - 300),
            Vector2D(100, 20),
            "stone",
            (160, 82, 45)  # Light brown
        )
        
        # Right side platforms - ascending
        self.add_platform(
            Vector2D(window_width - 200, window_height - 150),
            Vector2D(120, 25),
            "wood",
            (139, 69, 19)
        )
        
        self.add_platform(
            Vector2D(window_width - 150, window_height - 300),
            Vector2D(100, 20),
            "stone",
            (160, 82, 45)
        )
        
        # Center platforms - main path
        self.add_platform(
            Vector2D(window_width // 2, window_height - 250),
            Vector2D(150, 25),
            "wood",
            (139, 69, 19)
        )
        
        # Upper platforms - challenging jumps
        self.add_platform(
            Vector2D(window_width // 2 - 100, window_height - 400),
            Vector2D(80, 20),
            "stone",
            (160, 82, 45)
        )
        
        self.add_platform(
            Vector2D(window_width // 2 + 100, window_height - 400),
            Vector2D(80, 20),
            "stone",
            (160, 82, 45)
        )
        
        # High platform - goal area
        self.add_platform(
            Vector2D(window_width // 2, window_height - 500),
            Vector2D(120, 25),
            "special",
            (180, 120, 60)  # Golden brown for special platform
        )
        
        print(f"Created test level with {len(self.platforms)} platforms")