"""
Game States System
Система состояний игры (меню, игра, смерть)
"""

import pygame
from enum import Enum
from game.physics import Vector2D
from game.assets import asset_manager


class GameState(Enum):
    """Состояния игры."""
    MENU = "menu"
    PLAYING = "playing"
    DEATH = "death"
    PAUSED = "paused"


class MenuScreen:
    """Экран главного меню."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.background = None
        self.selected_option = 0
        self.menu_options = ["Start Game", "Exit"]
        
        # Загружаем фон меню
        self._load_background()
    
    def _load_background(self):
        """Загружает фон меню."""
        self.background = asset_manager.load_image("assets/background/menu_back.jpg")
        if not self.background:
            # Создаем fallback фон
            self.background = pygame.Surface((self.screen_width, self.screen_height))
            self.background.fill((20, 30, 50))  # Темно-синий
    
    def handle_input(self, keys_pressed: set, key_events: list) -> str:
        """
        Обрабатывает ввод в меню.
        
        Returns:
            Действие: "start_game", "exit", или None
        """
        for event in key_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_option == 0:
                        return "start_game"
                    elif self.selected_option == 1:
                        return "exit"
                elif event.key == pygame.K_ESCAPE:
                    return "exit"
        
        return None
    
    def render(self, surface: pygame.Surface):
        """Рендерит меню."""
        # Фон
        if self.background:
            bg_scaled = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
            surface.blit(bg_scaled, (0, 0))
        
        # Заголовок
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("Ingushetia Platformer", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        surface.blit(title_text, title_rect)
        
        # Опции меню
        option_font = pygame.font.Font(None, 48)
        start_y = self.screen_height // 2
        
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            option_text = option_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(self.screen_width // 2, start_y + i * 60))
            surface.blit(option_text, option_rect)
        
        # Инструкции
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "Use W/S or Arrow Keys to navigate",
            "Press ENTER or SPACE to select",
            "Press ESC to exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height - 100 + i * 25))
            surface.blit(text, text_rect)


class DeathScreen:
    """Экран смерти."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.selected_option = 0
        self.death_options = ["Restart", "Main Menu", "Exit"]
        self.death_timer = 0.0
    
    def handle_input(self, keys_pressed: set, key_events: list) -> str:
        """
        Обрабатывает ввод на экране смерти.
        
        Returns:
            Действие: "restart", "main_menu", "exit", или None
        """
        for event in key_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 1) % len(self.death_options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 1) % len(self.death_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_option == 0:
                        return "restart"
                    elif self.selected_option == 1:
                        return "main_menu"
                    elif self.selected_option == 2:
                        return "exit"
                elif event.key == pygame.K_r:
                    return "restart"
                elif event.key == pygame.K_ESCAPE:
                    return "main_menu"
        
        return None
    
    def update(self, delta_time: float):
        """Обновляет экран смерти."""
        self.death_timer += delta_time
    
    def render(self, surface: pygame.Surface):
        """Рендерит экран смерти."""
        # Полупрозрачный красный оверлей
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((100, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        # Заголовок смерти
        death_font = pygame.font.Font(None, 96)
        death_text = death_font.render("YOU DIED", True, (255, 50, 50))
        death_rect = death_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
        surface.blit(death_text, death_rect)
        
        # Мигающий эффект
        alpha = int(128 + 127 * abs(pygame.math.Vector2(1, 0).rotate(self.death_timer * 180).x))
        death_text.set_alpha(alpha)
        
        # Опции
        option_font = pygame.font.Font(None, 48)
        start_y = self.screen_height // 2 + 50
        
        for i, option in enumerate(self.death_options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            option_text = option_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(self.screen_width // 2, start_y + i * 60))
            surface.blit(option_text, option_rect)
        
        # Инструкции
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "Press R to restart quickly",
            "Use W/S to navigate, ENTER to select",
            "Press ESC for main menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, (200, 200, 200))
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height - 80 + i * 25))
            surface.blit(text, text_rect)


class ParallaxBackground:
    """Параллакс фон для основной игры."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.parallax_image = None
        self.parallax_x = 0.0
        self.parallax_speed = 0.3  # Скорость параллакса (30% от движения камеры)
        
        # Загружаем параллакс изображение
        self._load_parallax()
    
    def _load_parallax(self):
        """Загружает параллакс изображение."""
        self.parallax_image = asset_manager.load_image("assets/background/paralak.png")
        if not self.parallax_image:
            # Создаем fallback параллакс
            self.parallax_image = pygame.Surface((self.screen_width * 2, self.screen_height))
            # Градиент неба
            for y in range(self.screen_height):
                color_ratio = y / self.screen_height
                color = (
                    int(135 + (200 - 135) * color_ratio),  # Голубой к белому
                    int(206 + (220 - 206) * color_ratio),
                    int(235 + (255 - 235) * color_ratio)
                )
                pygame.draw.line(self.parallax_image, color, (0, y), (self.screen_width * 2, y))
    
    def update(self, camera_x: float):
        """Обновляет позицию параллакса на основе камеры."""
        self.parallax_x = camera_x * self.parallax_speed
    
    def render(self, surface: pygame.Surface):
        """Рендерит параллакс фон."""
        if not self.parallax_image:
            return
        
        # Масштабируем изображение под экран
        scaled_image = pygame.transform.scale(self.parallax_image, (self.screen_width * 2, self.screen_height))
        
        # Вычисляем позицию для бесшовного повтора
        image_width = scaled_image.get_width()
        offset_x = -int(self.parallax_x % image_width)
        
        # Рендерим изображение с повтором
        surface.blit(scaled_image, (offset_x, 0))
        if offset_x + image_width < self.screen_width:
            surface.blit(scaled_image, (offset_x + image_width, 0))