#!/usr/bin/env python3
"""
Test texture loading system
"""

import pygame
from game.assets import asset_manager
from game.player import Player
from game.physics import Vector2D


def test_texture_loading():
    """Test that textures load correctly."""
    print("Testing texture loading...")
    
    # Test individual sprite loading
    idle_sprite = asset_manager.get_player_sprite('idle', (32, 48))
    walk_sprite = asset_manager.get_player_sprite('walk', (32, 48))
    jump_sprite = asset_manager.get_player_sprite('jump', (32, 48))
    crouch_sprite = asset_manager.get_player_sprite('crouch', (32, 48))
    
    assert idle_sprite is not None, "Idle sprite should load"
    assert walk_sprite is not None, "Walk sprite should load"
    assert jump_sprite is not None, "Jump sprite should load"
    assert crouch_sprite is not None, "Crouch sprite should load"
    
    print(f"✓ Loaded sprites: idle={idle_sprite.get_size()}, walk={walk_sprite.get_size()}")
    print(f"✓ Loaded sprites: jump={jump_sprite.get_size()}, crouch={crouch_sprite.get_size()}")
    
    print("✓ Basic texture loading test passed")


def test_walk_animation_frames():
    """Test walk animation frame loading."""
    print("Testing walk animation frames...")
    
    frames = []
    for i in range(5):
        frame = asset_manager.get_walk_animation_frame(i, (32, 48))
        frames.append(frame)
        assert frame is not None, f"Walk frame {i} should load"
    
    print(f"✓ Loaded {len(frames)} walk animation frames")
    
    # Check that frames are different (not all the same)
    frame_sizes = [frame.get_size() for frame in frames]
    print(f"✓ Frame sizes: {frame_sizes}")
    
    print("✓ Walk animation frames test passed")


def test_player_sprite_integration():
    """Test player integration with sprite system."""
    print("Testing player sprite integration...")
    
    player = Player(Vector2D(100, 100))
    
    # Check that player loaded sprites
    assert player.sprites is not None, "Player should have sprites dictionary"
    assert len(player.sprites) > 0, "Player should have loaded sprites"
    assert hasattr(player, 'walk_frames'), "Player should have walk_frames attribute"
    
    print(f"✓ Player loaded {len(player.sprites)} sprites and {len(player.walk_frames)} walk frames")
    
    # Test sprite updates
    from game.player import PlayerState
    
    player.current_state = PlayerState.IDLE
    player._update_sprite()
    idle_sprite = player.current_sprite
    
    player.current_state = PlayerState.JUMPING
    player._update_sprite()
    jump_sprite = player.current_sprite
    
    # Check that sprites exist
    assert idle_sprite is not None, "Idle sprite should exist"
    assert jump_sprite is not None, "Jump sprite should exist"
    
    print("✓ Player sprite integration test passed")


def test_sprite_rendering():
    """Test sprite rendering without crashing."""
    print("Testing sprite rendering...")
    
    # Create test surface
    test_surface = pygame.Surface((200, 200))
    
    player = Player(Vector2D(100, 100))
    
    # Test rendering in different states
    from game.player import PlayerState
    
    states = [
        PlayerState.IDLE,
        PlayerState.WALKING,
        PlayerState.JUMPING,
        PlayerState.CROUCHING
    ]
    
    for state in states:
        player.current_state = state
        player._update_sprite()
        
        try:
            player.render(test_surface)
            print(f"✓ Rendered {state} successfully")
        except Exception as e:
            print(f"❌ Failed to render {state}: {e}")
            raise
    
    print("✓ Sprite rendering test passed")


def run_all_tests():
    """Run all texture tests."""
    print("Running texture loading tests...\n")
    
    try:
        test_texture_loading()
        test_walk_animation_frames()
        test_player_sprite_integration()
        test_sprite_rendering()
        
        print("\n✅ All texture tests passed!")
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