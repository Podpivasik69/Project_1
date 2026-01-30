#!/usr/bin/env python3
"""
Tests for collision detection system
"""

import pygame
from game.physics import Vector2D, PhysicsBody
from game.collision import Collider, CollisionSystem, CollisionLayer


def test_collision_layers():
    """Test collision layer system."""
    print("Testing collision layers...")
    
    # Player should collide with platforms
    assert CollisionLayer.can_collide(CollisionLayer.PLAYER, CollisionLayer.PLATFORM)
    assert CollisionLayer.can_collide(CollisionLayer.PLATFORM, CollisionLayer.PLAYER)
    
    # Pickups should only collide with player
    assert CollisionLayer.can_collide(CollisionLayer.PICKUP, CollisionLayer.PLAYER)
    assert not CollisionLayer.can_collide(CollisionLayer.PICKUP, CollisionLayer.PLATFORM)
    
    print("✓ Collision layers test passed")


def test_collider_creation():
    """Test collider creation and basic functionality."""
    print("Testing collider creation...")
    
    # Create physics body
    body = PhysicsBody(
        position=Vector2D(100, 100),
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero()
    )
    
    # Create collider
    collider = Collider(
        physics_body=body,
        size=Vector2D(50, 50),
        layer=CollisionLayer.PLAYER
    )
    
    # Test bounds calculation
    bounds = collider.get_bounds()
    assert bounds.width == 50 and bounds.height == 50
    assert bounds.centerx == 100 and bounds.centery == 100
    
    print("✓ Collider creation test passed")


def test_collision_system():
    """Test collision system functionality."""
    print("Testing collision system...")
    
    # Create collision system
    collision_system = CollisionSystem()
    
    # Create two colliders
    body1 = PhysicsBody(
        position=Vector2D(100, 100),
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero()
    )
    collider1 = Collider(body1, Vector2D(50, 50), CollisionLayer.PLAYER)
    
    body2 = PhysicsBody(
        position=Vector2D(120, 100),  # Overlapping with first collider
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero()
    )
    collider2 = Collider(body2, Vector2D(50, 50), CollisionLayer.PLATFORM)
    
    # Add colliders to system
    collision_system.add_collider(collider1)
    collision_system.add_collider(collider2)
    
    # Test collision detection
    collision = collision_system.check_collision(collider1, collider2)
    assert collision is not None, "Collision should be detected"
    
    # Test non-overlapping colliders
    body3 = PhysicsBody(
        position=Vector2D(200, 200),  # Far away
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero()
    )
    collider3 = Collider(body3, Vector2D(50, 50), CollisionLayer.PLATFORM)
    
    no_collision = collision_system.check_collision(collider1, collider3)
    assert no_collision is None, "No collision should be detected"
    
    print("✓ Collision system test passed")


def test_collision_resolution():
    """Test collision resolution."""
    print("Testing collision resolution...")
    
    collision_system = CollisionSystem()
    
    # Create overlapping colliders
    body1 = PhysicsBody(
        position=Vector2D(100, 100),
        velocity=Vector2D(10, 0),  # Moving right
        acceleration=Vector2D.zero(),
        mass=1.0
    )
    collider1 = Collider(body1, Vector2D(50, 50), CollisionLayer.PLAYER)
    
    body2 = PhysicsBody(
        position=Vector2D(120, 100),  # Overlapping
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero(),
        mass=1000.0  # Heavy platform (shouldn't move much)
    )
    collider2 = Collider(body2, Vector2D(50, 50), CollisionLayer.PLATFORM)
    
    collision_system.add_collider(collider1)
    collision_system.add_collider(collider2)
    
    # Store initial positions
    initial_pos1 = Vector2D(body1.position.x, body1.position.y)
    initial_pos2 = Vector2D(body2.position.x, body2.position.y)
    
    # Update system (should resolve collision)
    collision_system.update(0.016)  # ~60 FPS
    
    # Player should have moved more than platform due to mass difference
    player_moved = abs(body1.position.x - initial_pos1.x)
    platform_moved = abs(body2.position.x - initial_pos2.x)
    
    assert player_moved > platform_moved, f"Player should move more: {player_moved} vs {platform_moved}"
    
    print("✓ Collision resolution test passed")


def test_raycast():
    """Test raycast functionality."""
    print("Testing raycast...")
    
    collision_system = CollisionSystem()
    
    # Create a platform
    body = PhysicsBody(
        position=Vector2D(200, 200),
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero()
    )
    collider = Collider(body, Vector2D(100, 50), CollisionLayer.PLATFORM)
    collision_system.add_collider(collider)
    
    # Cast ray from left to right
    start = Vector2D(50, 200)
    direction = Vector2D.right()
    
    hit = collision_system.raycast(start, direction, 300)
    assert hit is not None, "Raycast should hit the platform"
    
    hit_collider, hit_point, distance = hit
    assert hit_collider == collider, "Should hit the correct collider"
    assert distance > 0, f"Distance should be positive: {distance}"
    
    # Cast ray that misses
    start_miss = Vector2D(50, 50)
    hit_miss = collision_system.raycast(start_miss, direction, 300)
    assert hit_miss is None, "Raycast should miss"
    
    print("✓ Raycast test passed")


def run_all_tests():
    """Run all collision tests."""
    print("Running collision system tests...\n")
    
    try:
        test_collision_layers()
        test_collider_creation()
        test_collision_system()
        test_collision_resolution()
        test_raycast()
        
        print("\n✅ All collision tests passed!")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    pygame.init()
    
    success = run_all_tests()
    
    pygame.quit()
    
    if not success:
        exit(1)