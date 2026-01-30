"""
Physics Module
Mathematical and physics utilities for the Ingushetia 2D Platformer
"""

import math
from dataclasses import dataclass
from typing import Tuple, Optional
import pygame


class Vector2D:
    """
    2D vector class with mathematical operations for physics calculations.
    """
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y
    
    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        """Vector addition."""
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        """Vector subtraction."""
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector2D':
        """Scalar multiplication."""
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar: float) -> 'Vector2D':
        """Reverse scalar multiplication."""
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> 'Vector2D':
        """Scalar division."""
        if scalar == 0:
            raise ValueError("Cannot divide vector by zero")
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def __eq__(self, other: 'Vector2D') -> bool:
        """Vector equality comparison."""
        return abs(self.x - other.x) < 1e-6 and abs(self.y - other.y) < 1e-6
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"
    
    def magnitude(self) -> float:
        """Calculate vector magnitude (length)."""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def magnitude_squared(self) -> float:
        """Calculate squared magnitude (faster than magnitude for comparisons)."""
        return self.x * self.x + self.y * self.y
    
    def normalize(self) -> 'Vector2D':
        """
        Return normalized vector (unit vector in same direction).
        Returns zero vector if magnitude is zero.
        """
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)
    
    def dot(self, other: 'Vector2D') -> float:
        """Calculate dot product with another vector."""
        return self.x * other.x + self.y * other.y
    
    def cross(self, other: 'Vector2D') -> float:
        """Calculate 2D cross product (returns scalar)."""
        return self.x * other.y - self.y * other.x
    
    def distance_to(self, other: 'Vector2D') -> float:
        """Calculate distance to another vector."""
        return (self - other).magnitude()
    
    def lerp(self, other: 'Vector2D', t: float) -> 'Vector2D':
        """Linear interpolation between this vector and another."""
        t = max(0.0, min(1.0, t))  # Clamp t to [0, 1]
        return self + (other - self) * t
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple."""
        return (self.x, self.y)
    
    def to_int_tuple(self) -> Tuple[int, int]:
        """Convert to integer tuple (for pygame coordinates)."""
        return (int(self.x), int(self.y))
    
    @classmethod
    def from_tuple(cls, t: Tuple[float, float]) -> 'Vector2D':
        """Create vector from tuple."""
        return cls(t[0], t[1])
    
    @classmethod
    def zero(cls) -> 'Vector2D':
        """Create zero vector."""
        return cls(0, 0)
    
    @classmethod
    def one(cls) -> 'Vector2D':
        """Create unit vector (1, 1)."""
        return cls(1, 1)
    
    @classmethod
    def up(cls) -> 'Vector2D':
        """Create up vector (0, -1) - negative Y is up in screen coordinates."""
        return cls(0, -1)
    
    @classmethod
    def down(cls) -> 'Vector2D':
        """Create down vector (0, 1)."""
        return cls(0, 1)
    
    @classmethod
    def left(cls) -> 'Vector2D':
        """Create left vector (-1, 0)."""
        return cls(-1, 0)
    
    @classmethod
    def right(cls) -> 'Vector2D':
        """Create right vector (1, 0)."""
        return cls(1, 0)


@dataclass
class PhysicsBody:
    """
    Physics component for game objects with position, velocity, and physical properties.
    """
    position: Vector2D
    velocity: Vector2D
    acceleration: Vector2D
    mass: float = 1.0
    friction: float = 0.8
    restitution: float = 0.0  # Bounciness (0 = no bounce, 1 = perfect bounce)
    drag: float = 0.01  # Air resistance
    gravity_scale: float = 1.0  # Multiplier for gravity effect
    is_static: bool = False  # Static objects don't move
    
    def __post_init__(self):
        """Initialize default vectors if None provided."""
        if self.position is None:
            self.position = Vector2D.zero()
        if self.velocity is None:
            self.velocity = Vector2D.zero()
        if self.acceleration is None:
            self.acceleration = Vector2D.zero()
    
    def apply_force(self, force: Vector2D) -> None:
        """
        Apply force to the physics body (F = ma, so a = F/m).
        
        Args:
            force: Force vector to apply
        """
        self.acceleration = self.acceleration + (force / self.mass)
    
    def apply_impulse(self, impulse: Vector2D) -> None:
        """
        Apply instantaneous impulse to velocity.
        
        Args:
            impulse: Impulse vector to apply
        """
        self.velocity = self.velocity + (impulse / self.mass)
    
    def integrate(self, delta_time: float, gravity: Vector2D = None) -> None:
        """
        Integrate physics using Verlet integration for stability.
        
        Args:
            delta_time: Time step in seconds
            gravity: Gravity vector to apply
        """
        # Only apply gravity if gravity_scale > 0
        if gravity and self.gravity_scale > 0:
            gravity_force = gravity * self.gravity_scale * self.mass
            self.apply_force(gravity_force)
        
        # Apply drag
        drag_force = self.velocity * (-self.drag * self.velocity.magnitude())
        self.apply_force(drag_force)
        
        # Verlet integration
        old_position = Vector2D(self.position.x, self.position.y)
        
        # Update position: x = x + v*dt + 0.5*a*dt^2
        self.position = self.position + self.velocity * delta_time + self.acceleration * (0.5 * delta_time * delta_time)
        
        # Update velocity: v = v + a*dt
        self.velocity = self.velocity + self.acceleration * delta_time
        
        # Reset acceleration for next frame
        self.acceleration = Vector2D.zero()
    
    def get_bounds(self, size: Vector2D) -> pygame.Rect:
        """
        Get bounding rectangle for collision detection.
        
        Args:
            size: Size of the object
            
        Returns:
            pygame.Rect representing the bounds
        """
        return pygame.Rect(
            self.position.x - size.x / 2,
            self.position.y - size.y / 2,
            size.x,
            size.y
        )


@dataclass
class CollisionData:
    """
    Data structure containing collision information.
    """
    other_body: PhysicsBody
    collision_point: Vector2D
    collision_normal: Vector2D  # Unit vector pointing away from collision
    penetration_depth: float
    collision_side: str  # "top", "bottom", "left", "right"
    
    def __post_init__(self):
        """Ensure collision normal is normalized."""
        if self.collision_normal.magnitude() > 0:
            self.collision_normal = self.collision_normal.normalize()


class PhysicsUtils:
    """
    Utility functions for physics calculations and collision detection.
    """
    
    @staticmethod
    def aabb_collision(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """
        Check if two axis-aligned bounding boxes (AABB) are colliding.
        
        Args:
            rect1: First rectangle
            rect2: Second rectangle
            
        Returns:
            True if rectangles are overlapping
        """
        return rect1.colliderect(rect2)
    
    @staticmethod
    def aabb_collision_data(rect1: pygame.Rect, rect2: pygame.Rect, body1: PhysicsBody, body2: PhysicsBody) -> Optional[CollisionData]:
        """
        Get detailed collision data for two AABB rectangles.
        
        Args:
            rect1: First rectangle
            rect2: Second rectangle  
            body1: First physics body
            body2: Second physics body
            
        Returns:
            CollisionData if collision exists, None otherwise
        """
        if not rect1.colliderect(rect2):
            return None
        
        # Calculate overlap amounts
        overlap_x = min(rect1.right, rect2.right) - max(rect1.left, rect2.left)
        overlap_y = min(rect1.bottom, rect2.bottom) - max(rect1.top, rect2.top)
        
        # Determine collision side and normal based on smallest overlap
        if overlap_x < overlap_y:
            # Horizontal collision
            if rect1.centerx < rect2.centerx:
                # rect1 is to the left of rect2
                normal = Vector2D(-1, 0)
                side = "right"
                collision_point = Vector2D(rect1.right, rect1.centery)
            else:
                # rect1 is to the right of rect2
                normal = Vector2D(1, 0)
                side = "left"
                collision_point = Vector2D(rect1.left, rect1.centery)
            penetration = overlap_x
        else:
            # Vertical collision
            if rect1.centery < rect2.centery:
                # rect1 is above rect2
                normal = Vector2D(0, -1)
                side = "bottom"
                collision_point = Vector2D(rect1.centerx, rect1.bottom)
            else:
                # rect1 is below rect2
                normal = Vector2D(0, 1)
                side = "top"
                collision_point = Vector2D(rect1.centerx, rect1.top)
            penetration = overlap_y
        
        return CollisionData(
            other_body=body2,
            collision_point=collision_point,
            collision_normal=normal,
            penetration_depth=penetration,
            collision_side=side
        )
    
    @staticmethod
    def resolve_collision(body1: PhysicsBody, body2: PhysicsBody, collision: CollisionData) -> None:
        """
        Resolve collision between two physics bodies.
        
        Args:
            body1: First physics body
            body2: Second physics body
            collision: Collision data
        """
        # Don't resolve collision if one body has infinite mass (static platforms)
        if body1.mass == float('inf') and body2.mass == float('inf'):
            return
        
        # Separate objects based on penetration
        separation = collision.collision_normal * collision.penetration_depth
        
        if body1.mass == float('inf'):
            # body1 is static (platform), only move body2 (player)
            body2.position = body2.position - separation
        elif body2.mass == float('inf'):
            # body2 is static (platform), only move body1 (player)
            body1.position = body1.position + separation
        else:
            # Both bodies can move
            total_mass = body1.mass + body2.mass
            body1_separation = separation * (body2.mass / total_mass)
            body2_separation = separation * (-body1.mass / total_mass)
            
            body1.position = body1.position + body1_separation
            body2.position = body2.position + body2_separation
        
        # Calculate relative velocity
        relative_velocity = body1.velocity - body2.velocity
        velocity_along_normal = relative_velocity.dot(collision.collision_normal)
        
        # Don't resolve if velocities are separating
        if velocity_along_normal > 0:
            return
        
        # Calculate restitution
        restitution = min(body1.restitution, body2.restitution)
        
        # Calculate impulse scalar
        impulse_scalar = -(1 + restitution) * velocity_along_normal
        
        if body1.mass == float('inf') and body2.mass != float('inf'):
            # Only body2 can move
            impulse = collision.collision_normal * impulse_scalar
            body2.velocity = body2.velocity - impulse
        elif body2.mass == float('inf') and body1.mass != float('inf'):
            # Only body1 can move
            impulse = collision.collision_normal * impulse_scalar
            body1.velocity = body1.velocity + impulse
        elif body1.mass != float('inf') and body2.mass != float('inf'):
            # Both bodies can move
            impulse_scalar /= (1 / body1.mass + 1 / body2.mass)
            impulse = collision.collision_normal * impulse_scalar
            body1.velocity = body1.velocity + impulse / body1.mass
            body2.velocity = body2.velocity - impulse / body2.mass
        
        # Apply friction only if there's relative motion
        if body1.mass != float('inf') or body2.mass != float('inf'):
            tangent = relative_velocity - collision.collision_normal * velocity_along_normal
            if tangent.magnitude() > 0.01:  # Avoid division by very small numbers
                tangent = tangent.normalize()
                
                friction_impulse = tangent * impulse_scalar * min(body1.friction, body2.friction) * 0.1
                
                if body1.mass != float('inf'):
                    body1.velocity = body1.velocity - friction_impulse / body1.mass
                if body2.mass != float('inf'):
                    body2.velocity = body2.velocity + friction_impulse / body2.mass