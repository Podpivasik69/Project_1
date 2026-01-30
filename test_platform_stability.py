#!/usr/bin/env python3
"""
Test platform stability (platforms shouldn't fall)
"""

import pygame
from game.physics import Vector2D, PhysicsBody
from game.collision import CollisionSystem, Collider, CollisionLayer


def test_platform_stability():
    """Test that platforms don't fall due to gravity."""
    print("Testing platform stability...")
    
    collision_system = CollisionSystem()
    
    # Create platform with gravity_scale=0
    platform_body = PhysicsBody(
        position=Vector2D(200, 200),
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero(),
        mass=1000.0,
        gravity_scale=0.0  # Should not be affected by gravity
    )
    platform_collider = Collider(
        physics_body=platform_body,
        size=Vector2D(100, 20),
        layer=CollisionLayer.PLATFORM
    )
    collision_system.add_collider(platform_collider)
    
    initial_position = Vector2D(platform_body.position.x, platform_body.position.y)
    
    # Update collision system for several frames
    for i in range(60):  # 1 second at 60 FPS
        collision_system.update(1.0 / 60.0)
    
    final_position = platform_body.position
    
    print(f"Initial position: {initial_position}")
    print(f"Final position: {final_position}")
    print(f"Position change: {final_position.y - initial_position.y}")
    
    # Platform should not have moved significantly
    position_change = abs(final_position.y - initial_position.y)
    assert position_change < 1.0, f"Platform moved too much: {position_change} pixels"
    
    print("✓ Platform stability test passed")


def test_player_falls_platform_stays():
    """Test that player falls but platform stays in place."""
    print("Testing player falls, platform stays...")
    
    collision_system = CollisionSystem()
    
    # Create player (should fall)
    from game.player import Player
    player = Player(Vector2D(200, 100))
    collision_system.add_collider(player.collider)
    
    # Create platform (should not fall)
    platform_body = PhysicsBody(
        position=Vector2D(200, 200),
        velocity=Vector2D.zero(),
        acceleration=Vector2D.zero(),
        mass=1000.0,
        gravity_scale=0.0
    )
    platform_collider = Collider(
        physics_body=platform_body,
        size=Vector2D(150, 20),
        layer=CollisionLayer.PLATFORM
    )
    collision_system.add_collider(platform_collider)
    
    initial_player_y = player.get_position().y
    initial_platform_y = platform_body.position.y
    
    # Update for several frames
    for i in range(60):
        player.update(1.0 / 60.0)
        collision_system.update(1.0 / 60.0)
    
    final_player_y = player.get_position().y
    final_platform_y = platform_body.position.y
    
    print(f"Player moved: {final_player_y - initial_player_y:.1f} pixels")
    print(f"Platform moved: {final_platform_y - initial_platform_y:.1f} pixels")
    
    # Player should have fallen down
    assert final_player_y > initial_player_y, "Player should have fallen"
    
    # Platform should not have moved
    platform_movement = abs(final_platform_y - initial_platform_y)
    assert platform_movement < 1.0, f"Platform should not move: {platform_movement}"
    
    print("✓ Player falls, platform stays test passed")


def run_all_tests():
    """Run all platform stability tests."""
    print("Running platform stability tests...\n")
    
    try:
        test_platform_stability()
        test_player_falls_platform_stays()
        
        print("\n✅ All platform stability tests passed!")
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