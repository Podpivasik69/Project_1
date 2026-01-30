"""
Game State Manager Module
Centralized game state management following SOLID principles
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, Callable
import pygame
from game.physics import Vector2D
from game.utils import Colors, FontSizes, RenderUtils, GameConfig
from game.player import PlayerState
from game.wolf import Wolf
from game.combat import CombatSystem
# from game.world_manager import WorldManager


class GameState(Enum):
    """Enumeration of possible game states."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    LOADING = "loading"


class IGameState(ABC):
    """Interface for game state implementations (Interface Segregation Principle)."""
    
    @abstractmethod
    def enter(self, previous_state: Optional[GameState], data: Dict[str, Any] = None) -> None:
        """Called when entering this state."""
        pass
    
    @abstractmethod
    def exit(self, next_state: GameState) -> Dict[str, Any]:
        """Called when exiting this state. Returns data to pass to next state."""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update state logic."""
        pass
    
    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Render state visuals."""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if event was consumed."""
        pass


class MenuState(IGameState):
    """Menu state implementation."""
    
    def __init__(self, window_width: int, window_height: int):
        self.window_width = window_width
        self.window_height = window_height
        
    def enter(self, previous_state: Optional[GameState], data: Dict[str, Any] = None) -> None:
        """Enter menu state."""
        pass
        
    def exit(self, next_state: GameState) -> Dict[str, Any]:
        """Exit menu state."""
        return {}
        
    def update(self, delta_time: float) -> None:
        """Update menu logic."""
        pass
        
    def render(self, surface: pygame.Surface) -> None:
        """Render menu."""
        RenderUtils.draw_gradient_background(surface, Colors.MIDNIGHT_BLUE, Colors.DARK_BLUE, 
                                           self.window_width, self.window_height)
        
        font_large = pygame.font.Font(None, FontSizes.EXTRA_LARGE)
        font_medium = pygame.font.Font(None, FontSizes.LARGE)
        font_small = pygame.font.Font(None, FontSizes.MEDIUM)
        
        # Title with shadow
        title_text = GameConfig.GAME_TITLE
        title_pos = (self.window_width // 2, self.window_height // 2 - 100)
        RenderUtils.draw_text_with_shadow(surface, title_text, font_large, title_pos, Colors.GOLD)
        
        # Subtitle
        subtitle = font_medium.render("Cultural Heritage Platformer", True, Colors.LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(center=(self.window_width // 2, self.window_height // 2 - 50))
        surface.blit(subtitle, subtitle_rect)
        
        # Instructions
        instructions = [
            "Press ENTER to start",
            "Press ESC to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, Colors.WHITE)
            text_rect = text.get_rect(center=(self.window_width // 2, self.window_height // 2 + 20 + i * 30))
            surface.blit(text, text_rect)
        
        # Add decorative elements
        RenderUtils.draw_stars(surface, self.window_width, self.window_height)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle menu events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return True  # Signal to transition to playing
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()
        return False


class PlayingState(IGameState):
    """Playing state implementation."""
    
    def __init__(self, window_width: int, window_height: int):
        self.window_width = window_width
        self.window_height = window_height
        
        # Game objects (will be injected)
        self.player = None
        self.collision_system = None
        self.input_manager = None
        
        # Combat system
        self.combat_system = CombatSystem()
        
        # Enemies
        self.wolves = []
        
        # Simple platforms
        self.platforms = []
        self.platforms_created = False
        
    def set_game_objects(self, player, collision_system, input_manager):
        """Inject game objects (Dependency Injection)."""
        self.player = player
        self.collision_system = collision_system
        self.input_manager = input_manager
        
    def enter(self, previous_state: Optional[GameState], data: Dict[str, Any] = None) -> None:
        """Enter playing state."""
        # Устанавливаем позицию игрока
        if self.player:
            start_pos = Vector2D(100, 300)  # Поставим игрока выше первой платформы
            self.player.reset_position(start_pos)
        
        # Game objects should already be injected via set_game_objects
        if self.player and self.collision_system:
            # Make sure player collider is in collision system
            if self.player.collider not in self.collision_system.colliders:
                self.collision_system.add_collider(self.player.collider)
            
            # Создаем простые платформы
            if not self.platforms_created:
                self._create_simple_platforms()
                self.platforms_created = True
        
    def exit(self, next_state: GameState) -> Dict[str, Any]:
        """Exit playing state."""
        return {}
        
    def update(self, delta_time: float) -> None:
        """Update playing state."""
        if self.input_manager and self.player:
            self.input_manager.update(delta_time, self.player)
            
        if self.player:
            # Применяем гравитацию к игроку
            self._apply_gravity_to_player(delta_time)
            
            # Обновляем физику игрока
            self.player.update(delta_time)
            
            # Обрабатываем атаку игрока
            if self.player.is_attacking:
                hit_targets = self.combat_system.perform_attack(
                    self.player, 
                    self.player.weapon, 
                    self.wolves
                )
                if hit_targets:
                    print(f"Player hit {len(hit_targets)} targets!")
        
        # Обновляем волков
        for wolf in self.wolves[:]:  # Копируем список для безопасного удаления
            if wolf.marked_for_removal:
                self.wolves.remove(wolf)
                continue
            
            # Применяем гравитацию к волку
            self._apply_gravity_to_wolf(wolf, delta_time)
            
            # Обновляем волка
            wolf.update(delta_time)
            
        # Простая проверка коллизий вместо сложной системы
        self._simple_collision_check()
        
        # if self.collision_system:
        #     self.collision_system.update(delta_time)
    
    def _simple_collision_check(self) -> None:
        """Простая проверка коллизий игрока с платформами."""
        if not self.player:
            return
        
        # Получаем позицию игрока с учетом состояния
        player_y_offset = 0
        if self.player.current_state == PlayerState.WALKING:
            player_y_offset = 2  # Опускаем игрока на 2 пикселя при ходьбе
        elif self.player.current_state == PlayerState.CROUCHING:
            player_y_offset = -2  # Поднимаем игрока на 2 пикселя при приседании
        
        player_rect = pygame.Rect(
            self.player.physics_body.position.x - self.player.size.x / 2,
            self.player.physics_body.position.y - self.player.size.y / 2 + player_y_offset,
            self.player.size.x,
            self.player.size.y
        )
        
        # Сначала проверим, находится ли игрок на земле
        player_on_ground = False
        
        # Проверяем коллизию с каждой платформой
        for i, platform in enumerate(self.platforms):
            platform_rect = platform['rect']
            
            if player_rect.colliderect(platform_rect):
                # Определяем перекрытие по осям
                overlap_x = min(player_rect.right, platform_rect.right) - max(player_rect.left, platform_rect.left)
                overlap_y = min(player_rect.bottom, platform_rect.bottom) - max(player_rect.top, platform_rect.top)
                
                # Добавляем небольшой буфер для более стабильных коллизий
                collision_buffer = 2.0
                
                # Определяем, какая ось имеет меньшее перекрытие (направление коллизии)
                if overlap_x < overlap_y and overlap_x > 1:  # Добавил проверку минимального перекрытия
                    # Горизонтальная коллизия
                    if player_rect.centerx < platform_rect.centerx:
                        # Игрок слева от платформы
                        self.player.physics_body.position.x = platform_rect.left - self.player.size.x / 2 - collision_buffer
                    else:
                        # Игрок справа от платформы
                        self.player.physics_body.position.x = platform_rect.right + self.player.size.x / 2 + collision_buffer
                    self.player.physics_body.velocity.x = 0
                else:
                    # Вертикальная коллизия
                    if player_rect.centery < platform_rect.centery:
                        # Игрок сверху платформы (приземление)
                        self.player.physics_body.position.y = platform_rect.top - self.player.size.y / 2 - collision_buffer + player_y_offset
                        self.player.physics_body.velocity.y = 0
                        self.player.is_grounded = True
                        self.player.jump_count = 0
                        player_on_ground = True
                        
                        if self.player.current_state in ["falling", "jumping"]:
                            self.player._change_state("idle")
                    else:
                        # Игрок снизу платформы (удар головой)
                        self.player.physics_body.position.y = platform_rect.bottom + self.player.size.y / 2 + collision_buffer + player_y_offset
                        if self.player.physics_body.velocity.y < 0:
                            self.player.physics_body.velocity.y = 0
                
                break  # Обрабатываем только первую коллизию
        
        # Если игрок не касается ни одной платформы, он не на земле
        if not player_on_ground and self.player.is_grounded:
            # Проверим, действительно ли игрок не касается платформ
            # Создадим немного увеличенный прямоугольник для проверки
            check_rect = pygame.Rect(
                player_rect.x,
                player_rect.y,
                player_rect.width,
                player_rect.height + 8  # Увеличил с 5 до 8 пикселей для более стабильной проверки
            )
            
            still_grounded = False
            for platform in self.platforms:
                if check_rect.colliderect(platform['rect']):
                    still_grounded = True
                    break
            
            if not still_grounded:
                self.player.is_grounded = False
        
        # Обрабатываем коллизии волков
        self._handle_wolf_collisions()
    
    def _apply_gravity_to_player(self, delta_time: float) -> None:
        """Применяет гравитацию к игроку."""
        if not self.player:
            return
        
        # Гравитация: 980 пикселей/сек^2 (как в реальном мире)
        gravity = Vector2D(0, 980)
        
        # Применяем гравитацию только если игрок имеет gravity_scale > 0
        if self.player.physics_body.gravity_scale > 0:
            gravity_force = gravity * self.player.physics_body.gravity_scale * self.player.physics_body.mass
            self.player.physics_body.apply_force(gravity_force)
        
        # Интегрируем физику
        self.player.physics_body.integrate(delta_time, gravity)
    
    def _apply_gravity_to_wolf(self, wolf: Wolf, delta_time: float) -> None:
        """Применяет гравитацию к волку."""
        if not wolf:
            return
        
        # Гравитация: 980 пикселей/сек^2
        gravity = Vector2D(0, 980)
        
        # Применяем гравитацию
        if wolf.physics_body.gravity_scale > 0:
            gravity_force = gravity * wolf.physics_body.gravity_scale * wolf.physics_body.mass
            wolf.physics_body.apply_force(gravity_force)
        
        # Интегрируем физику
        wolf.physics_body.integrate(delta_time, gravity)
    
    def spawn_wolf(self, position: Vector2D = None) -> None:
        """Создает нового волка."""
        if position is None:
            # Спавним справа от игрока
            if self.player:
                position = Vector2D(self.player.physics_body.position.x + 300, 200)
            else:
                position = Vector2D(500, 200)
        
        wolf = Wolf(position)
        wolf.set_target(self.player)  # Устанавливаем игрока как цель
        self.wolves.append(wolf)
        
        print(f"Spawned wolf at {position}")
    
    def _handle_wolf_collisions(self) -> None:
        """Обрабатывает коллизии волков с платформами."""
        for wolf in self.wolves:
            if not wolf.health.is_alive:
                continue
            
            # Получаем позицию волка с учетом состояния
            wolf_rect = pygame.Rect(
                wolf.physics_body.position.x - wolf.size.x / 2,
                wolf.physics_body.position.y - wolf.size.y / 2,
                wolf.size.x,
                wolf.size.y
            )
            
            # Проверяем коллизию с платформами
            wolf_on_ground = False
            
            for platform in self.platforms:
                platform_rect = platform['rect']
                
                if wolf_rect.colliderect(platform_rect):
                    # Определяем перекрытие
                    overlap_x = min(wolf_rect.right, platform_rect.right) - max(wolf_rect.left, platform_rect.left)
                    overlap_y = min(wolf_rect.bottom, platform_rect.bottom) - max(wolf_rect.top, platform_rect.top)
                    
                    collision_buffer = 2.0
                    
                    if overlap_x < overlap_y and overlap_x > 1:
                        # Горизонтальная коллизия
                        if wolf_rect.centerx < platform_rect.centerx:
                            wolf.physics_body.position.x = platform_rect.left - wolf.size.x / 2 - collision_buffer
                        else:
                            wolf.physics_body.position.x = platform_rect.right + wolf.size.x / 2 + collision_buffer
                        wolf.physics_body.velocity.x = 0
                    else:
                        # Вертикальная коллизия
                        if wolf_rect.centery < platform_rect.centery:
                            # Волк сверху платформы
                            wolf.physics_body.position.y = platform_rect.top - wolf.size.y / 2 - collision_buffer
                            wolf.physics_body.velocity.y = 0
                            wolf.is_grounded = True
                            wolf_on_ground = True
                        else:
                            # Волк снизу платформы
                            wolf.physics_body.position.y = platform_rect.bottom + wolf.size.y / 2 + collision_buffer
                            if wolf.physics_body.velocity.y < 0:
                                wolf.physics_body.velocity.y = 0
                    
                    break
            
            # Если волк не касается платформ
            if not wolf_on_ground and wolf.is_grounded:
                check_rect = pygame.Rect(
                    wolf_rect.x,
                    wolf_rect.y,
                    wolf_rect.width,
                    wolf_rect.height + 8
                )
                
                still_grounded = False
                for platform in self.platforms:
                    if check_rect.colliderect(platform['rect']):
                        still_grounded = True
                        break
                
                if not still_grounded:
                    wolf.is_grounded = False
            
    def render(self, surface: pygame.Surface) -> None:
        """Render playing state."""
        # Sky gradient background
        RenderUtils.draw_gradient_background(surface, Colors.SKY_BLUE, Colors.CORNFLOWER_BLUE,
                                           self.window_width, self.window_height)
        
        # Render simple platforms
        self._render_platforms(surface)
        
        # Render player
        if self.player:
            self.player.render(surface)
        
        # Render wolves
        for wolf in self.wolves:
            wolf.render(surface)
        
        # Render combat debug info
        if GameConfig.SHOW_DEBUG_INFO and self.player:
            self.combat_system.render_attack_area(surface, self.player, self.player.weapon, debug=True)
            
        # Render UI panels
        if GameConfig.SHOW_DEBUG_INFO:
            self._render_debug_panel(surface)
        self._render_instructions_panel(surface)
    
    def _create_simple_platforms(self) -> None:
        """Создает простые платформы."""
        from game.physics import PhysicsBody
        from game.collision import Collider, CollisionLayer
        
        # Платформа данные: (x, y, width, height, color)
        platform_data = [
            (0, 550, 1280, 120, Colors.PLATFORM_BROWN),      # Нижняя земля - поднял еще выше
            (300, 450, 200, 20, (100, 100, 100)),            # Средняя платформа - поднял выше
            (600, 350, 200, 20, (100, 100, 100)),            # Высокая платформа - поднял выше
            (900, 250, 200, 20, (100, 100, 100)),            # Очень высокая платформа - поднял выше
        ]
        
        for i, (x, y, width, height, color) in enumerate(platform_data):
            # Создаем физическое тело
            physics_body = PhysicsBody(
                position=Vector2D(x + width/2, y + height/2),
                velocity=Vector2D.zero(),
                acceleration=Vector2D.zero(),
                mass=float('inf')
            )
            
            # Создаем коллайдер
            collider = Collider(
                physics_body=physics_body,
                size=Vector2D(width, height),
                layer=CollisionLayer.PLATFORM,
                is_trigger=False
            )
            
            # Добавляем в систему коллизий
            self.collision_system.add_collider(collider)
            
            # Сохраняем для рендеринга
            self.platforms.append({
                'rect': pygame.Rect(x, y, width, height),
                'color': color
            })
    
    def _render_platforms(self, surface: pygame.Surface) -> None:
        """Рендерит платформы."""
        for platform in self.platforms:
            pygame.draw.rect(surface, platform['color'], platform['rect'])
            # Рисуем границу
            pygame.draw.rect(surface, Colors.BLACK, platform['rect'], 2)
        
        # Отладка: рисуем коллайдеры
        if GameConfig.SHOW_DEBUG_INFO:
            from game.collision import CollisionLayer
            for collider in self.collision_system.colliders:
                if collider.layer == CollisionLayer.PLATFORM:
                    bounds = collider.get_bounds()
                    pygame.draw.rect(surface, Colors.RED, bounds, 2)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle playing state events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True  # Signal to go to menu
            elif event.key == pygame.K_F1:
                # Спавним волка
                self.spawn_wolf()
                return False
                
        # Pass events to input manager
        if self.input_manager:
            self.input_manager.handle_event(event)
            
        return False
    
    def _render_debug_panel(self, surface: pygame.Surface) -> None:
        """Render debug information panel."""
        if not self.player:
            return
        
        # Create panel using utility
        panel_width = 300
        panel_height = 200
        panel_surface = RenderUtils.create_panel(panel_width, panel_height, Colors.BLACK, Colors.DARK_GRAY)
        
        # Add debug text
        font = pygame.font.Font(None, FontSizes.SMALL)
        y_offset = 10
        
        # Player debug info
        for key, value in self.player.debug_info.items():
            text = font.render(f"{key}: {value}", True, Colors.WHITE)
            panel_surface.blit(text, (10, y_offset))
            y_offset += 18
        
        # Input debug info
        if self.input_manager:
            input_debug = self.input_manager.get_debug_info()
            text = font.render("--- Input ---", True, Colors.YELLOW)
            panel_surface.blit(text, (10, y_offset))
            y_offset += 18
            
            for key, value in input_debug['keyboard'].items():
                if key in ['horizontal', 'jump', 'crouch']:
                    text = font.render(f"{key}: {value}", True, Colors.LIGHT_GRAY)
                    panel_surface.blit(text, (10, y_offset))
                    y_offset += 18
        
        # Blit panel to screen
        surface.blit(panel_surface, (10, 10))
    
    def _render_instructions_panel(self, surface: pygame.Surface) -> None:
        """Render instructions panel."""
        # Create panel using utility
        panel_width = 250
        panel_height = 120
        panel_surface = RenderUtils.create_panel(panel_width, panel_height, (0, 0, 50), (100, 150, 255))
        
        # Add title
        font_title = pygame.font.Font(None, FontSizes.MEDIUM)
        font_text = pygame.font.Font(None, FontSizes.SMALL)
        
        title = font_title.render("Controls", True, Colors.WHITE)
        panel_surface.blit(title, (10, 10))
        
        # Instructions
        instructions = [
            "WASD/Arrows: Move",
            "SPACE/W/Up: Jump", 
            "S/Down: Crouch",
            "LMB: Attack",
            "F1: Spawn Wolf",
            "ESC: Menu"
        ]
        
        y_offset = 35
        for instruction in instructions:
            text = font_text.render(instruction, True, Colors.LIGHT_GRAY)
            panel_surface.blit(text, (10, y_offset))
            y_offset += 20
        
        # Blit panel to screen
        surface.blit(panel_surface, (self.window_width - panel_width - 10, 
                                   self.window_height - panel_height - 10))


class PausedState(IGameState):
    """Paused state implementation."""
    
    def __init__(self, window_width: int, window_height: int):
        self.window_width = window_width
        self.window_height = window_height
        
    def enter(self, previous_state: Optional[GameState], data: Dict[str, Any] = None) -> None:
        """Enter paused state."""
        pass
        
    def exit(self, next_state: GameState) -> Dict[str, Any]:
        """Exit paused state."""
        return {}
        
    def update(self, delta_time: float) -> None:
        """Update paused state."""
        pass
        
    def render(self, surface: pygame.Surface) -> None:
        """Render paused state."""
        surface.fill(Colors.DARK_GRAY)
        
        font = pygame.font.Font(None, FontSizes.LARGE + 4)
        text = font.render("PAUSED", True, Colors.WHITE)
        text_rect = text.get_rect(center=(self.window_width // 2, self.window_height // 2))
        surface.blit(text, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle paused state events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True  # Signal to resume
        return False


class GameStateManager:
    """
    Centralized game state manager following Single Responsibility Principle.
    This is the single source of truth for game state.
    """
    
    def __init__(self, window_width: int, window_height: int):
        self.window_width = window_width
        self.window_height = window_height
        
        # State instances (Open/Closed Principle - easy to add new states)
        self.states: Dict[GameState, IGameState] = {
            GameState.MENU: MenuState(window_width, window_height),
            GameState.PLAYING: PlayingState(window_width, window_height),
            GameState.PAUSED: PausedState(window_width, window_height)
        }
        
        # Current state management
        self.current_state = GameState.MENU
        self.previous_state = None
        self.state_data = {}
        
        # Valid transitions (Liskov Substitution Principle - states are interchangeable)
        self.valid_transitions = {
            GameState.MENU: [GameState.PLAYING],
            GameState.PLAYING: [GameState.PAUSED, GameState.MENU],
            GameState.PAUSED: [GameState.PLAYING, GameState.MENU]
        }
        
        # Event callbacks
        self.state_change_callbacks: list[Callable[[GameState, GameState], None]] = []
        
    def add_state_change_callback(self, callback: Callable[[GameState, GameState], None]) -> None:
        """Add callback for state changes."""
        self.state_change_callbacks.append(callback)
        
    def set_game_objects(self, player, collision_system, input_manager):
        """Inject game objects into playing state."""
        playing_state = self.states[GameState.PLAYING]
        if isinstance(playing_state, PlayingState):
            playing_state.set_game_objects(player, collision_system, input_manager)
    
    def can_transition_to(self, new_state: GameState) -> bool:
        """Check if transition is valid."""
        return new_state in self.valid_transitions.get(self.current_state, [])
    
    def transition_to(self, new_state: GameState, data: Dict[str, Any] = None) -> bool:
        """Transition to new state."""
        if not self.can_transition_to(new_state):
            return False
        
        # Get current and new state instances
        current_state_instance = self.states[self.current_state]
        new_state_instance = self.states[new_state]
        
        # Exit current state
        exit_data = current_state_instance.exit(new_state)
        
        # Update state tracking
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Merge exit data with provided data
        combined_data = {**(data or {}), **exit_data}
        
        # Enter new state
        new_state_instance.enter(self.previous_state, combined_data)
        
        # Notify callbacks
        for callback in self.state_change_callbacks:
            callback(self.previous_state, self.current_state)
        
        return True
    
    def get_current_state(self) -> GameState:
        """Get current state."""
        return self.current_state
    
    def update(self, delta_time: float) -> None:
        """Update current state."""
        current_state_instance = self.states[self.current_state]
        current_state_instance.update(delta_time)
    
    def render(self, surface: pygame.Surface) -> None:
        """Render current state."""
        current_state_instance = self.states[self.current_state]
        current_state_instance.render(surface)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events for current state."""
        current_state_instance = self.states[self.current_state]
        
        # Let state handle the event
        handled = current_state_instance.handle_event(event)
        
        # Handle state transitions based on return value
        if handled:
            if self.current_state == GameState.MENU:
                self.transition_to(GameState.PLAYING)
            elif self.current_state == GameState.PLAYING:
                self.transition_to(GameState.MENU)
            elif self.current_state == GameState.PAUSED:
                self.transition_to(GameState.PLAYING)