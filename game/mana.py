"""
Mana System Module
Система маны для магических способностей
"""

import pygame
from typing import Optional, Callable
from game.physics import Vector2D
from game.utils import Colors


class ManaComponent:
    """
    Компонент маны для магических способностей.
    """
    
    def __init__(self, max_mana: int = 100, current_mana: int = None, regen_rate: float = 10.0):
        self.max_mana = max_mana
        self.current_mana = current_mana if current_mana is not None else max_mana
        self.regen_rate = regen_rate  # Мана в секунду
        
        # Callbacks
        self.on_mana_spent: Optional[Callable[[int, int], None]] = None  # (spent, remaining)
        self.on_mana_restored: Optional[Callable[[int, int], None]] = None  # (restored, new_total)
        
        # Состояние
        self.regen_enabled = True
        self.regen_delay = 0.0  # Задержка после трат перед восстановлением
        self.regen_timer = 0.0
    
    def spend_mana(self, amount: int) -> bool:
        """
        Потратить ману.
        
        Args:
            amount: Количество маны для траты
            
        Returns:
            True если мана была потрачена успешно
        """
        if amount <= 0 or self.current_mana < amount:
            return False
        
        self.current_mana -= amount
        self.regen_timer = self.regen_delay  # Сброс таймера восстановления
        
        if self.on_mana_spent:
            self.on_mana_spent(amount, self.current_mana)
        
        return True
    
    def restore_mana(self, amount: int) -> int:
        """
        Восстановить ману.
        
        Args:
            amount: Количество маны для восстановления
            
        Returns:
            Фактически восстановленное количество
        """
        if amount <= 0:
            return 0
        
        old_mana = self.current_mana
        self.current_mana = min(self.max_mana, self.current_mana + amount)
        actual_restore = self.current_mana - old_mana
        
        if actual_restore > 0 and self.on_mana_restored:
            self.on_mana_restored(actual_restore, self.current_mana)
        
        return actual_restore
    
    def can_afford(self, cost: int) -> bool:
        """Проверить, хватает ли маны для способности."""
        return self.current_mana >= cost
    
    def get_mana_percentage(self) -> float:
        """Получить процент маны (0.0 - 1.0)."""
        return self.current_mana / self.max_mana if self.max_mana > 0 else 0.0
    
    def is_full_mana(self) -> bool:
        """Проверить полная ли мана."""
        return self.current_mana >= self.max_mana
    
    def set_max_mana(self, max_mana: int) -> None:
        """Установить максимальную ману."""
        if max_mana <= 0:
            return
        
        ratio = self.current_mana / self.max_mana if self.max_mana > 0 else 1.0
        self.max_mana = max_mana
        self.current_mana = min(self.current_mana, max_mana)
    
    def update(self, delta_time: float) -> None:
        """Обновить восстановление маны."""
        if not self.regen_enabled or self.regen_rate <= 0:
            return
        
        # Проверяем задержку восстановления
        if self.regen_timer > 0:
            self.regen_timer -= delta_time
            return
        
        # Восстанавливаем ману
        if self.current_mana < self.max_mana:
            regen_amount = self.regen_rate * delta_time
            self.restore_mana(int(regen_amount))


class ManaBar:
    """
    Полоска маны для отображения.
    """
    
    def __init__(self, width: int = 40, height: int = 6):
        self.width = width
        self.height = height
        self.offset_y = -25  # Смещение над полоской здоровья
        
        # Цвета
        self.bg_color = Colors.BLACK
        self.border_color = Colors.WHITE
        self.mana_color = (0, 100, 255)  # Синий
        self.low_mana_color = (100, 0, 200)  # Фиолетовый
        
        # Пороги
        self.low_threshold = 0.25  # 25% - низкая мана
    
    def render(self, surface: pygame.Surface, position: Vector2D, mana_component: ManaComponent,
               camera_offset: Vector2D = None) -> None:
        """
        Отрисовать полоску маны.
        
        Args:
            surface: Поверхность для рисования
            position: Позиция объекта
            mana_component: Компонент маны
            camera_offset: Смещение камеры
        """
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
        
        # Полоска маны
        mana_percentage = mana_component.get_mana_percentage()
        mana_width = int(self.width * mana_percentage)
        
        if mana_width > 0:
            # Выбираем цвет в зависимости от количества маны
            if mana_percentage > self.low_threshold:
                color = self.mana_color
            else:
                color = self.low_mana_color
            
            mana_rect = pygame.Rect(bar_x, bar_y, mana_width, self.height)
            pygame.draw.rect(surface, color, mana_rect)


class ProgressBar:
    """
    Универсальная полоска прогресса с градиентом.
    """
    
    def __init__(self, width: int = 200, height: int = 20):
        self.width = width
        self.height = height
        
        # Цвета градиента
        self.color_left = (255, 0, 0)    # Красный (низкий)
        self.color_mid = (255, 255, 0)   # Желтый (средний)
        self.color_right = (0, 255, 0)   # Зеленый (высокий)
        
        self.bg_color = (60, 60, 60)
        self.border_color = Colors.WHITE
        self.show_border = True
        self.show_text = True
        
        # Текст
        self.font_size = 16
        self.text_color = Colors.WHITE
    
    def get_gradient_color(self, percentage: float) -> tuple:
        """
        Получить цвет градиента для заданного процента.
        
        Args:
            percentage: Процент заполнения (0.0 - 1.0)
            
        Returns:
            RGB цвет
        """
        if percentage <= 0.5:
            # Интерполяция между левым и средним цветом
            ratio = percentage / 0.5
            r = int(self.color_left[0] * (1 - ratio) + self.color_mid[0] * ratio)
            g = int(self.color_left[1] * (1 - ratio) + self.color_mid[1] * ratio)
            b = int(self.color_left[2] * (1 - ratio) + self.color_mid[2] * ratio)
        else:
            # Интерполяция между средним и правым цветом
            ratio = (percentage - 0.5) / 0.5
            r = int(self.color_mid[0] * (1 - ratio) + self.color_right[0] * ratio)
            g = int(self.color_mid[1] * (1 - ratio) + self.color_right[1] * ratio)
            b = int(self.color_mid[2] * (1 - ratio) + self.color_right[2] * ratio)
        
        return (r, g, b)
    
    def render(self, surface: pygame.Surface, position: Vector2D, current_value: int, 
               max_value: int, text: str = None) -> None:
        """
        Отрисовать полоску прогресса.
        
        Args:
            surface: Поверхность для рисования
            position: Позиция центра полоски
            current_value: Текущее значение
            max_value: Максимальное значение
            text: Текст для отображения
        """
        if max_value <= 0:
            return
        
        # Вычисляем позицию
        bar_x = int(position.x - self.width // 2)
        bar_y = int(position.y - self.height // 2)
        
        # Фон
        bg_rect = pygame.Rect(bar_x, bar_y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, bg_rect)
        
        # Заполнение
        percentage = current_value / max_value
        fill_width = int(self.width * percentage)
        
        if fill_width > 0:
            color = self.get_gradient_color(percentage)
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, self.height)
            pygame.draw.rect(surface, color, fill_rect)
        
        # Рамка
        if self.show_border:
            pygame.draw.rect(surface, self.border_color, bg_rect, 2)
        
        # Текст
        if self.show_text:
            if text is None:
                text = f"{current_value}/{max_value}"
            
            font = pygame.font.Font(None, self.font_size)
            text_surface = font.render(text, True, self.text_color)
            text_rect = text_surface.get_rect(center=(position.x, position.y))
            surface.blit(text_surface, text_rect)