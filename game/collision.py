"""
Collision Detection System
Advanced collision detection and response for the Ingushetia 2D Platformer
"""

from typing import List, Optional, Tuple
import pygame
from game.physics import Vector2D, PhysicsBody, CollisionData, PhysicsUtils


class CollisionLayer:
    """
    Collision layer system for organizing collision groups.
    """
    PLAYER = 1
    PLATFORM = 2
    ENEMY = 4
    PICKUP = 8
    TRIGGER = 16
    
    @staticmethod
    def can_collide(layer1: int, layer2: int) -> bool:
        """
        Check if two collision layers can collide with each other.
        
        Args:
            layer1: First collision layer
            layer2: Second collision layer
            
        Returns:
            True if layers can collide
        """
        # Define collision matrix
        collision_matrix = {
            CollisionLayer.PLAYER: [CollisionLayer.PLATFORM, CollisionLayer.ENEMY, CollisionLayer.PICKUP, CollisionLayer.TRIGGER],
            CollisionLayer.PLATFORM: [CollisionLayer.PLAYER, CollisionLayer.ENEMY],
            CollisionLayer.ENEMY: [CollisionLayer.PLAYER, CollisionLayer.PLATFORM],
            CollisionLayer.PICKUP: [CollisionLayer.PLAYER],
            CollisionLayer.TRIGGER: [CollisionLayer.PLAYER]
        }
        
        return layer2 in collision_matrix.get(layer1, [])


class Collider:
    """
    Collider component that can be attached to game objects.
    """
    
    def __init__(self, physics_body: PhysicsBody, size: Vector2D, layer: int = CollisionLayer.PLATFORM, is_trigger: bool = False):
        self.physics_body = physics_body
        self.size = size
        self.layer = layer
        self.is_trigger = is_trigger  # Triggers don't block movement but generate events
        self.enabled = True
        
        # Collision callbacks
        self.on_collision_enter = None
        self.on_collision_stay = None
        self.on_collision_exit = None
        
        # Track current collisions
        self.current_collisions = set()
    
    def get_bounds(self) -> pygame.Rect:
        """Get the collision bounds as a pygame Rect."""
        return self.physics_body.get_bounds(self.size)
    
    def set_collision_callbacks(self, on_enter=None, on_stay=None, on_exit=None):
        """
        Set collision event callbacks.
        
        Args:
            on_enter: Called when collision starts
            on_stay: Called while collision continues
            on_exit: Called when collision ends
        """
        self.on_collision_enter = on_enter
        self.on_collision_stay = on_stay
        self.on_collision_exit = on_exit


