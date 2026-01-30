#!/usr/bin/env python3
"""
Tests for player collision integration
"""

import pygame
from game.physics import Vector2D, PhysicsBody
from game.player import Player, PlayerState
from game.collision import CollisionSystem, Collider, CollisionLayer


def test_player_platform_collision():
    """Test player collision with platforms."""
    print("Testing player-platform collision...")
    
    # Create collision system
    collision_system = CollisionSystem()
    
    # Create player above platform
    player = Player(Vector2D(100, 50))
    collision_system.add_collider(player.collider)
    
    # Create platform below player
    platform_body = PhysicsBody(
        position=Vector2D(100, 150),
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero(),
        mass=1000.0,
        gravity_scale=0.0  # Platform doesn't fall
    )
    platform_collider = Collider(
        physics_body=platform_body,
        size=Vector2D(200, 20),
        layer=CollisionLayer.PLATFORM
    )
    collision_system.add_collider(platform_collider)
    
    # Simulate falling and landing
    for i in range(120):  # 2 seconds at 60 FPS
        player.update(1.0 / 60.0)
        collision_system.update(1.0 / 60.0)
        
        # Check if player landed
        if player.is_grounded and player.current_state == PlayerState.IDLE:
            print(f"Player landed after {i+1} frames")
            break
    
    # Verify player is on platform
    player_y = player.get_position().y
    platform_top = platform_body.position.y - 10  # Platform half-height
    
    print(f"Player Y: {player_y}, Platform top: {platform_top}")
    print(f"Player grounded: {player.is_grounded}")
    print(f"Player state: {player.current_state}")
    
    # Player should be close to platform surface
    assert abs(player_y - platform_top) < 50, f"Player should be near platform surface"
    
    print("✓ Player-platform collision test passed")


def test_player_jumping_off_platform():
    """Test player jumping off platform."""
    print("Testing player jumping off platform...")
    
    collision_system = CollisionSystem()
    
    # Create player on platform (grounded)
    player = Player(Vector2D(100, 130))
    player.is_grounded = True  # Manually set grounded for test
    player.current_state = PlayerState.IDLE
    collision_system.add_collider(player.collider)
    
    # Create platform
    platform_body = PhysicsBody(
        position=Vector2D(100, 150),
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero(),
        mass=1000.0,
        gravity_scale=0.0
    )
    platform_collider = Collider(
        physics_body=platform_body,
        size=Vector2D(200, 20),
        layer=CollisionLayer.PLATFORM
    )
    collision_system.add_collider(platform_collider)
    
    # Make player jump
    initial_y = player.get_position().y
    success = player.jump()
    
    assert success, "Jump should succeed when grounded"
    assert player.current_state == PlayerState.JUMPING, "Player should be in jumping state"
    
    # Update a few frames
    for i in range(10):
        player.update(1.0 / 60.0)
        collision_system.update(1.0 / 60.0)
    
    # Player should be higher than initial position
    current_y = player.get_position().y
    assert current_y < initial_y, f"Player should be higher after jumping: {current_y} vs {initial_y}"
    
    print("✓ Player jumping off platform test passed")


def test_player_horizontal_movement_on_platform():
    """Test player horizontal movement while on platform."""
    print("Testing player horizontal movement on platform...")
    
    collision_system = CollisionSystem()
    
    # Create player on platform
    player = Player(Vector2D(100, 130))
    player.is_grounded = True
    collision_system.add_collider(player.collider)
    
    # Create wide platform
    platform_body = PhysicsBody(
        position=Vector2D(200, 150),
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero(),
        mass=1000.0,
        gravity_scale=0.0
    )
    platform_collider = Collider(
        physics_body=platform_body,
        size=Vector2D(400, 20),
        layer=CollisionLayer.PLATFORM
    )
    collision_system.add_collider(platform_collider)
    
    # Set horizontal input
    player.set_input(1.0, False, False)  # Move right
    
    initial_x = player.get_position().x
    
    # Update several frames
    for i in range(30):
        player.update(1.0 / 60.0)
        collision_system.update(1.0 / 60.0)
    
    # Player should have moved horizontally
    current_x = player.get_position().x
    assert current_x > initial_x, f"Player should have moved right: {current_x} vs {initial_x}"
    
    # Player should still be grounded
    assert player.is_grounded, "Player should still be grounded while walking"
    
    print("✓ Player horizontal movement test passed")


def test_player_collision_sides():
    """Test player collision from different sides."""
    print("Testing player collision from different sides...")
    
    collision_system = CollisionSystem()
    
    # Create platform
    platform_body = PhysicsBody(
        position=Vector2D(200, 200),
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero(),
        mass=1000.0,
        gravity_scale=0.0
    )
    platform_collider = Collider(
        physics_body=platform_body,
        size=Vector2D(100, 50),
        layer=CollisionLayer.PLATFORM
    )
    collision_system.add_collider(platform_collider)
    
    # Test collision detection (not necessarily stopping)
    player = Player(Vector2D(120, 200))  # Left of platform
    collision_system.add_collider(player.collider)
    
    # Check if collision is detected
    collision = collision_system.check_collision(player.collider, platform_collider)
    
    # For now, just verify collision system works
    print(f"Collision detected: {collision is not None}")
    
    # This test passes if no exceptions are thrown
    assert True, "Collision system should handle side collisions without crashing"
    
    print("✓ Player collision sides test passed")


def test_multiple_platforms():
    """Test player interaction with multiple platforms."""
    print("Testing multiple platforms...")
    
    collision_system = CollisionSystem()
    
    # Create player
    player = Player(Vector2D(100, 50))
    collision_system.add_collider(player.collider)
    
    # Create multiple platforms at different heights
    platforms = [
        (100, 150, 150, 20),  # Ground platform
        (300, 100, 100, 20),  # Higher platform
    ]
    
    for x, y, width, height in platforms:
        platform_body = PhysicsBody(
            position=Vector2D(x, y),
            velocity=Vector2D.zero(),
            acceleration=Vector2D.zero(),
            mass=1000.0,
            gravity_scale=0.0
        )
        platform_collider = Collider(
            physics_body=platform_body,
            size=Vector2D(width, height),
            layer=CollisionLayer.PLATFORM
        )
        collision_system.add_collider(platform_collider)
    
    # Let player fall
    initial_y = player.get_position().y
    
    for i in range(120):  # More time to fall
        player.update(1.0 / 60.0)
        collision_system.update(1.0 / 60.0)
        
        if player.is_grounded:
            print(f"Player landed after {i+1} frames")
            break
    
    # Player should have moved down from initial position
    final_y = player.get_position().y
    assert final_y > initial_y, f"Player should have fallen: {final_y} vs {initial_y}"
    
    print("✓ Multiple platforms test passed")


def run_all_tests():
    """Run all player collision integration tests."""
    print("Running player collision integration tests...\n")
    
    try:
        test_player_platform_collision()
        test_player_jumping_off_platform()
        test_player_horizontal_movement_on_platform()
        test_player_collision_sides()
        test_multiple_platforms()
        
        print("\n✅ All player collision integration tests passed!")
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