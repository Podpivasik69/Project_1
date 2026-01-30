#!/usr/bin/env python3
"""
Test jumping while moving
"""

import pygame
from game.physics import Vector2D, PhysicsBody
from game.player import Player, PlayerState
from game.collision import CollisionSystem, Collider, CollisionLayer


def test_jump_while_moving():
    """Test that player can jump while moving horizontally."""
    print("Testing jump while moving...")
    
    collision_system = CollisionSystem()
    
    # Create player on platform
    player = Player(Vector2D(100, 130))
    player.is_grounded = True
    player.current_state = PlayerState.IDLE
    collision_system.add_collider(player.collider)
    
    # Create platform
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
    
    # Set horizontal movement input
    player.set_input(1.0, False, False)  # Move right
    
    # Update a few frames to get moving
    for i in range(5):
        player.update(1.0 / 60.0)
        collision_system.update(1.0 / 60.0)
    
    print(f"Before jump - Grounded: {player.is_grounded}, State: {player.current_state}")
    print(f"Velocity: {player.physics_body.velocity}")
    print(f"Jump count: {player.jump_count}")
    
    # Player should be moving and grounded
    assert player.is_grounded, "Player should be grounded before jump"
    assert abs(player.physics_body.velocity.x) > 0, "Player should be moving horizontally"
    
    # Now try to jump while moving
    player.set_input(1.0, True, False)  # Move right AND jump
    
    # Update one frame
    player.update(1.0 / 60.0)
    collision_system.update(1.0 / 60.0)
    
    print(f"After jump - Grounded: {player.is_grounded}, State: {player.current_state}")
    print(f"Velocity: {player.physics_body.velocity}")
    print(f"Jump count: {player.jump_count}")
    
    # Player should have jumped
    assert not player.is_grounded, "Player should not be grounded after jump"
    assert player.physics_body.velocity.y < 0, "Player should have upward velocity after jump"
    assert player.current_state == PlayerState.JUMPING, "Player should be in jumping state"
    assert player.jump_count == 1, "Jump count should be 1"
    
    print("✓ Jump while moving test passed")


def test_multiple_jumps_while_moving():
    """Test that player can't double jump (unless allowed)."""
    print("Testing multiple jumps while moving...")
    
    player = Player(Vector2D(100, 100))
    player.is_grounded = True
    
    # First jump should work
    success1 = player.jump()
    assert success1, "First jump should succeed"
    assert player.jump_count == 1, "Jump count should be 1"
    
    # Second jump should fail (single jump only)
    success2 = player.jump()
    assert not success2, "Second jump should fail with single jump limit"
    assert player.jump_count == 1, "Jump count should still be 1"
    
    print("✓ Multiple jumps test passed")


def test_jump_input_while_moving():
    """Test jump input processing while moving."""
    print("Testing jump input while moving...")
    
    player = Player(Vector2D(100, 100))
    player.is_grounded = True
    
    # Set both horizontal and jump input
    player.set_input(1.0, True, False)  # Right + Jump
    
    initial_y = player.physics_body.position.y
    
    # Update player
    player.update(1.0 / 60.0)
    
    # Also integrate physics manually for test
    player.physics_body.integrate(1.0 / 60.0)
    
    # Should have horizontal velocity and upward velocity
    assert abs(player.physics_body.velocity.x) > 0, f"Should have horizontal velocity, got: {player.physics_body.velocity.x}"
    assert player.physics_body.velocity.y < 0, f"Should have upward velocity from jump, got: {player.physics_body.velocity.y}"
    
    print("✓ Jump input while moving test passed")


def run_all_tests():
    """Run all jump while moving tests."""
    print("Running jump while moving tests...\n")
    
    try:
        test_jump_while_moving()
        test_multiple_jumps_while_moving()
        test_jump_input_while_moving()
        
        print("\n✅ All jump while moving tests passed!")
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