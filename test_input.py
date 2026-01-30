#!/usr/bin/env python3
"""
Tests for input controller module
"""

import pygame
from game.input_controller import PlayerController, InputManager, InputState
from game.player import Player
from game.physics import Vector2D


def test_input_state():
    """Test InputState data class."""
    print("Testing InputState...")
    
    # Test default values
    input_state = InputState()
    assert input_state.horizontal == 0.0
    assert input_state.jump == False
    assert input_state.crouch == False
    
    # Test custom values
    input_state = InputState(horizontal=1.0, jump=True, crouch=True)
    assert input_state.horizontal == 1.0
    assert input_state.jump == True
    assert input_state.crouch == True
    
    print("✓ InputState test passed")


def test_player_controller_creation():
    """Test PlayerController creation and initialization."""
    print("Testing PlayerController creation...")
    
    controller = PlayerController()
    
    # Test key mappings exist
    assert 'move_left' in controller.key_mappings
    assert 'move_right' in controller.key_mappings
    assert 'jump' in controller.key_mappings
    assert 'crouch' in controller.key_mappings
    
    # Test WASD keys are mapped
    assert pygame.K_a in controller.key_mappings['move_left']
    assert pygame.K_d in controller.key_mappings['move_right']
    assert pygame.K_SPACE in controller.key_mappings['jump']
    assert pygame.K_w in controller.key_mappings['jump']  # W is now in jump
    assert pygame.K_s in controller.key_mappings['crouch']
    
    # Test arrow keys are also mapped
    assert pygame.K_LEFT in controller.key_mappings['move_left']
    assert pygame.K_RIGHT in controller.key_mappings['move_right']
    assert pygame.K_UP in controller.key_mappings['jump']  # UP is now in jump
    assert pygame.K_DOWN in controller.key_mappings['crouch']
    
    print("✓ PlayerController creation test passed")


def test_key_event_handling():
    """Test key event handling."""
    print("Testing key event handling...")
    
    controller = PlayerController()
    
    # Simulate key press event
    key_down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
    controller.handle_event(key_down_event)
    
    # Key should be in pressed set
    assert pygame.K_a in controller.keys_pressed
    assert pygame.K_a in controller.keys_just_pressed
    
    # Process input
    controller._process_input()
    
    # Should register left movement
    assert controller.input_state.horizontal == -1.0
    
    # Simulate key release
    key_up_event = pygame.event.Event(pygame.KEYUP, key=pygame.K_a)
    controller.handle_event(key_up_event)
    
    # Key should be removed from pressed set
    assert pygame.K_a not in controller.keys_pressed
    assert pygame.K_a in controller.keys_just_released
    
    print("✓ Key event handling test passed")


def test_horizontal_input():
    """Test horizontal movement input processing."""
    print("Testing horizontal input...")
    
    controller = PlayerController()
    
    # Test left movement
    controller.keys_pressed.add(pygame.K_a)
    controller._process_input()
    assert controller.input_state.horizontal == -1.0
    
    # Test right movement
    controller.keys_pressed.clear()
    controller.keys_pressed.add(pygame.K_d)
    controller._process_input()
    assert controller.input_state.horizontal == 1.0
    
    # Test both keys (should cancel out to 0)
    controller.keys_pressed.add(pygame.K_a)
    controller._process_input()
    assert controller.input_state.horizontal == 0.0
    
    # Test no input
    controller.keys_pressed.clear()
    controller._process_input()
    assert controller.input_state.horizontal == 0.0
    
    print("✓ Horizontal input test passed")


def test_jump_input_buffering():
    """Test jump input buffering system."""
    print("Testing jump input buffering...")
    
    controller = PlayerController()
    
    # Simulate jump key press
    controller.keys_just_pressed.add(pygame.K_SPACE)
    controller._process_input()
    
    # Jump should be active
    assert controller.input_state.jump == True
    assert controller.jump_buffer_timer > 0
    
    # Clear just pressed (simulate next frame)
    controller.keys_just_pressed.clear()
    
    # Update with small delta time
    controller.update(0.05)  # 50ms
    
    # Jump should still be buffered
    assert controller.input_state.jump == True
    assert controller.jump_buffer_timer > 0
    
    # Update with enough time to expire buffer
    controller.update(0.2)  # 200ms total
    
    # Jump buffer should be expired
    assert controller.input_state.jump == False
    assert controller.jump_buffer_timer == 0
    
    print("✓ Jump input buffering test passed")


def test_player_integration():
    """Test PlayerController integration with Player."""
    print("Testing player integration...")
    
    controller = PlayerController()
    player = Player(Vector2D(100, 100))
    
    # Test horizontal movement
    controller.keys_pressed.add(pygame.K_d)
    controller.update(1.0/60.0, player)
    
    # Player should receive input
    assert player.input_horizontal == 1.0
    assert player.facing_right == True
    
    # Test jump
    controller.keys_pressed.clear()
    controller.keys_just_pressed.add(pygame.K_SPACE)
    controller.update(1.0/60.0, player)
    
    # Player should receive jump input
    assert player.input_jump_pressed == True
    
    print("✓ Player integration test passed")


def test_input_manager():
    """Test InputManager functionality."""
    print("Testing InputManager...")
    
    input_manager = InputManager()
    
    # Test initialization
    assert input_manager.keyboard_controller is not None
    assert input_manager.gamepad_controller is not None
    
    # Test event handling
    key_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
    input_manager.handle_event(key_event)
    
    # Should pass event to keyboard controller
    assert pygame.K_a in input_manager.keyboard_controller.keys_pressed
    
    # Test update
    player = Player(Vector2D(100, 100))
    input_manager.update(1.0/60.0, player)
    
    # Should update player input
    assert player.input_horizontal == -1.0
    
    print("✓ InputManager test passed")


def test_custom_key_mapping():
    """Test custom key mapping functionality."""
    print("Testing custom key mapping...")
    
    controller = PlayerController()
    
    # Add custom key for jump
    controller.add_key_to_action('jump', pygame.K_j)
    
    # Test that custom key works
    assert pygame.K_j in controller.key_mappings['jump']
    
    # Simulate key press (both pressed and just_pressed for jump)
    controller.keys_pressed.add(pygame.K_j)
    controller.keys_just_pressed.add(pygame.K_j)
    controller._process_input()
    
    # Should register as jump input
    assert controller.input_state.jump == True
    
    # Remove custom key
    controller.remove_key_from_action('jump', pygame.K_j)
    assert pygame.K_j not in controller.key_mappings['jump']
    
    print("✓ Custom key mapping test passed")


def run_all_tests():
    """Run all input controller tests."""
    print("Running input controller tests...\n")
    
    try:
        test_input_state()
        test_player_controller_creation()
        test_key_event_handling()
        test_horizontal_input()
        test_jump_input_buffering()
        test_player_integration()
        test_input_manager()
        test_custom_key_mapping()
        
        print("\n✅ All input controller tests passed!")
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