class CollisionSystem:
    """
    Manages collision detection and response for all game objects.
    """
    
    def __init__(self):
        self.colliders: List[Collider] = []
        self.gravity = Vector2D(0, 980)  # Default gravity (pixels/second^2)
        
        # Spatial partitioning for optimization (simple grid)
        self.grid_size = 100
        self.spatial_grid = {}
    
    def add_collider(self, collider: Collider) -> None:
        """Add a collider to the system."""
        if collider not in self.colliders:
            self.colliders.append(collider)
    
    def remove_collider(self, collider: Collider) -> None:
        """Remove a collider from the system."""
        if collider in self.colliders:
            self.colliders.remove(collider)
    
    def _get_grid_key(self, position: Vector2D) -> Tuple[int, int]:
        """Get spatial grid key for a position."""
        return (int(position.x // self.grid_size), int(position.y // self.grid_size))
    
    def _update_spatial_grid(self) -> None:
        """Update spatial partitioning grid."""
        self.spatial_grid.clear()
        
        for collider in self.colliders:
            if not collider.enabled:
                continue
                
            bounds = collider.get_bounds()
            
            # Add collider to all grid cells it overlaps
            min_x = int(bounds.left // self.grid_size)
            max_x = int(bounds.right // self.grid_size)
            min_y = int(bounds.top // self.grid_size)
            max_y = int(bounds.bottom // self.grid_size)
            
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    key = (x, y)
                    if key not in self.spatial_grid:
                        self.spatial_grid[key] = []
                    self.spatial_grid[key].append(collider)
    
    def _get_potential_collisions(self, collider: Collider) -> List[Collider]:
        """Get list of colliders that could potentially collide with the given collider."""
        bounds = collider.get_bounds()
        potential_colliders = set()
        
        # Check all grid cells the collider overlaps
        min_x = int(bounds.left // self.grid_size)
        max_x = int(bounds.right // self.grid_size)
        min_y = int(bounds.top // self.grid_size)
        max_y = int(bounds.bottom // self.grid_size)
        
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                key = (x, y)
                if key in self.spatial_grid:
                    potential_colliders.update(self.spatial_grid[key])
        
        # Remove self and disabled colliders
        potential_colliders.discard(collider)
        return [c for c in potential_colliders if c.enabled]
    
    def check_collision(self, collider1: Collider, collider2: Collider) -> Optional[CollisionData]:
        """
        Check collision between two colliders.
        
        Args:
            collider1: First collider
            collider2: Second collider
            
        Returns:
            CollisionData if collision exists, None otherwise
        """
        if not (collider1.enabled and collider2.enabled):
            return None
        
        if not CollisionLayer.can_collide(collider1.layer, collider2.layer):
            return None
        
        bounds1 = collider1.get_bounds()
        bounds2 = collider2.get_bounds()
        
        return PhysicsUtils.aabb_collision_data(bounds1, bounds2, collider1.physics_body, collider2.physics_body)
    
    def resolve_collision(self, collider1: Collider, collider2: Collider, collision: CollisionData) -> None:
        """
        Resolve collision between two colliders.
        
        Args:
            collider1: First collider
            collider2: Second collider
            collision: Collision data
        """
        # Don't resolve if either is a trigger
        if collider1.is_trigger or collider2.is_trigger:
            return
        
        # Limit penetration depth to prevent extreme corrections
        max_penetration = 50.0  # Maximum pixels to correct in one frame
        if collision.penetration_depth > max_penetration:
            # Scale down the collision normal to limit correction
            collision.penetration_depth = max_penetration
        
        # Use physics utils to resolve the collision
        PhysicsUtils.resolve_collision(collider1.physics_body, collider2.physics_body, collision)
    
    def update(self, delta_time: float) -> None:
        """
        Update collision system - detect collisions and resolve them.
        
        Args:
            delta_time: Time elapsed since last update
        """
        # Update spatial grid
        self._update_spatial_grid()
        
        # Apply gravity to all physics bodies (only if gravity_scale > 0)
        for collider in self.colliders:
            if collider.enabled and collider.physics_body.gravity_scale > 0:
                collider.physics_body.apply_force(self.gravity * collider.physics_body.mass * collider.physics_body.gravity_scale)
        
        # Integrate physics for all bodies
        for collider in self.colliders:
            if collider.enabled:
                collider.physics_body.integrate(delta_time, self.gravity)
        
        # Detect and resolve collisions
        collision_pairs = []
        
        for collider in self.colliders:
            if not collider.enabled:
                continue
            
            potential_colliders = self._get_potential_collisions(collider)
            
            for other_collider in potential_colliders:
                # Avoid duplicate pairs
                if id(collider) >= id(other_collider):
                    continue
                
                collision = self.check_collision(collider, other_collider)
                if collision:
                    collision_pairs.append((collider, other_collider, collision))
        
        # Resolve all collisions
        for collider1, collider2, collision in collision_pairs:
            self.resolve_collision(collider1, collider2, collision)
            
            # Handle collision events
            self._handle_collision_events(collider1, collider2, collision)
            self._handle_collision_events(collider2, collider1, collision)
    
    def _handle_collision_events(self, collider: Collider, other_collider: Collider, collision: CollisionData) -> None:
        """Handle collision events for a collider."""
        other_id = id(other_collider)
        
        if other_id not in collider.current_collisions:
            # New collision
            collider.current_collisions.add(other_id)
            if collider.on_collision_enter:
                collider.on_collision_enter(other_collider, collision)
        else:
            # Ongoing collision
            if collider.on_collision_stay:
                collider.on_collision_stay(other_collider, collision)
    
    def raycast(self, start: Vector2D, direction: Vector2D, max_distance: float, layer_mask: int = None) -> Optional[Tuple[Collider, Vector2D, float]]:
        """
        Cast a ray and return the first collider hit.
        
        Args:
            start: Ray start position
            direction: Ray direction (should be normalized)
            max_distance: Maximum ray distance
            layer_mask: Collision layers to check (None = all layers)
            
        Returns:
            Tuple of (collider, hit_point, distance) if hit, None otherwise
        """
        # Simple raycast implementation using step-by-step checking
        step_size = 5.0  # Pixels per step
        steps = int(max_distance / step_size)
        
        for i in range(steps):
            current_pos = start + direction * (i * step_size)
            
            for collider in self.colliders:
                if not collider.enabled:
                    continue
                
                if layer_mask is not None and not (collider.layer & layer_mask):
                    continue
                
                bounds = collider.get_bounds()
                if bounds.collidepoint(current_pos.to_int_tuple()):
                    distance = i * step_size
                    return (collider, current_pos, distance)
        
        return None
    
    def get_colliders_in_area(self, area: pygame.Rect, layer_mask: int = None) -> List[Collider]:
        """
        Get all colliders in a specific area.
        
        Args:
            area: Rectangle area to check
            layer_mask: Collision layers to include (None = all layers)
            
        Returns:
            List of colliders in the area
        """
        result = []
        
        for collider in self.colliders:
            if not collider.enabled:
                continue
            
            if layer_mask is not None and not (collider.layer & layer_mask):
                continue
            
            if collider.get_bounds().colliderect(area):
                result.append(collider)
        
        return result