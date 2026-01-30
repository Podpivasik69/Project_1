"""
Simple Wolf Enemy Module
Simplified wolf enemy for minimal working platformer
"""

import pygame
import math
from typing import Dict
from game.physics import Vector2D
from game.assets import asset_manager


class SimpleWolf:
    """Простой враг-волк с базовым ИИ."""
    
    def __init__(self, start_position: Vector2D, size: Vector2D = None):
        if size is None:
            size = Vector2D(64, 48)
        
        self.position = Vector2D(start_position.x, start_position.y)
        self.velocity = Vector2D(0, 0)
        self.size = size
        
        # Физические параметры
        self.move_speed = 80.0
        self.gravity = 980.0
        self.friction = 0.8
        
        # Состояние
        self.is_grounded = False
        self.facing_right = True
        self.current_state = "idle"
        
        # ИИ
        self.detection_range = 200.0
        self.attack_range = 60.0
        self.attack_damage = 10  # Уменьшил с 15 до 10
        self.attack_cooldown = 2.0  # Увеличил с 1.5 до 2.0
        self.last_attack_time = 0.0
        
        # Патрулирование
        self.patrol_start = start_position.x
        self.patrol_range = 150.0
        self.patrol_direction = 1
        
        # Анимация
        self.animation_timer = 0.0
        self.animation_speed = 6.0
        self.walk_frames = [0, 1, 3, 4, 5, 6]  # доступные кадры ходьбы волка
        self.current_frame = 0
        
        # Здоровье
        self.health = 50
        self.max_health = 50
        self.is_dead = False
        
        # Цель
        self.target = None
        
        # Загружаем спрайты
        self.sprites = self._load_sprites()
    
    def _load_sprites(self) -> Dict[str, pygame.Surface]:
        """Загружает все спрайты волка."""
        sprites = {}
        
        # Основные спрайты
        sprites['idle'] = asset_manager.get_wolf_sprite('idle', (int(self.size.x), int(self.size.y)))
        sprites['attack'] = asset_manager.get_wolf_sprite('attack', (int(self.size.x), int(self.size.y)))
        
        # Кадры ходьбы
        for frame_num in self.walk_frames:
            sprites[f'walk_{frame_num}'] = asset_manager.get_wolf_walk_frame(
                frame_num, (int(self.size.x), int(self.size.y))
            )
        
        return sprites
    
    def set_target(self, target):
        """Устанавливает цель для преследования."""
        self.target = target
    
    def update(self, delta_time: float):
        """Обновляет волка."""
        if self.is_dead:
            return
        
        self.last_attack_time += delta_time
        
        # ИИ логика
        if self.target:
            distance_to_target = abs(self.target.position.x - self.position.x)
            
            if distance_to_target <= self.detection_range:
                # Преследуем цель
                if distance_to_target <= self.attack_range:
                    # Атакуем
                    self._attack_target(delta_time)
                else:
                    # Движемся к цели
                    self._move_towards_target()
            else:
                # Патрулируем
                self._patrol()
        else:
            # Патрулируем
            self._patrol()
        
        # Гравитация
        if not self.is_grounded:
            self.velocity.y += self.gravity * delta_time
        
        # Обновляем позицию
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time
        
        # Обновляем анимацию
        self._update_animation(delta_time)
    
    def _move_towards_target(self):
        """Движется к цели."""
        if not self.target:
            return
        
        direction = 1 if self.target.position.x > self.position.x else -1
        self.velocity.x = direction * self.move_speed
        
        # ИНВЕРТИРОВАННОЕ направление взгляда (волки ходят задом наперед)
        self.facing_right = self.velocity.x < 0  # Инвертировано!
        self.current_state = "walking"
    
    def _patrol(self):
        """Патрулирует территорию."""
        # Проверяем границы патрулирования
        if self.position.x <= self.patrol_start - self.patrol_range:
            self.patrol_direction = 1
        elif self.position.x >= self.patrol_start + self.patrol_range:
            self.patrol_direction = -1
        
        self.velocity.x = self.patrol_direction * self.move_speed * 0.5  # Медленнее при патрулировании
        
        # ИНВЕРТИРОВАННОЕ направление взгляда (волки ходят задом наперед)
        self.facing_right = self.velocity.x < 0  # Инвертировано!
        self.current_state = "walking"
    
    def _attack_target(self, delta_time: float):
        """Атакует цель."""
        self.velocity.x = 0
        self.current_state = "attacking"
        
        if self.last_attack_time >= self.attack_cooldown:
            if self.target and hasattr(self.target, 'take_damage'):
                # Проверяем, что цель все еще в радиусе атаки
                distance = abs(self.target.position.x - self.position.x)
                
                # Проверяем вертикальное расположение (не кусать сверху)
                wolf_center_y = self.position.y + self.size.y / 2
                target_center_y = self.target.position.y + self.target.size.y / 2
                vertical_distance = abs(wolf_center_y - target_center_y)
                
                # Проверяем, не находится ли игрок сверху волка
                target_bottom = self.target.position.y + self.target.size.y
                wolf_top = self.position.y
                player_above_wolf = target_bottom < wolf_top + 20
                
                # Атакуем только если:
                # 1. В радиусе атаки
                # 2. Примерно на одном уровне Y (±30px)
                # 3. Игрок не сверху волка
                if (distance <= self.attack_range and 
                    vertical_distance <= 30 and 
                    not player_above_wolf):
                    
                    self.target.take_damage(self.attack_damage)
                    print(f"🐺 Wolf attacks for {self.attack_damage} damage!")
            
            self.last_attack_time = 0.0
    
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
        """Рендерит волка."""
        if self.is_dead:
            return
        
        if camera_offset is None:
            camera_offset = Vector2D(0, 0)
        
        # Выбираем спрайт на основе состояния
        if self.current_state == "walking":
            # Анимация ходьбы для движения и патрулирования
            sprite_key = f'walk_{self.current_frame}'
            sprite = self.sprites.get(sprite_key, self.sprites['idle'])
        elif self.current_state == "attacking":
            # Для атаки используем статичный спрайт (или отдельную текстуру если есть)
            sprite = self.sprites['attack']
        else:
            # Idle - используем анимацию ходьбы (волки всегда в движении)
            sprite_key = f'walk_{self.current_frame}'
            sprite = self.sprites.get(sprite_key, self.sprites['idle'])
        
        # Отражаем спрайт в зависимости от направления движения
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
        bar_width = 50
        bar_height = 6
        bar_x = int(self.position.x - camera_offset.x + (self.size.x - bar_width) / 2)
        bar_y = int(self.position.y - camera_offset.y - 12)
        
        # Фон полоски
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (100, 100, 100), bg_rect)
        
        # Здоровье
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        if health_width > 0:
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            color = (255, 0, 0) if health_ratio < 0.3 else (255, 165, 0) if health_ratio < 0.6 else (255, 255, 0)
            pygame.draw.rect(surface, color, health_rect)
        
        # Рамка
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 1)
    
    def take_damage(self, damage: int) -> bool:
        """Получает урон. Возвращает True если волк умер."""
        if self.is_dead:
            return True
        
        self.health = max(0, self.health - damage)
        if self.health <= 0:
            self.is_dead = True
            print("🐺 Wolf defeated!")
            return True
        return False
    
    def check_platform_collision(self, platform_rect: pygame.Rect):
        """Проверяет коллизию с платформой."""
        wolf_rect = self.get_rect()
        
        if wolf_rect.colliderect(platform_rect):
            # Определяем сторону коллизии
            overlap_left = wolf_rect.right - platform_rect.left
            overlap_right = platform_rect.right - wolf_rect.left
            overlap_top = wolf_rect.bottom - platform_rect.top
            overlap_bottom = platform_rect.bottom - wolf_rect.top
            
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
                # Столкновение слева - разворачиваемся
                self.position.x = platform_rect.left - self.size.x
                self.velocity.x = 0
                self.patrol_direction = -1
            elif min_overlap == overlap_right and self.velocity.x < 0:
                # Столкновение справа - разворачиваемся
                self.position.x = platform_rect.right
                self.velocity.x = 0
                self.patrol_direction = 1