"""
Player Module
Player character implementation for the Ingushetia 2D Platformer
"""

import pygame
import math
from typing import Optional, Dict
from dataclasses import dataclass
from game.physics import Vector2D, PhysicsBody
from game.collision import Collider, CollisionLayer, CollisionData
from game.assets import asset_manager
from game.health import HealthComponent, HealthBar
from game.combat import Shashka


@dataclass
class PlayerStats:
    """Player statistics and configuration."""
    max_health: int = 100
    current_health: int = 100
    move_speed: float = 200.0  # pixels per second
    jump_force: float = 650.0  # pixels per second - увеличил с 550 до 650
    max_jump_count: int = 1  # Single jump by default
    ground_friction: float = 0.85  # Увеличил с 0.8 до 0.85
    air_friction: float = 0.98     # Увеличил с 0.95 до 0.98


class PlayerState:
    """Player state enumeration."""
    IDLE = "idle"
    WALKING = "walking"
    JUMPING = "jumping"
    FALLING = "falling"
    CROUCHING = "crouching"


class Player:
    """
    Player character class with physics, rendering, and input handling.
    """
    
    def __init__(self, start_position: Vector2D, size: Vector2D = None):
        """
        Initialize player character.
        
        Args:
            start_position: Starting position in world coordinates
            size: Player size (default: 48x72 pixels - увеличенный размер)
        """
        if size is None:
            size = Vector2D(48, 72)  # Увеличил с 32x48 до 48x72
        
        self.size = size
        self.stats = PlayerStats()
        
        # Physics setup
        self.physics_body = PhysicsBody(
            position=Vector2D(start_position.x, start_position.y),
            velocity=Vector2D.zero(),
            acceleration=Vector2D.zero(),
            mass=1.0,
            friction=self.stats.ground_friction,
            restitution=0.0,
            gravity_scale=1.0
        )
        
        # Collision setup
        self.collider = Collider(
            physics_body=self.physics_body,
            size=self.size,
            layer=CollisionLayer.PLAYER,
            is_trigger=False
        )
        
        # Set up collision callbacks
        self.collider.set_collision_callbacks(
            on_enter=self._on_collision_enter,
            on_stay=self._on_collision_stay,
            on_exit=self._on_collision_exit
        )
        
        # Здоровье
        self.health = HealthComponent(max_health=100)
        self.health.on_death = self._on_death
        self.health.on_damage = self._on_damage
        
        # Health bar
        self.health_bar = HealthBar(width=60, height=8)
        
        # Боевая система
        self.weapon = Shashka()
        self.is_attacking = False
        
        # Player state
        self.current_state = PlayerState.FALLING
        self.facing_right = True
        
        # Ground detection
        self.is_grounded = False
        self.ground_check_distance = 5.0
        self.jump_count = 0
        
        # Input state
        self.input_horizontal = 0.0  # -1 to 1
        self.input_jump = False
        self.input_jump_pressed = False  # Track jump press vs hold
        self.input_crouch = False
        self.input_attack = False  # Атака
        
        # Visual representation
        self.color = (100, 150, 255)  # Light blue (fallback)
        self.sprites = {}  # Will store loaded sprites
        self.current_sprite = None
        self.sprite_flip = False  # For horizontal flipping
        
        # Simple animation system
        self.animation_timer = 0.0
        self.current_frame = 0
        self.walk_frames = []  # Will store walk animation frames (0-4, using frames 0,1,2,4,5)
        self.walk_animation_speed = 8.0  # Frames per second
        
        # Load sprites
        self._load_sprites()
        
        # Debug info
        self.debug_info = {}
    
    def _load_sprites(self) -> None:
        """Load player sprites from assets."""
        sprite_size = (int(self.size.x), int(self.size.y))
        
        # Load static sprites
        self.sprites = {
            PlayerState.IDLE: asset_manager.get_player_sprite('idle', sprite_size),
            PlayerState.JUMPING: asset_manager.get_player_sprite('jump', sprite_size),
            PlayerState.FALLING: asset_manager.get_player_sprite('jump', sprite_size),  # Use jump sprite for falling
            PlayerState.CROUCHING: asset_manager.get_player_sprite('crouch', sprite_size)
        }
        
        # Load walk animation frames (0, 1, 2, 4, 5)
        self.walk_frames = []
        available_frames = [0, 1, 2, 4, 5]  # Available walk frame files
        
        for frame_num in available_frames:
            frame = asset_manager.get_walk_animation_frame_by_number(frame_num, sprite_size)
            # Always add frame since get_walk_animation_frame_by_number always returns something
            self.walk_frames.append(frame)
        
        # Set initial sprite
        self.current_sprite = self.sprites[PlayerState.FALLING]
        
        print(f"Loaded {len(self.sprites)} player sprites and {len(self.walk_frames)} walk frames")
    
    def _update_sprite(self) -> None:
        """Update current sprite based on player state with simple animation logic."""
        # Handle sprite flipping based on facing direction
        self.sprite_flip = not self.facing_right
        
        # Simple state-based sprite selection
        if self.current_state == PlayerState.WALKING and self.walk_frames:
            # Simple walk animation - cycle through frames
            frame_duration = 1.0 / self.walk_animation_speed
            frame_index = int(self.animation_timer / frame_duration) % len(self.walk_frames)
            self.current_sprite = self.walk_frames[frame_index]
            
        elif self.current_state == PlayerState.IDLE:
            self.current_sprite = self.sprites[PlayerState.IDLE]
            
        elif self.current_state == PlayerState.JUMPING:
            self.current_sprite = self.sprites[PlayerState.JUMPING]
                    
        elif self.current_state == PlayerState.FALLING:
            self.current_sprite = self.sprites[PlayerState.FALLING]
                    
        elif self.current_state == PlayerState.CROUCHING:
            self.current_sprite = self.sprites[PlayerState.CROUCHING]
                
        else:
            # Default sprite for other states
            if self.current_state in self.sprites:
                self.current_sprite = self.sprites[self.current_state]
    
    def _on_collision_enter(self, other_collider: Collider, collision: CollisionData) -> None:
        """Handle collision enter events."""
        if other_collider.layer == CollisionLayer.PLATFORM:
            if collision.collision_side == "top":
                self.is_grounded = True
                self.jump_count = 0
                
                if self.current_state in [PlayerState.FALLING, PlayerState.JUMPING]:
                    self._change_state(PlayerState.IDLE)
                    
                    # Stop downward velocity when landing
                    if self.physics_body.velocity.y > 0:
                        self.physics_body.velocity = Vector2D(
                            self.physics_body.velocity.x,
                            0
                        )
    
    def _on_death(self) -> None:
        """Вызывается при смерти игрока."""
        print("Player died!")
        # Можно добавить логику перезапуска уровня
    
    def _on_damage(self, damage: int, remaining_health: int) -> None:
        """Вызывается при получении урона."""
        print(f"Player took {damage} damage, {remaining_health} health remaining")
        # Можно добавить эффекты получения урона
    
    def take_damage(self, damage: int) -> bool:
        """
        Получить урон.
        
        Args:
            damage: Количество урона
            
        Returns:
            True если игрок еще жив
        """
        return self.health.take_damage(damage)
    
    def attack(self) -> None:
        """Выполнить атаку."""
        if self.weapon.can_attack():
            self.weapon.start_attack()
            self.is_attacking = True
    
    def _on_collision_stay(self, other_collider: Collider, collision: CollisionData) -> None:
        """Handle ongoing collision events."""
        if other_collider.layer == CollisionLayer.PLATFORM:
            if collision.collision_side == "top":
                # Continuously maintain grounded state while on platform
                self.is_grounded = True
                # Reset jump count while on ground
                if self.jump_count > 0 and abs(self.physics_body.velocity.y) < 10:
                    self.jump_count = 0
    
    def _on_collision_exit(self, other_collider: Collider) -> None:
        """Handle collision exit events."""
        # Don't immediately lose grounded state on collision exit
        # Let the physics update handle this more gracefully
        pass
    
    def _change_state(self, new_state: str) -> None:
        """Change player state with validation."""
        if self.current_state != new_state:
            old_state = self.current_state
            self.current_state = new_state
            self._on_state_changed(old_state, new_state)
    
    def _on_state_changed(self, old_state: str, new_state: str) -> None:
        """Handle state change events."""
        # Reset state-specific properties
        if new_state == PlayerState.IDLE:
            pass
        elif new_state == PlayerState.WALKING:
            pass
        elif new_state == PlayerState.JUMPING:
            pass
        elif new_state == PlayerState.FALLING:
            pass
        elif new_state == PlayerState.CROUCHING:
            pass
    
    def set_input(self, horizontal: float, jump: bool, crouch: bool, attack: bool = False) -> None:
        """
        Set player input state.
        
        Args:
            horizontal: Horizontal input (-1 to 1)
            jump: Jump button pressed
            crouch: Crouch button pressed
            attack: Attack button pressed
        """
        self.input_horizontal = max(-1.0, min(1.0, horizontal))
        
        # Handle jump press detection
        jump_pressed = jump and not self.input_jump
        self.input_jump = jump
        self.input_jump_pressed = jump_pressed
        
        self.input_crouch = crouch
        self.input_attack = attack
        
        # Update facing direction
        if self.input_horizontal > 0:
            self.facing_right = True
        elif self.input_horizontal < 0:
            self.facing_right = False
    
    def jump(self) -> bool:
        """
        Attempt to make the player jump.
        
        Returns:
            True if jump was successful
        """
        # Debug info
        can_jump = self.jump_count < self.stats.max_jump_count
        
        if can_jump:
            # Apply jump force - reset Y velocity completely for consistent jumps
            self.physics_body.velocity = Vector2D(
                self.physics_body.velocity.x,  # Keep horizontal velocity
                -self.stats.jump_force  # Set jump velocity
            )
            
            self.jump_count += 1
            self.is_grounded = False  # Immediately lose grounded state when jumping
            self._change_state(PlayerState.JUMPING)
            
            return True
        
        return False
    
    def update(self, delta_time: float) -> None:
        """
        Update player logic, physics, and state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        self.animation_timer += delta_time
        
        # Обновляем здоровье
        self.health.update(delta_time)
        
        # Обновляем оружие
        self.weapon.update(delta_time)
        if not self.weapon.is_attacking:
            self.is_attacking = False
        
        # Handle input
        self._handle_input(delta_time)
        
        # Check if player should lose grounded state
        self._check_grounded_state()
        
        # Update state based on physics
        self._update_state()
        
        # Update sprite based on state
        self._update_sprite()
        
        # Apply friction based on state
        self._apply_friction()
        
        # Keep player within reasonable bounds
        self._clamp_position()
        
        # Update debug info
        self._update_debug_info()
    
    def _clamp_position(self) -> None:
        """Keep player within reasonable world bounds."""
        # Prevent player from going too far off screen
        min_x = -100
        max_x = 2000  # Reasonable world width
        min_y = -500  # Allow going above screen
        max_y = 900   # Увеличил до 900, чтобы дать больше места для падения
        
        if self.physics_body.position.x < min_x:
            self.physics_body.position.x = min_x
            self.physics_body.velocity.x = max(0, self.physics_body.velocity.x)
        elif self.physics_body.position.x > max_x:
            self.physics_body.position.x = max_x
            self.physics_body.velocity.x = min(0, self.physics_body.velocity.x)
        
        if self.physics_body.position.y < min_y:
            self.physics_body.position.y = min_y
            self.physics_body.velocity.y = max(0, self.physics_body.velocity.y)
        elif self.physics_body.position.y > max_y:
            # Reset player if they fall too far - поставим на безопасную позицию над платформой
            print(f"Player fell too far! Position: {self.physics_body.position}, max_y: {max_y}")
            self.reset_position(Vector2D(100, 300))  # Изменил на 300
            print("Player fell too far, resetting position")
    
    def _check_grounded_state(self) -> None:
        """Check if player should lose grounded state based on velocity."""
        # Only lose grounded state if moving upward significantly (jumping)
        # Don't lose grounded state from small velocity changes during movement
        if self.is_grounded and self.physics_body.velocity.y < -50:  # Уменьшил порог с -100 до -50
            self.is_grounded = False
    
    def _handle_input(self, delta_time: float) -> None:
        """Handle player input and apply forces."""
        # Horizontal movement
        if abs(self.input_horizontal) > 0.1:
            # Calculate desired velocity
            desired_velocity = self.input_horizontal * self.stats.move_speed
            
            # Apply force to reach desired velocity - более отзывчивое движение
            velocity_diff = desired_velocity - self.physics_body.velocity.x
            move_force = Vector2D(velocity_diff * self.physics_body.mass * 15, 0)  # Увеличил с 10 до 15
            self.physics_body.apply_force(move_force)
        
        # Jump input (only on press, not hold)
        if self.input_jump_pressed:
            self.jump()
        
        # Attack input
        if self.input_attack:
            self.attack()
        
        # Crouch input
        if self.input_crouch and self.is_grounded:
            if self.current_state != PlayerState.CROUCHING:
                self._change_state(PlayerState.CROUCHING)
        elif self.current_state == PlayerState.CROUCHING:
            self._change_state(PlayerState.IDLE)
    
    def _update_state(self) -> None:
        """Update player state based on current conditions."""
        # More sophisticated ground detection
        # Check if player is moving downward fast enough to be considered falling
        falling_threshold = 30   # Уменьшил с 50 до 30 для более быстрой реакции
        jumping_threshold = -30  # Увеличил с -50 до -30
        
        # State transitions
        if not self.is_grounded:
            if self.physics_body.velocity.y < jumping_threshold:  # Going up fast
                if self.current_state != PlayerState.JUMPING:
                    self._change_state(PlayerState.JUMPING)
            elif self.physics_body.velocity.y > falling_threshold:  # Going down fast
                if self.current_state != PlayerState.FALLING:
                    self._change_state(PlayerState.FALLING)
        else:
            # On ground - check for movement
            if self.current_state not in [PlayerState.CROUCHING]:
                if abs(self.input_horizontal) > 0.1:
                    if self.current_state != PlayerState.WALKING:
                        self._change_state(PlayerState.WALKING)
                else:
                    if self.current_state != PlayerState.IDLE:
                        self._change_state(PlayerState.IDLE)
    
    def _apply_friction(self) -> None:
        """Apply friction based on current state."""
        if self.is_grounded:
            friction = self.stats.ground_friction
            # Если игрок не двигается, применяем дополнительное торможение
            if abs(self.input_horizontal) < 0.1:
                friction = 0.75  # Более сильное торможение когда не двигаемся
        else:
            friction = self.stats.air_friction
        
        # Apply horizontal friction
        self.physics_body.velocity = Vector2D(
            self.physics_body.velocity.x * friction,
            self.physics_body.velocity.y
        )
        
        # Останавливаем очень медленное движение чтобы избежать "дрожания"
        if abs(self.physics_body.velocity.x) < 5.0 and self.is_grounded:
            self.physics_body.velocity.x = 0
    
    def _update_debug_info(self) -> None:
        """Update debug information."""
        self.debug_info = {
            "position": f"({self.physics_body.position.x:.1f}, {self.physics_body.position.y:.1f})",
            "velocity": f"({self.physics_body.velocity.x:.1f}, {self.physics_body.velocity.y:.1f})",
            "state": self.current_state,
            "grounded": self.is_grounded,
            "jump_count": f"{self.jump_count}/{self.stats.max_jump_count}",
            "facing_right": self.facing_right,
            "can_jump": self.jump_count < self.stats.max_jump_count,
            "input_h": f"{self.input_horizontal:.1f}",
            "input_jump": self.input_jump_pressed,
            "walk_frame": f"{int(self.animation_timer * self.walk_animation_speed) % len(self.walk_frames) if self.walk_frames else 0}/{len(self.walk_frames)}"
        }
    
    def render(self, surface: pygame.Surface, camera_offset: Vector2D = None) -> None:
        """
        Render the player character with simple sprite rendering.
        
        Args:
            surface: Surface to render on
            camera_offset: Camera offset for world-to-screen conversion
        """
        if camera_offset is None:
            camera_offset = Vector2D.zero()
        
        # Calculate screen position with state-based offset
        screen_pos = self.physics_body.position - camera_offset
        
        # Применяем смещение в зависимости от состояния
        if self.current_state == PlayerState.WALKING:
            screen_pos.y += 2  # Опускаем при ходьбе
        elif self.current_state == PlayerState.CROUCHING:
            screen_pos.y -= 2  # Поднимаем при приседании
        
        # Get current sprite
        sprite = self.current_sprite
        
        if sprite:
            # Calculate sprite position (center the sprite)
            sprite_rect = sprite.get_rect()
            sprite_rect.center = (int(screen_pos.x), int(screen_pos.y))
            
            # Adjust position for crouching - move sprite down
            if self.current_state == PlayerState.CROUCHING:
                # Move sprite down by quarter of its height to simulate crouching
                sprite_rect.y += int(self.size.y * 0.25)
            
            # Flip sprite horizontally if facing left
            if self.sprite_flip:
                sprite = pygame.transform.flip(sprite, True, False)
            
            # Draw sprite
            surface.blit(sprite, sprite_rect)
            
        else:
            # Fallback to colored rectangle if no sprite
            self._render_fallback(surface, screen_pos)
        
        # Simple ground indicator
        if self.is_grounded:
            ground_color = (0, 255, 0)
            pygame.draw.circle(surface, ground_color, 
                             (int(screen_pos.x), int(screen_pos.y + self.size.y / 2) + 5), 3)
        
        # Рисуем оружие
        if self.weapon:
            self.weapon.render(surface, self.physics_body.position, self.facing_right, camera_offset)
        
        # Рисуем полоску здоровья
        if self.health.is_alive:
            self.health_bar.render(surface, self.physics_body.position, self.health, camera_offset)
    
    
    def _render_fallback(self, surface: pygame.Surface, screen_pos: Vector2D) -> None:
        """Render fallback colored rectangle when no sprite is available."""
        # Create player rectangle
        player_rect = pygame.Rect(
            screen_pos.x - self.size.x / 2,
            screen_pos.y - self.size.y / 2,
            self.size.x,
            self.size.y
        )
        
        # Choose color based on state
        base_color = (100, 150, 255)  # Light blue
        if self.current_state == PlayerState.JUMPING:
            base_color = (150, 255, 150)  # Light green
        elif self.current_state == PlayerState.FALLING:
            base_color = (255, 150, 150)  # Light red
        elif self.current_state == PlayerState.CROUCHING:
            base_color = (255, 255, 150)  # Light yellow
            # Make player shorter when crouching
            player_rect.height = int(self.size.y * 0.7)
            player_rect.y += int(self.size.y * 0.3)
        elif self.current_state == PlayerState.WALKING:
            base_color = (150, 200, 255)  # Slightly different blue
        
        # Draw player with outline for better visibility
        outline_rect = pygame.Rect(player_rect.x - 2, player_rect.y - 2, 
                                 player_rect.width + 4, player_rect.height + 4)
        pygame.draw.rect(surface, (0, 0, 0), outline_rect)  # Black outline
        pygame.draw.rect(surface, base_color, player_rect)
        
        # Draw facing direction indicator (eye)
        eye_size = 4
        if self.facing_right:
            eye_pos = (player_rect.right - 8, player_rect.top + 8)
        else:
            eye_pos = (player_rect.left + 8, player_rect.top + 8)
        
        pygame.draw.circle(surface, (255, 255, 255), eye_pos, eye_size)
        pygame.draw.circle(surface, (0, 0, 0), eye_pos, eye_size - 1)
    
    def render_debug(self, surface: pygame.Surface, camera_offset: Vector2D = None, font: pygame.font.Font = None) -> None:
        """
        Render debug information.
        
        Args:
            surface: Surface to render on
            camera_offset: Camera offset
            font: Font to use for text
        """
        if font is None:
            font = pygame.font.Font(None, 20)
        
        if camera_offset is None:
            camera_offset = Vector2D.zero()
        
        screen_pos = self.physics_body.position - camera_offset
        
        # Render debug text above player
        y_offset = 0
        for key, value in self.debug_info.items():
            text = font.render(f"{key}: {value}", True, (255, 255, 0))
            surface.blit(text, (screen_pos.x + 40, screen_pos.y - 60 + y_offset))
            y_offset += 15
    
    def get_position(self) -> Vector2D:
        """Get player world position."""
        return Vector2D(self.physics_body.position.x, self.physics_body.position.y)
    
    def get_bounds(self) -> pygame.Rect:
        """Get player collision bounds."""
        return self.collider.get_bounds()
    
    def take_damage(self, damage: int) -> bool:
        """
        Apply damage to player.
        
        Args:
            damage: Damage amount
            
        Returns:
            True if player is still alive
        """
        self.stats.current_health = max(0, self.stats.current_health - damage)
        return self.stats.current_health > 0
    
    def heal(self, amount: int) -> None:
        """
        Heal the player.
        
        Args:
            amount: Healing amount
        """
        self.stats.current_health = min(
            self.stats.max_health,
            self.stats.current_health + amount
        )
    
    def reset_position(self, position: Vector2D) -> None:
        """
        Reset player to a specific position.
        
        Args:
            position: New position
        """
        self.physics_body.position = Vector2D(position.x, position.y)
        self.physics_body.velocity = Vector2D.zero()
        self.physics_body.acceleration = Vector2D.zero()
        self.is_grounded = False
        self.jump_count = 0
        self._change_state(PlayerState.FALLING)