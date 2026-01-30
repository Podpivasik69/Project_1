"""
Shashka Projectile System
Система метания шашки для игры
"""

import pygame
from game.physics import Vector2D
from game.assets import asset_manager


class ShashkaProjectile:
    """Снаряд шашки с линейным движением."""
    
    def __init__(self, start_x: float, start_y: float, direction: int):
        """
        Создает снаряд шашки.
        
        Args:
            start_x: Начальная позиция X
            start_y: Начальная позиция Y  
            direction: Направление (1 = вправо, -1 = влево)
        """
        self.position = Vector2D(start_x, start_y)
        
        # ПАРАМЕТРЫ
        self.speed = 250  # пикселей/секунду (было 400)
        self.direction = direction
        self.velocity = Vector2D(self.speed * direction, 0)  # Только горизонтально
        
        # Свойства
        self.damage = 15  # урон (было 10)
        self.active = True
        self.lifetime = 0.0  # Для безопасности
        
        # Размер для коллизий (увеличен еще в 1.5 раза)
        self.width = 96   # было 64, стало 64 * 1.5 = 96
        self.height = 24  # было 16, стало 16 * 1.5 = 24
        
        # Загружаем спрайт
        self.sprite = self._load_sprite()
    
    def _load_sprite(self) -> pygame.Surface:
        """Загружает спрайт шашки."""
        sprite = asset_manager.get_weapon_sprite('shashka', (self.width, self.height))
        
        if not sprite:
            # Создаем placeholder если нет текстуры
            sprite = asset_manager.create_placeholder(
                (self.width, self.height), 
                (200, 200, 200),  # Серебристый
                "Ш"
            )
        
        return sprite
    
    def update(self, delta_time: float):
        """Обновляет снаряд - линейное движение БЕЗ гравитации."""
        if not self.active:
            return
        
        # Линейное движение: x += velocity.x * delta_time
        self.position.x += self.velocity.x * delta_time
        # Y НЕ изменяется - БЕЗ гравитации
        
        # Увеличиваем время жизни
        self.lifetime += delta_time
        
        # Деактивируем если слишком долго летит (на всякий случай)
        if self.lifetime > 5.0:
            self.active = False
    
    def draw(self, surface: pygame.Surface, camera_offset: Vector2D = None):
        """Рисует шашку с правильным направлением."""
        if not self.active:
            return
        
        if camera_offset is None:
            camera_offset = Vector2D(0, 0)
        
        sprite = self.sprite
        
        # Отражаем спрайт если летит влево
        if self.direction < 0:
            sprite = pygame.transform.flip(sprite, True, False)
        
        # Рендерим
        render_pos = (
            int(self.position.x - camera_offset.x - self.width // 2),
            int(self.position.y - camera_offset.y - self.height // 2)
        )
        surface.blit(sprite, render_pos)
    
    def get_rect(self) -> pygame.Rect:
        """Возвращает прямоугольник для коллизий."""
        return pygame.Rect(
            int(self.position.x - self.width // 2),
            int(self.position.y - self.height // 2),
            self.width,
            self.height
        )
    
    def check_collision(self, platforms) -> bool:
        """
        Проверяет столкновение с платформами.
        
        Args:
            platforms: Список платформ для проверки
            
        Returns:
            True если коснулся платформы
        """
        if not self.active:
            return False
        
        shashka_rect = self.get_rect()
        
        for platform in platforms:
            if shashka_rect.colliderect(platform.rect if hasattr(platform, 'rect') else platform):
                self.active = False
                return True
        
        return False
    
    def check_enemy_collision(self, enemies):
        """
        Проверяет столкновение с врагами.
        
        Args:
            enemies: Список врагов для проверки
            
        Returns:
            Врага при попадании или None
        """
        if not self.active:
            return None
        
        shashka_rect = self.get_rect()
        
        for enemy in enemies:
            enemy_rect = enemy.get_rect() if hasattr(enemy, 'get_rect') else pygame.Rect(
                int(enemy.position.x), int(enemy.position.y), 
                int(enemy.size.x), int(enemy.size.y)
            )
            
            if shashka_rect.colliderect(enemy_rect):
                self.active = False
                return enemy
        
        return None
    
    @property
    def x(self) -> float:
        """Возвращает X координату для проверки границ экрана."""
        return self.position.x
    
    @property
    def y(self) -> float:
        """Возвращает Y координату."""
        return self.position.y