"""
Simple Player Module
Simplified player for minimal working platformer
"""

import pygame
from typing import Dict
from game.physics import Vector2D
from game.assets import asset_manager


class SimplePlayer:
    """Простой игрок с базовым управлением и анимацией."""
    
    def __init__(self, start_position: Vector2D, size: Vector2D = None):
        if size is None:
            size = Vector2D(48, 72)
        
        self.position = Vector2D(start_position.x, start_position.y)
        self.velocity = Vector2D(0, 0)
        self.size = size
        
        # Физические параметры
        self.move_speed = 200.0
        self.jump_force = 650.0
        self.gravity = 980.0
        self.friction = 0.85
        
        # Состояние
        self.is_grounded = False
        self.facing_right = True
        self.current_state = "idle"
        
        # Анимация
        self.animation_timer = 0.0
        self.animation_speed = 8.0  # кадров в секунду
        self.walk_frames = [0, 1, 2, 4, 5]  # доступные кадры ходьбы
        self.current_frame = 0
        
        # Здоровье
        self.health = 100
        self.max_health = 100
        
        # Ввод
        self.input_horizontal = 0.0
        self.input_jump = False
        self.input_attack = False
        
        # Загружаем спрайты
        self.sprites = self._load_sprites()
    
    def _load_sprites(self) -> Dict[str, pygame.Surface]:
        """Загружает все спрайты игрока."""
        sprites = {}
        
        # Основные спрайты
        sprites['idle'] = asset_manager.get_player_sprite('idle', (int(self.size.x), int(self.size.y)))
        sprites['jump'] = asset_manager.get_player_sprite('jump', (int(self.size.x), int(self.size.y)))
        sprites['crouch'] = asset_manager.get_player_sprite('crouch', (int(self.size.x), int(self.size.y)))
        
        # Кадры ходьбы
        for frame_num in self.walk_frames:
            sprites[f'walk_{frame_num}'] = asset_manager.get_walk_animation_frame_by_number(
                frame_num, (int(self.size.x), int(self.size.y))
            )
        
        return sprites
    
    def set_input(self, horizontal: float, jump: bool, attack: bool = False):
        """Устанавливает ввод игрока."""
        self.input_horizontal = max(-1.0, min(1.0, horizontal))
        self.input_jump = jump
        self.input_attack = attack
    
    def update(self, delta_time: float):
        """Обновляет игрока."""
        # Горизонтальное движение
        if self.input_horizontal != 0:
            self.velocity.x = self.input_horizontal * self.move_speed
            self.facing_right = self.input_horizontal > 0
        else:
            self.velocity.x *= self.friction
            if abs(self.velocity.x) < 10:
                self.velocity.x = 0
        
        # Прыжок
        if self.input_jump and self.is_grounded:
            self.velocity.y = -self.jump_force
            self.is_grounded = False
        
        # Гравитация
        if not self.is_grounded:
            self.velocity.y += self.gravity * delta_time
        
        # Обновляем позицию
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time
        
        # Определяем состояние на основе физики
        self._update_state()
        
        # Обновляем анимацию
        self._update_animation(delta_time)
    
    def _update_state(self):
        """Определяет текущее состояние игрока на основе физики."""
        # Проверяем вертикальное движение (приоритет)
        if self.velocity.y != 0 or not self.is_grounded:
            self.current_state = "jumping"  # Используем для прыжка и падения
        # Проверяем горизонтальное движение (только если на земле)
        elif self.velocity.x != 0 and self.is_grounded:
            self.current_state = "walking"
        # Состояние покоя (на земле и не движется)
        elif self.velocity.x == 0 and self.velocity.y == 0 and self.is_grounded:
            self.current_state = "idle"
        else:
            # Fallback на idle
            self.current_state = "idle"
    
    def _update_animation(self, delta_time: float):
        """Обновляет анимацию."""
        if self.current_state == "walking":
            self.animation_timer += delta_time * self.animation_speed
            frame_index = int(self.animation_timer) % len(self.walk_frames)
            self.current_frame = self.walk_frames[frame_index]
        else:
            self.animation_timer = 0.0
            self.current_frame = 0
    
    def get_rect(self) -> pygame.Rect:
        """Возвращает прямоугольник коллизии."""
        return pygame.Rect(
            int(self.position.x), 
            int(self.position.y), 
            int(self.size.x), 
            int(self.size.y)
        )
    
    def render(self, surface: pygame.Surface, camera_offset: Vector2D = None):
        """Рендерит игрока."""
        if camera_offset is None:
            camera_offset = Vector2D(0, 0)
        
        # Выбираем спрайт на основе состояния
        if self.current_state == "idle":
            # IDLE: только static.png когда стоит на месте
            sprite = self.sprites['idle']
        elif self.current_state == "walking":
            # ХОДЬБА: анимация walk/*.png только при движении по земле
            sprite_key = f'walk_{self.current_frame}'
            sprite = self.sprites.get(sprite_key, self.sprites['idle'])
        elif self.current_state == "jumping":
            # ПРЫЖОК/ПАДЕНИЕ: только jump.png при любом вертикальном движении
            sprite = self.sprites['jump']
        else:
            # Fallback
            sprite = self.sprites['idle']
        
        # Отражаем спрайт в зависимости от направления
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        
        # Рендерим
        render_pos = (
            int(self.position.x - camera_offset.x),
            int(self.position.y - camera_offset.y)
        )
        surface.blit(sprite, render_pos)
        
        # Рендерим полоску здоровья
        self._render_health_bar(surface, camera_offset)
    
    def _render_health_bar(self, surface: pygame.Surface, camera_offset: Vector2D):
        """Рендерит полоску здоровья."""
        bar_width = 60
        bar_height = 8
        bar_x = int(self.position.x - camera_offset.x + (self.size.x - bar_width) / 2)
        bar_y = int(self.position.y - camera_offset.y - 15)
        
        # Фон полоски
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (100, 100, 100), bg_rect)
        
        # Здоровье
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        if health_width > 0:
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            color = (255, 0, 0) if health_ratio < 0.3 else (255, 255, 0) if health_ratio < 0.6 else (0, 255, 0)
            pygame.draw.rect(surface, color, health_rect)
        
        # Рамка
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 1)
    
    def take_damage(self, damage: int) -> bool:
        """Получает урон. Возвращает True если игрок умер."""
        self.health = max(0, self.health - damage)
        return self.health <= 0
    
    def heal(self, amount: int):
        """Лечит игрока."""
        self.health = min(self.max_health, self.health + amount)
    
    def check_platform_collision(self, platform_rect: pygame.Rect):
        """Проверяет коллизию с платформой."""
        player_rect = self.get_rect()
        
        if player_rect.colliderect(platform_rect):
            # Определяем сторону коллизии
            overlap_left = player_rect.right - platform_rect.left
            overlap_right = platform_rect.right - player_rect.left
            overlap_top = player_rect.bottom - platform_rect.top
            overlap_bottom = platform_rect.bottom - player_rect.top
            
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            
            if min_overlap == overlap_top and self.velocity.y >= 0:
                # Приземление на платформу
                self.position.y = platform_rect.top - self.size.y
                self.velocity.y = 0
                self.is_grounded = True
            elif min_overlap == overlap_bottom and self.velocity.y < 0:
                # Удар головой о платформу
                self.position.y = platform_rect.bottom
                self.velocity.y = 0
            elif min_overlap == overlap_left and self.velocity.x > 0:
                # Столкновение слева
                self.position.x = platform_rect.left - self.size.x
                self.velocity.x = 0
            elif min_overlap == overlap_right and self.velocity.x < 0:
                # Столкновение справа
                self.position.x = platform_rect.right
                self.velocity.x = 0