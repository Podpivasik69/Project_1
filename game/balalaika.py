"""
Balalaika Projectile System
Система снарядов балалайки для медведя-босса
"""

import pygame
import math
from game.physics import Vector2D
from game.assets import asset_manager


class BalalaikaProjectile:
    """Снаряд балалайки медведя-босса."""
    
    def __init__(self, start_x: float, start_y: float, target_x: float, target_y: float):
        """
        Создает снаряд балалайки.
        
        Args:
            start_x: Начальная позиция X (медведь)
            start_y: Начальная позиция Y (медведь)
            target_x: Целевая позиция X (игрок в момент броска)
            target_y: Целевая позиция Y (игрок в момент броска)
        """
        self.start_pos = Vector2D(start_x, start_y)
        self.target_pos = Vector2D(target_x, target_y)
        self.position = Vector2D(start_x, start_y)
        
        # ПАРАМЕТРЫ
        self.speed = 200  # пикселей/секунду
        self.damage = 10
        self.passes_through_platforms = True  # Проходит сквозь платформы
        self.active = True
        
        # Размер для коллизий
        self.width = 48
        self.height = 32
        
        # Вычисляем направление движения
        self._calculate_velocity()
        
        # Загружаем спрайт
        self.sprite = self._load_sprite()
    
    def _calculate_velocity(self):
        """Вычисляет скорость движения к цели."""
        # Вектор от старта к цели
        direction = Vector2D(
            self.target_pos.x - self.start_pos.x,
            self.target_pos.y - self.start_pos.y
        )
        
        # Нормализуем и умножаем на скорость
        distance = math.sqrt(direction.x ** 2 + direction.y ** 2)
        if distance > 0:
            self.velocity = Vector2D(
                (direction.x / distance) * self.speed,
                (direction.y / distance) * self.speed
            )
        else:
            self.velocity = Vector2D(0, 0)
    
    def _load_sprite(self) -> pygame.Surface:
        """Загружает спрайт балалайки."""
        sprite = asset_manager.load_image("assets/balalaika.png", (self.width, self.height))
        
        if not sprite:
            # Создаем placeholder если нет текстуры
            sprite = asset_manager.create_placeholder(
                (self.width, self.height), 
                (139, 69, 19),  # Коричневый (дерево)
                "♪"
            )
        
        return sprite
    
    def update(self, delta_time: float):
        """Обновляет снаряд - линейное движение к цели."""
        if not self.active:
            return
        
        # Линейное движение к target_pos
        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time
        
        # Проверяем, не улетел ли слишком далеко
        distance_from_start = math.sqrt(
            (self.position.x - self.start_pos.x) ** 2 + 
            (self.position.y - self.start_pos.y) ** 2
        )
        
        if distance_from_start > 1000:
            self.active = False
    
    def get_rect(self) -> pygame.Rect:
        """Возвращает прямоугольник для коллизий."""
        return pygame.Rect(
            int(self.position.x - self.width // 2),
            int(self.position.y - self.height // 2),
            self.width,
            self.height
        )
    
    def check_player_collision(self, player_rect: pygame.Rect) -> bool:
        """
        Проверяет столкновение с игроком.
        
        Args:
            player_rect: Прямоугольник игрока
            
        Returns:
            True если попал в игрока
        """
        if not self.active:
            return False
        
        balalaika_rect = self.get_rect()
        
        if balalaika_rect.colliderect(player_rect):
            self.active = False
            return True
        
        return False
    
    def draw(self, surface: pygame.Surface, camera_offset: Vector2D = None):
        """Рисует балалайку."""
        if not self.active:
            return
        
        if camera_offset is None:
            camera_offset = Vector2D(0, 0)
        
        # Рендерим
        render_pos = (
            int(self.position.x - camera_offset.x - self.width // 2),
            int(self.position.y - camera_offset.y - self.height // 2)
        )
        surface.blit(self.sprite, render_pos)
    
    @property
    def x(self) -> float:
        """Возвращает X координату."""
        return self.position.x
    
    @property
    def y(self) -> float:
        """Возвращает Y координату."""
        return self.position.y