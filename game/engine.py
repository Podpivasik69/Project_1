"""
Game Engine Module
Core game engine components for the Ingushetia 2D Platformer
"""

from typing import Dict, Any, Optional
import pygame


class StateManager:
    """
    Manages game state transitions and validation.
    Ensures proper state flow and prevents invalid transitions.
    """
    
    def __init__(self, initial_state = "menu"):
        self.current_state = initial_state
        self.previous_state = None
        self.state_data = {}  # Store state-specific data
        
        # Define valid state transitions
        self.valid_transitions = {
            "menu": ["playing"],
            "playing": ["paused", "game_over", "menu"],
            "paused": ["playing", "menu"],
            "game_over": ["menu", "playing"]
        }
        
        # State entry/exit callbacks
        self.on_enter_callbacks = {}
        self.on_exit_callbacks = {}
    
    def register_state_callback(self, state, on_enter=None, on_exit=None):
        """
        Register callbacks for state entry and exit.
        
        Args:
            state: The game state to register callbacks for
            on_enter: Callback function called when entering the state
            on_exit: Callback function called when exiting the state
        """
        if on_enter:
            self.on_enter_callbacks[state] = on_enter
        if on_exit:
            self.on_exit_callbacks[state] = on_exit
    
    def can_transition_to(self, new_state) -> bool:
        """
        Check if transition to new state is valid.
        
        Args:
            new_state: The state to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """
        return new_state in self.valid_transitions.get(self.current_state, [])
    
    def transition_to(self, new_state, data: dict = None) -> bool:
        """
        Attempt to transition to a new state.
        
        Args:
            new_state: The state to transition to
            data: Optional data to pass to the new state
            
        Returns:
            True if transition successful, False if invalid
        """
        if not self.can_transition_to(new_state):
            print(f"Invalid transition from {self.current_state} to {new_state}")
            return False
        
        # Call exit callback for current state
        if self.current_state in self.on_exit_callbacks:
            self.on_exit_callbacks[self.current_state]()
        
        # Update states
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Store state data
        if data:
            self.state_data[new_state] = data
        
        # Call enter callback for new state
        if new_state in self.on_enter_callbacks:
            self.on_enter_callbacks[new_state]()
        
        return True
    
    def get_current_state(self):
        """Get the current game state."""
        return self.current_state
    
    def get_previous_state(self):
        """Get the previous game state."""
        return self.previous_state
    
    def get_state_data(self, state = None) -> dict:
        """
        Get data associated with a state.
        
        Args:
            state: The state to get data for. If None, returns current state data.
            
        Returns:
            Dictionary of state data
        """
        target_state = state or self.current_state
        return self.state_data.get(target_state, {})
    
    def set_state_data(self, data: dict, state = None) -> None:
        """
        Set data for a state.
        
        Args:
            data: Data to store
            state: The state to store data for. If None, uses current state.
        """
        target_state = state or self.current_state
        self.state_data[target_state] = data


class EventSystem:
    """
    Simple event system for decoupled communication between game components.
    """
    
    def __init__(self):
        self.handlers: Dict[str, list] = {}
    
    def register_handler(self, event_type: str, handler) -> None:
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: The type of event to listen for
            handler: Callable to handle the event
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def emit_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """
        Emit an event to all registered handlers.
        
        Args:
            event_type: The type of event to emit
            data: Optional data to pass to handlers
        """
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                handler(data or {})
    
    def unregister_handler(self, event_type: str, handler) -> None:
        """
        Unregister an event handler.
        
        Args:
            event_type: The event type to unregister from
            handler: The handler to remove
        """
        if event_type in self.handlers and handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)