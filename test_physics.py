#!/usr/bin/env python3
"""
Simple tests for physics module
"""

from game.physics import Vector2D, PhysicsBody, PhysicsUtils
import pygame


def test_vector2d_basic_operations():
    """Test basic Vector2D operations."""
    print("Testing Vector2D basic operations...")
    
    # Test creation
    v1 = Vector2D(3, 4)
    v2 = Vector2D(1, 2)
    
    # Test addition
    v3 = v1 + v2
    assert v3.x == 4 and v3.y == 6, f"Addition failed: {v3}"
    
    # Test subtraction
    v4 = v1 - v2
    assert v4.x == 2 and v4.y == 2, f"Subtraction failed: {v4}"
    
    # Test scalar multiplication
    v5 = v1 * 2
    assert v5.x == 6 and v5.y == 8, f"Scalar multiplication failed: {v5}"
    
    # Test magnitude
    mag = v1.magnitude()
    expected_mag = 5.0  # sqrt(3^2 + 4^2) = 5
    assert abs(mag - expected_mag) < 1e-6, f"Magnitude failed: {mag} != {expected_mag}"
    
    # Test normalization
    v6 = v1.normalize()
    expected_x, expected_y = 3/5, 4/5
    assert abs(v6.x - expected_x) < 1e-6 and abs(v6.y - expected_y) < 1e-6, f"Normalization failed: {v6}"
    
    print("✓ Vector2D basic operations passed")


def test_vector2d_static_methods():
    """Test Vector2D static methods."""
    print("Testing Vector2D static methods...")
    
    # Test zero vector
    zero = Vector2D.zero()
    assert zero.x == 0 and zero.y == 0, f"Zero vector failed: {zero}"
    
    # Test direction vectors
    up = Vector2D.up()
    assert up.x == 0 and up.y == -1, f"Up vector failed: {up}"
    
    right = Vector2D.right()
    assert right.x == 1 and right.y == 0, f"Right vector failed: {right}"
    
    # Test from_tuple
    v = Vector2D.from_tuple((5, 7))
    assert v.x == 5 and v.y == 7, f"From tuple failed: {v}"
    
    print("✓ Vector2D static methods passed")


def test_physics_body():
    """Test PhysicsBody functionality."""
    print("Testing PhysicsBody...")
    
    # Create physics body
    position = Vector2D(10, 20)
    velocity = Vector2D(5, 0)
    body = PhysicsBody(
        position=position,
        velocity=velocity,
        acceleration=Vector2D.zero(),
        mass=1.0
    )
    
    # Test force application
    force = Vector2D(10, 0)  # 10N force
    body.apply_force(force)
    
    # With mass=1, acceleration should equal force
    assert body.acceleration.x == 10, f"Force application failed: {body.acceleration}"
    
    # Test integration
    dt = 0.1
    old_pos_x = body.position.x
    body.integrate(dt)
    
    # Position should have changed
    assert body.position.x > old_pos_x, f"Integration failed: position didn't change"
    
    print("✓ PhysicsBody tests passed")


def test_collision_detection():
    """Test collision detection utilities."""
    print("Testing collision detection...")
    
    # Create two overlapping rectangles
    rect1 = pygame.Rect(0, 0, 50, 50)
    rect2 = pygame.Rect(25, 25, 50, 50)
    
    # Test basic collision
    collision = PhysicsUtils.aabb_collision(rect1, rect2)
    assert collision, "AABB collision detection failed"
    
    # Test non-overlapping rectangles
    rect3 = pygame.Rect(100, 100, 50, 50)
    no_collision = PhysicsUtils.aabb_collision(rect1, rect3)
    assert not no_collision, "AABB collision false positive"
    
    print("✓ Collision detection tests passed")


def run_all_tests():
    """Run all physics tests."""
    print("Running physics module tests...\n")
    
    try:
        test_vector2d_basic_operations()
        test_vector2d_static_methods()
        test_physics_body()
        test_collision_detection()
        
        print("\n✅ All physics tests passed!")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    # Initialize pygame for rect operations
    pygame.init()
    
    success = run_all_tests()
    
    pygame.quit()
    
    if not success:
        exit(1)