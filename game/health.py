"""
Health System Module
Система здоровья для игры
"""

import pygame
from typing import Optional, Callable
from game.physics import Vector2D
from game.utils import Colors


class HealthComponent:
    """Компонент здоровья для игровых объектов."""
    
    def __init__(self, max_health: int = 100, current_health: Optional[int] = None):
        self.max_health = max_health
        self.current_health = current_health if current_health is not None else max_health
        
        # Callbacks
        self.on_damage: Optional[Callable[[int, int], None]] = None  # (damage, remaining_health)
        self.on_heal: Optional[Callable[[int, int], None]] = None    # (heal_amount, new_health)
        self.on_death: Optional[Callable[[], None]] = None
        
        # Состояние
        self.is_alive = True
        self.is_invulnerable = False
        self.invulnerability_timer = 0.0
        
    def take_damage(self, damage: int) -> bool:
        """
        Получить урон.
        
        Args:
            damage: Количество урона
            
        Returns:
            True если объект еще жив
        """
        if not self.is_alive or self.is_invulnerable or damage <= 0:
            return self.is_alive
        
        self.current_health = max(0, self.current_health - damage)
        
        if self.on_damage:
            self.on_damage(damage, self.current_health)
        
        if self.current_health <= 0:
            self.is_alive = False
            if self.on_death:
                self.on_death()
        
        return self.is_alive
    
    def heal(self, amount: int) -> None:
        """
        Восстановить здоровье.
        
        Args:
            amount: Количество восстановления
        """
        if not self.is_alive or amount <= 0:
            return
        
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        
        if self.on_heal and self.current_health > old_health:
            self.on_heal(amount, self.current_health)
    
    def set_invulnerable(self, duration: float) -> None:
        """
        Сделать неуязвимым на время.
        
        Args:
            duration: Длительность неуязвимости в секундах
        """
        self.is_invulnerable = True
        self.invulnerability_timer = duration
    
    def update(self, delta_time: float) -> None:
        """Обновить состояние здоровья."""
        if self.is_invulnerable:
            self.invulnerability_timer -= delta_time
            if self.invulnerability_timer <= 0:
                self.is_invulnerable = False
                self.invulnerability_timer = 0
    
    def get_health_percentage(self) -> float:
        """Получить процент здоровья (0.0 - 1.0)."""
        return self.current_health / self.max_health if self.max_health > 0 else 0.0
    
    def is_full_health(self) -> bool:
        """Проверить полное ли здоровье."""
        return self.current_health >= self.max_health
    
    def reset(self) -> None:
        """Сбросить здоровье к максимуму."""
        self.current_health = self.max_health
        self.is_alive = True
        self.is_invulnerable = False
        self.invulnerability_timer = 0


class HealthBar:
    """Полоска здоровья для отображения над объектами."""
    
    def __init__(self, width: int = 40, height: int = 6):
        self.width = width
        self.height = height
        self.offset_y = -15  # Смещение над объектом
        
        # Цвета
        self.bg_color = Colors.BLACK
        self.border_color = Colors.WHITE
        self.health_color = Colors.GREEN
        self.damage_color = Colors.RED
        self.warning_color = Colors.YELLOW
        
        # Пороги для изменения цвета
        self.warning_threshold = 0.3  # 30% - желтый
        self.danger_threshold = 0.15  # 15% - красный
    
    def render(self, surface: pygame.Surface, position: Vector2D, health_component: HealthComponent, 
               camera_offset: Vector2D = None) -> None:
        """
        Отрисовать полоску здоровья.
        
        Args:
            surface: Поверхность для рисования
            position: Позиция объекта
            health_component: Компонент здоровья
            camera_offset: Смещение камеры
        """
        if not health_component.is_alive:
            return
        
        if camera_offset is None:
            camera_offset = Vector2D.zero()
        
        # Вычисляем позицию полоски
        screen_pos = position - camera_offset
        bar_x = int(screen_pos.x - self.width // 2)
        bar_y = int(screen_pos.y + self.offset_y)
        
        # Фон полоски
        bg_rect = pygame.Rect(bar_x - 1, bar_y - 1, self.width + 2, self.height + 2)
        pygame.draw.rect(surface, self.border_color, bg_rect)
        
        bg_rect = pygame.Rect(bar_x, bar_y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, bg_rect)
        
        # Полоска здоровья
        health_percentage = health_component.get_health_percentage()
        health_width = int(self.width * health_percentage)
        
        if health_width > 0:
            # Выбираем цвет в зависимости от количества здоровья
            if health_percentage > self.warning_threshold:
                color = self.health_color
            elif health_percentage > self.danger_threshold:
                color = self.warning_color
            else:
                color = self.damage_color
            
            # Мигание при низком здоровье
            if health_percentage <= self.danger_threshold:
                # Простое мигание
                import time
                if int(time.time() * 4) % 2:  # 4 раза в секунду
                    color = self.damage_color
                else:
                    color = (100, 0, 0)  # Темно-красный
            
            health_rect = pygame.Rect(bar_x, bar_y, health_width, self.height)
            pygame.draw.rect(surface, color, health_rect)
        
        # Эффект неуязвимости
        if health_component.is_invulnerable:
            # Белая обводка при неуязвимости
            border_rect = pygame.Rect(bar_x - 2, bar_y - 2, self.width + 4, self.height + 4)
            pygame.draw.rect(surface, Colors.WHITE, border_rect, 2)