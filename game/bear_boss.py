"""
Bear Boss System
Система медведя-босса
"""

import pygame
import random
import math
from typing import Dict, Optional
from game.physics import Vector2D
from game.assets import asset_manager
from game.balalaika import BalalaikaProjectile


class BearBoss:
    """Медведь-босс с ИИ и атаками."""
    
    def __init__(self, start_x: float, start_y: float, size: Vector2D = None):
        if size is None:
            size = Vector2D(96, 80)  # Крупнее обычных врагов
        
        self.position = Vector2D(start_x, start_y)
        self.velocity = Vector2D(0, 0)
        self.size = size
        
        # Физические параметры
        self.move_speed = 60.0  # Медленнее волка
        self.gravity = 980.0
        self.friction = 0.8
        
        # Состояние
        self.is_grounded = False
        self.facing_right = False  # Смотрит влево (к игроку)
        self.state = "idle"  # "idle", "chase", "attack", "throw"
        
        # Боевые параметры
        self.health = 100
        self.max_health = 100
        self.damage_melee = 20  # Удар лапой
        self.damage_balalaika = 10  # Балалайка
        self.is_dead = False
        
        # Таймеры атак
        self.attack_cooldown = 2.0  # секунды
        self.balalaika_cooldown = 3.0  # секунды
        self.last_attack_time = 0.0
        self.last_balalaika_time = 0.0
        
        # ИИ параметры
        self.detection_range = 400.0  # Дальше чем у волка
        self.chase_range = 300.0      # Начинает преследовать
        self.attack_range = 100.0     # Ближняя атака
        self.balalaika_chance = 0.3   # 30% шанс кинуть балалайку
        
        # Анимация
        self.animation_timer = 0.0
        self.animation_speed = 4.0  # Медленнее волка
        self.current_frame = 0
        
        # Цель
        self.target = None
        
        # Загружаем спрайты
        self.sprites = self._load_sprites()
    
    def _load_sprites(self) -> Dict[str, pygame.Surface]:
        """Загружает все спрайты медведя."""
        sprites = {}
        
        # Основные спрайты
        sprites['idle'] = asset_manager.get_bear_sprite('idle', (int(self.size.x), int(self.size.y)))
        sprites['walk'] = asset_manager.get_bear_sprite('walk', (int(self.size.x), int(self.size.y)))
        sprites['attack'] = asset_manager.get_bear_sprite('attack', (int(self.size.x), int(self.size.y)))
        
        # Если нет отдельных спрайтов, используем базовые
        if not sprites['walk']:
            sprites['walk'] = sprites['idle']
        if not sprites['attack']:
            sprites['attack'] = sprites['idle']
        
        return sprites
    
    def set_target(self, target):
        """Устанавливает цель для преследования."""
        self.target = target
    
    def update(self, delta_time: float, player_position: tuple = None):
        """Обновляет медведя-босса."""
        if self.is_dead:
            return
        
        # Обновляем таймеры
        self.last_attack_time += delta_time
        self.last_balalaika_time += delta_time
        
        # ИИ логика
        if self.target and player_position:
            self._update_ai(player_position)
        
        # Физика
        self._update_physics(delta_time)
        
        # Анимация
        self._update_animation(delta_time)
    
    def _update_ai(self, player_position: tuple):
        """Обновляет ИИ медведя."""
        player_x, player_y = player_position
        distance_to_player = math.sqrt(
            (player_x - self.position.x) ** 2 + 
            (player_y - self.position.y) ** 2
        )
        
        # Определяем направление к игроку
        if player_x < self.position.x:
            self.facing_right = False
        else:
            self.facing_right = True
        
        # Логика состояний
        if distance_to_player > self.chase_range:
            # Слишком далеко - стоим
            self.state = "idle"
            self.velocity.x = 0
            
        elif distance_to_player <= self.attack_range:
            # Близко - атакуем
            if self.last_attack_time >= self.attack_cooldown:
                self.state = "attack"
                self._attack_melee()
            else:
                self.state = "idle"
                self.velocity.x = 0
                
        else:
            # В зоне преследования
            if (self.last_balalaika_time >= self.balalaika_cooldown and 
                random.random() < self.balalaika_chance):
                # Кидаем балалайку
                self.state = "throw"
                return self._throw_balalaika(player_x, player_y)
            else:
                # Преследуем
                self.state = "chase"
                direction = 1 if player_x > self.position.x else -1
                self.velocity.x = direction * self.move_speed
        
        return None  # Нет балалайки
    
    def _update_physics(self, delta_time: float):
        """Обновляет физику медведя."""
        # Применяем трение
        if self.state != "chase":
            self.velocity.x *= self.friction
            if abs(self.velocity.x) < 10:
                self.velocity.x = 0
        
        # Гравитация
        if not self.is_grounded:
            self.velocity.y += self.gravity * delta_time
        
        # Обновляем позицию
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time
    
    def _update_animation(self, delta_time: float):
        """Обновляет анимацию."""
        if self.state in ["chase"]:
            self.animation_timer += delta_time * self.animation_speed
            self.current_frame = int(self.animation_timer) % 2  # Простая анимация ходьбы
        else:
            self.animation_timer = 0.0
            self.current_frame = 0
    
    def _attack_melee(self):
        """Выполняет ближнюю атаку."""
        if self.target and hasattr(self.target, 'take_damage'):
            # Проверяем, что игрок все еще в радиусе атаки
            distance = math.sqrt(
                (self.target.position.x - self.position.x) ** 2 + 
                (self.target.position.y - self.position.y) ** 2
            )
            
            if distance <= self.attack_range:
                self.target.take_damage(self.damage_melee)
                print("🐻 Медведь рычит и бьет лапой!")
                self.last_attack_time = 0.0
    
    def _throw_balalaika(self, target_x: float, target_y: float) -> Optional[BalalaikaProjectile]:
        """Кидает балалайку в игрока."""
        # Создаем снаряд балалайки
        balalaika = BalalaikaProjectile(
            self.position.x, 
            self.position.y - 20,  # Немного выше центра медведя
            target_x, 
            target_y
        )
        
        print("🎵 Медведь кинул балалайку!")
        self.last_balalaika_time = 0.0
        
        return balalaika
    
    def get_rect(self) -> pygame.Rect:
        """Возвращает прямоугольник коллизии."""
        return pygame.Rect(
            int(self.position.x), 
            int(self.position.y), 
            int(self.size.x), 
            int(self.size.y)
        )
    
    def take_damage(self, damage: int) -> bool:
        """Получает урон. Возвращает True если медведь умер."""
        if self.is_dead:
            return True
        
        self.health = max(0, self.health - damage)
        print(f"🐻 Медведь получил {damage} урона! Здоровье: {self.health}/{self.max_health}")
        
        if self.health <= 0:
            self.is_dead = True
            print("🐻💀 Медведь-босс повержен!")
            return True
        return False
    
    def render(self, surface: pygame.Surface, camera_offset: Vector2D = None):
        """Рендерит медведя."""
        if self.is_dead:
            return
        
        if camera_offset is None:
            camera_offset = Vector2D(0, 0)
        
        # Выбираем спрайт на основе состояния
        if self.state == "attack":
            sprite = self.sprites['attack']
        elif self.state in ["chase"]:
            sprite = self.sprites['walk']
        else:
            sprite = self.sprites['idle']
        
        # Отражаем спрайт в зависимости от направления
        if self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        
        # Рендерим
        render_pos = (
            int(self.position.x - camera_offset.x),
            int(self.position.y - camera_offset.y)
        )
        surface.blit(sprite, render_pos)
        
        # Рендерим полоску здоровья (больше чем у волка)
        self._render_health_bar(surface, camera_offset)
    
    def _render_health_bar(self, surface: pygame.Surface, camera_offset: Vector2D):
        """Рендерит полоску здоровья босса."""
        bar_width = 80  # Шире чем у волка
        bar_height = 10  # Выше чем у волка
        bar_x = int(self.position.x - camera_offset.x + (self.size.x - bar_width) / 2)
        bar_y = int(self.position.y - camera_offset.y - 20)
        
        # Фон полоски
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (100, 100, 100), bg_rect)
        
        # Здоровье
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        if health_width > 0:
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
            # Цвет зависит от здоровья (красный для босса)
            color = (255, 0, 0) if health_ratio < 0.3 else (255, 100, 0) if health_ratio < 0.6 else (255, 150, 0)
            pygame.draw.rect(surface, color, health_rect)
        
        # Рамка
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 2)
        
        # Надпись "BOSS"
        font = pygame.font.Font(None, 16)
        boss_text = font.render("BOSS", True, (255, 255, 255))
        surface.blit(boss_text, (bar_x, bar_y - 15))
    
    def check_platform_collision(self, platform_rect: pygame.Rect):
        """Проверяет коллизию с платформой."""
        bear_rect = self.get_rect()
        
        if bear_rect.colliderect(platform_rect):
            # Определяем сторону коллизии
            overlap_left = bear_rect.right - platform_rect.left
            overlap_right = platform_rect.right - bear_rect.left
            overlap_top = bear_rect.bottom - platform_rect.top
            overlap_bottom = platform_rect.bottom - bear_rect.top
            
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
                # Столкновение слева - останавливаемся
                self.position.x = platform_rect.left - self.size.x
                self.velocity.x = 0
            elif min_overlap == overlap_right and self.velocity.x < 0:
                # Столкновение справа - останавливаемся
                self.position.x = platform_rect.right
                self.velocity.x = 0