#!/usr/bin/env python3
"""
Test player visibility and collision handling
"""

import pygame
from game.physics import Vector2D
from game.player import Player
from game.platform import PlatformManager
from game.collision import CollisionSystem


def test_player_stays_visible():
    """Test that player doesn't disappear after collision."""
    print("Testing player visibility after collision...")
    
    collision_system = CollisionSystem()
    platform_manager = PlatformManager()
    
    # Create player
    player = Player(Vector2D(200, 100))
    collision_system.add_collider(player.collider)
    
    # Create platform below player
    platform = platform_manager.add_platform(Vector2D(200, 200), Vector2D(150, 30))
    collision_system.add_collider(platform.collider)
    
    print(f"Initial player position: {player.get_position()}")
    print(f"Platform position: {platform.position}")
    
    # Let player fall and collide
    for i in range(120):  # 2 seconds
        player.update(1.0 / 60.0)
        collision_system.update(1.0 / 60.0)
        
        # Check player is still in reasonable bounds
        pos = player.get_position()
        assert -200 < pos.x < 2200, f"Player X out of bounds: {pos.x}"
        assert -600 < pos.y < 1100, f"Player Y out of bounds: {pos.y}"
        
        if player.is_grounded:
            print(f"Player landed after {i+1} frames at {pos}")
            break
    
    final_pos = player.get_position()
    print(f"Final player position: {final_pos}")
    
    # Player should be near the platform
    assert abs(final_pos.x - 200) < 100, f"Player X too far from platform: {final_pos.x}"
    assert abs(final_pos.y - 170) < 50, f"Player Y not on platform: {final_pos.y}"
    
    print("✓ Player visibility test passed")


def test_player_collision_stability():
    """Test that player collision doesn't cause extreme movements."""
    print("Testing collision stability...")
    
    collision_system = CollisionSystem()
    platform_manager = PlatformManager()
    
    # Create player on platform
    player = Player(Vector2D(200, 170))
    player.is_grounded = True
    collision_system.add_collider(player.collider)
    
    # Create platform
    platform = platform_manager.add_platform(Vector2D(200, 200), Vector2D(150, 30))
    collision_system.add_collider(platform.collider)
    
    initial_pos = player.get_position()
    
    # Update for several frames
    for i in range(30):
        player.update(1.0 / 60.0)
        collision_system.update(1.0 / 60.0)
        
        pos = player.get_position()
        
        # Player shouldn't move too far from initial position
        distance_moved = abs(pos.x - initial_pos.x) + abs(pos.y - initial_pos.y)
        assert distance_moved < 100, f"Player moved too far: {distance_moved} pixels"
    
    print("✓ Collision stability test passed")


def test_multiple_platform_collisions():
    """Test player with multiple platforms."""
    print("Testing multiple platform collisions...")
    
    collision_system = CollisionSystem()
    platform_manager = PlatformManager()
    
    # Create player
    player = Player(Vector2D(200, 50))
    collision_system.add_collider(player.collider)
    
    # Create multiple platforms
    platforms = [
        (200, 150, 100, 20),
        (300, 200, 100, 20),
        (100, 250, 100, 20),
    ]
    
    for x, y, w, h in platforms:
        platform = platform_manager.add_platform(Vector2D(x, y), Vector2D(w, h))
        collision_system.add_collider(platform.collider)
    
    # Update for many frames
    for i in range(180):  # 3 seconds
        player.update(1.0 / 60.0)
        collision_system.update(1.0 / 60.0)
        
        pos = player.get_position()
        
        # Player should stay in reasonable bounds
        assert -100 < pos.x < 500, f"Player X out of bounds: {pos.x}"
        assert -100 < pos.y < 400, f"Player Y out of bounds: {pos.y}"
    
    print("✓ Multiple platform collision test passed")


def run_all_tests():
    """Run all player visibility tests."""
    print("Running player visibility tests...\n")
    
    try:
        test_player_stays_visible()
        test_player_collision_stability()
        test_multiple_platform_collisions()
        
        print("\n✅ All player visibility tests passed!")
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