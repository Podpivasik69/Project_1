"""
Input Controller Module
Handles player input and translates it to game actions
"""

import pygame
from typing import Dict, Set
from dataclasses import dataclass
from game.player import Player


@dataclass
class InputState:
    """Current input state."""
    horizontal: float = 0.0  # -1 to 1
    jump: bool = False
    crouch: bool = False
    attack: bool = False  # Атака
    
    # Additional actions for future use
    action1: bool = False  # Could be attack, interact, etc.
    action2: bool = False
    pause: bool = False


class PlayerController:
    """
    Handles player input processing and translates keyboard input to player actions.
    Supports both WASD and arrow key controls.
    """
    
    def __init__(self):
        # Key mappings
        self.key_mappings = {
            # Movement
            'move_left': [pygame.K_a, pygame.K_LEFT],
            'move_right': [pygame.K_d, pygame.K_RIGHT],
            'jump': [pygame.K_SPACE, pygame.K_w, pygame.K_UP],  # SPACE, W, and UP for jump
            'crouch': [pygame.K_s, pygame.K_DOWN],
            
            # Combat
            'attack': [],  # Будет обрабатываться через мышь
            
            # Actions
            'action1': [pygame.K_j, pygame.K_z],
            'action2': [pygame.K_k, pygame.K_x],
            'pause': [pygame.K_ESCAPE, pygame.K_p]
        }
        
        # Track key states
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()
        
        # Mouse states
        self.mouse_buttons_pressed: Set[int] = set()
        self.mouse_buttons_just_pressed: Set[int] = set()
        self.mouse_buttons_just_released: Set[int] = set()
        self.mouse_pos = (0, 0)
        
        # Input state
        self.input_state = InputState()
        
        # Settings
        self.dead_zone = 0.1  # Minimum input threshold
        self.input_buffer_time = 0.1  # Seconds to buffer jump input
        self.jump_buffer_timer = 0.0
        
        # Coyote time (grace period for jumping after leaving ground)
        self.coyote_time = 0.1
        self.coyote_timer = 0.0
        self.was_grounded = False
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle pygame events for input processing.
        
        Args:
            event: Pygame event to process
        """
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            self.keys_just_pressed.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
            self.keys_just_released.add(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons_pressed.add(event.button)
            self.mouse_buttons_just_pressed.add(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons_pressed.discard(event.button)
            self.mouse_buttons_just_released.add(event.button)
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
    
    def update(self, delta_time: float, player: Player = None) -> None:
        """
        Update input controller and process input state.
        
        Args:
            delta_time: Time elapsed since last update
            player: Player object to update (optional)
        """
        # Update timers
        self.jump_buffer_timer = max(0, self.jump_buffer_timer - delta_time)
        
        if player:
            # Update coyote time
            if player.is_grounded:
                self.coyote_timer = self.coyote_time
                self.was_grounded = True
            else:
                self.coyote_timer = max(0, self.coyote_timer - delta_time)
                if self.was_grounded and self.coyote_timer <= 0:
                    self.was_grounded = False
        
        # Process input
        self._process_input()
        
        # Apply input to player if provided
        if player:
            self._apply_input_to_player(player)
        
        # Clear just pressed/released sets
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_buttons_just_pressed.clear()
        self.mouse_buttons_just_released.clear()
    
    def _process_input(self) -> None:
        """Process current key states into input state."""
        # Horizontal movement
        horizontal = 0.0
        
        if self._is_key_pressed('move_left'):
            horizontal -= 1.0
        if self._is_key_pressed('move_right'):
            horizontal += 1.0
        
        # Apply dead zone
        if abs(horizontal) < self.dead_zone:
            horizontal = 0.0
        
        self.input_state.horizontal = horizontal
        
        # Jump input (with buffering)
        if self._is_key_just_pressed('jump'):
            self.jump_buffer_timer = self.input_buffer_time
        
        self.input_state.jump = self.jump_buffer_timer > 0
        
        # Other inputs
        self.input_state.crouch = self._is_key_pressed('crouch')
        self.input_state.attack = 1 in self.mouse_buttons_just_pressed  # Левая кнопка мыши
        self.input_state.action1 = self._is_key_just_pressed('action1')
        self.input_state.action2 = self._is_key_just_pressed('action2')
        self.input_state.pause = self._is_key_just_pressed('pause')
    
    def _apply_input_to_player(self, player: Player) -> None:
        """
        Apply processed input to player character.
        
        Args:
            player: Player object to control
        """
        # Handle jump with coyote time and buffering
        jump_input = False
        if self.input_state.jump:
            # Can jump if grounded, in coyote time, or has remaining jumps
            can_jump = (player.is_grounded or 
                       self.coyote_timer > 0 or 
                       player.jump_count < player.stats.max_jump_count)
            
            if can_jump:
                jump_input = True
                self.jump_buffer_timer = 0  # Consume jump buffer
                if not player.is_grounded:
                    self.coyote_timer = 0  # Consume coyote time
        
        # Set player input
        player.set_input(
            horizontal=self.input_state.horizontal,
            jump=jump_input,
            crouch=self.input_state.crouch,
            attack=self.input_state.attack
        )
    
    def _is_key_pressed(self, action: str) -> bool:
        """Check if any key for the given action is currently pressed."""
        if action not in self.key_mappings:
            return False
        
        return any(key in self.keys_pressed for key in self.key_mappings[action])
    
    def _is_key_just_pressed(self, action: str) -> bool:
        """Check if any key for the given action was just pressed this frame."""
        if action not in self.key_mappings:
            return False
        
        return any(key in self.keys_just_pressed for key in self.key_mappings[action])
    
    def _is_key_just_released(self, action: str) -> bool:
        """Check if any key for the given action was just released this frame."""
        if action not in self.key_mappings:
            return False
        
        return any(key in self.keys_just_released for key in self.key_mappings[action])
    
    def get_input_state(self) -> InputState:
        """Get current input state."""
        return self.input_state
    
    def set_key_mapping(self, action: str, keys: list) -> None:
        """
        Set custom key mapping for an action.
        
        Args:
            action: Action name
            keys: List of pygame key constants
        """
        self.key_mappings[action] = keys
    
    def add_key_to_action(self, action: str, key: int) -> None:
        """
        Add a key to an existing action.
        
        Args:
            action: Action name
            key: Pygame key constant
        """
        if action in self.key_mappings:
            if key not in self.key_mappings[action]:
                self.key_mappings[action].append(key)
    
    def remove_key_from_action(self, action: str, key: int) -> None:
        """
        Remove a key from an action.
        
        Args:
            action: Action name
            key: Pygame key constant
        """
        if action in self.key_mappings and key in self.key_mappings[action]:
            self.key_mappings[action].remove(key)
    
    def get_debug_info(self) -> Dict[str, any]:
        """Get debug information about current input state."""
        return {
            'horizontal': self.input_state.horizontal,
            'jump': self.input_state.jump,
            'crouch': self.input_state.crouch,
            'jump_buffer': self.jump_buffer_timer,
            'coyote_time': self.coyote_timer,
            'keys_pressed': len(self.keys_pressed),
            'was_grounded': self.was_grounded
        }


class GamepadController:
    """
    Gamepad/Controller input handler (placeholder for future implementation).
    """
    
    def __init__(self):
        self.connected = False
        self.joystick = None
        
        # Initialize joystick support
        pygame.joystick.init()
        
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.connected = True
            print(f"Gamepad connected: {self.joystick.get_name()}")
    
    def update(self, delta_time: float, player: Player = None) -> None:
        """Update gamepad input (placeholder)."""
        if not self.connected or not self.joystick:
            return
        
        # TODO: Implement gamepad input processing
        # This would read joystick axes and buttons
        # and translate them to player actions
        pass
    
    def get_input_state(self) -> InputState:
        """Get gamepad input state (placeholder)."""
        return InputState()


class InputManager:
    """
    Manages multiple input sources (keyboard, gamepad) and combines them.
    """
    
    def __init__(self):
        self.keyboard_controller = PlayerController()
        self.gamepad_controller = GamepadController()
        self.combined_input = InputState()
        
        # Input priority (keyboard takes precedence over gamepad)
        self.input_priority = ['keyboard', 'gamepad']
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events for all input sources."""
        self.keyboard_controller.handle_event(event)
    
    def update(self, delta_time: float, player: Player = None) -> None:
        """Update all input sources and combine input."""
        # Update individual controllers
        self.keyboard_controller.update(delta_time, player)
        self.gamepad_controller.update(delta_time)
        
        # Combine input (keyboard takes priority)
        keyboard_input = self.keyboard_controller.get_input_state()
        gamepad_input = self.gamepad_controller.get_input_state()
        
        # Use keyboard input if any keyboard input is detected
        if (abs(keyboard_input.horizontal) > 0 or 
            keyboard_input.jump or 
            keyboard_input.crouch):
            self.combined_input = keyboard_input
        else:
            self.combined_input = gamepad_input
    
    def get_input_state(self) -> InputState:
        """Get combined input state."""
        return self.combined_input
    
    def get_debug_info(self) -> Dict[str, any]:
        """Get debug information from all input sources."""
        return {
            'keyboard': self.keyboard_controller.get_debug_info(),
            'gamepad_connected': self.gamepad_controller.connected
        }