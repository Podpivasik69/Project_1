"""
Simple Game Loop
Minimal working platformer with your textures and combat
"""

import asyncio
import pygame
import sys
from typing import List, Dict
from game.physics import Vector2D
from game.simple_player import SimplePlayer
from game.simple_wolf import SimpleWolf
from game.simple_combat import SimpleCombat
from game.assets import asset_manager


class Platform:
    """Простая платформа из блоков травы."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))
        self.grass_texture = None
        self.block_size = 64  # Размер одного блока травы
    
    def get_grass_texture(self):
        if self.grass_texture is None:
            self.grass_texture = asset_manager.load_image("assets/grass_ground.jpg", (self.block_size, self.block_size))
            if not self.grass_texture:
                # Fallback если нет текстуры
                self.grass_texture = asset_manager.create_placeholder((self.block_size, self.block_size), (139, 69, 19), "GRASS")
        return self.grass_texture
    
    def render(self, surface: pygame.Surface, camera_offset: Vector2D = None):
        if camera_offset is None:
            camera_offset = Vector2D(0, 0)
        
        grass_texture = self.get_grass_texture()
        
        # Рендерим платформу блоками травы
        blocks_x = int(self.rect.width // self.block_size) + 1
        blocks_y = int(self.rect.height // self.block_size) + 1
        
        for bx in range(blocks_x):
            for by in range(blocks_y):
                block_x = self.rect.x + bx * self.block_size
                block_y = self.rect.y + by * self.block_size
                
                # Обрезаем блок если он выходит за границы платформы
                clip_width = min(self.block_size, self.rect.right - block_x)
                clip_height = min(self.block_size, self.rect.bottom - block_y)
                
                if clip_width > 0 and clip_height > 0:
                    # Создаем обрезанную версию блока если нужно
                    if clip_width < self.block_size or clip_height < self.block_size:
                        clipped_texture = pygame.Surface((clip_width, clip_height))
                        clipped_texture.blit(grass_texture, (0, 0), (0, 0, clip_width, clip_height))
                        texture_to_render = clipped_texture
                    else:
                        texture_to_render = grass_texture
                    
                    render_pos = (
                        int(block_x - camera_offset.x),
                        int(block_y - camera_offset.y)
                    )
                    surface.blit(texture_to_render, render_pos)


class SimpleGame:
    """Простая игра-платформер."""
    
    def __init__(self):
        self.screen = None
        self.clock = None
        self.running = False
        self.delta_time = 0.0
        
        # Настройки
        self.WINDOW_WIDTH = 1024
        self.WINDOW_HEIGHT = 768
        self.TARGET_FPS = 60
        self.GRAVITY = 980.0
        
        # Игровые объекты
        self.player = None
        self.wolves = []
        self.platforms = []
        self.combat_system = SimpleCombat()
        
        # Фон
        self.background = None
        
        # Камера
        self.camera_position = Vector2D(0, 0)
        self.camera_smoothing = 5.0
        
        # Ввод
        self.keys_pressed = set()
        
        # Отладка
        self.debug_mode = False
    
    def initialize(self) -> bool:
        """Инициализирует игру."""
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            pygame.display.set_caption("Ingushetia Platformer - Simple Version")
            self.clock = pygame.time.Clock()
            self.running = True
            
            # Создаем игровые объекты
            self._create_game_objects()
            
            print("Simple game initialized!")
            print("Controls:")
            print("  WASD or Arrow Keys - Move")
            print("  SPACE - Jump")
            print("  X or CTRL - Attack")
            print("  Z - Throw Shashka")
            print("  F1 - Toggle debug mode")
            print("  ESC - Quit")
            
            return True
        except Exception as e:
            print(f"Failed to initialize game: {e}")
            return False
    
    def _create_game_objects(self):
        """Создает игровые объекты."""
        # Игрок
        self.player = SimplePlayer(Vector2D(100, 300))
        
        # Платформы
        self.platforms = [
            # Земля
            Platform(0, 600, 2000, 100),
            # Платформы для прыжков
            Platform(300, 500, 200, 20),
            Platform(600, 400, 200, 20),
            Platform(900, 300, 200, 20),
            Platform(1200, 450, 200, 20),
            # Стены
            Platform(-50, 0, 50, 800),  # Левая стена
            Platform(2000, 0, 50, 800),  # Правая стена
        ]
        
        # Волки
        self.wolves = [
            SimpleWolf(Vector2D(500, 550)),
            SimpleWolf(Vector2D(800, 350)),
            SimpleWolf(Vector2D(1300, 400)),
        ]
        
        # Устанавливаем игрока как цель для волков
        for wolf in self.wolves:
            wolf.set_target(self.player)
        
        # Загружаем фон
        self.background = asset_manager.get_background("sky")
    
    def handle_events(self):
        """Обрабатывает события."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode
                    print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
                elif event.key == pygame.K_r and len(self.wolves) == 0:
                    # Перезапуск игры
                    self._restart_game()
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
    
    def update(self, delta_time: float):
        """Обновляет игру."""
        # Обрабатываем ввод
        self._handle_input()
        
        # Обновляем игрока
        self.player.update(delta_time)
        
        # Проверяем коллизии игрока с платформами
        for platform in self.platforms:
            self.player.check_platform_collision(platform.rect)
        
        # Проверяем, стоит ли игрок на земле (после всех коллизий)
        platform_rects = [platform.rect for platform in self.platforms]
        if not self.player.check_if_on_ground(platform_rects) and self.player.is_grounded:
            # Игрок больше не на земле
            self.player.is_grounded = False
        
        # Обрабатываем шашки игрока
        for shashka in self.player.active_shashkas[:]:  # Копия списка
            shashka.update(delta_time)
            
            # Проверить столкновение с платформами
            if shashka.check_collision(self.platforms):
                self.player.active_shashkas.remove(shashka)
                print("💥 Шашка попала в платформу!")
                continue
            
            # Проверить столкновение с врагами
            hit_enemy = shashka.check_enemy_collision(self.wolves)
            if hit_enemy:
                # Наносим урон
                hit_enemy.take_damage(shashka.damage)
                self.player.active_shashkas.remove(shashka)
                print(f"🎯 Попадание! Урон: {shashka.damage}, здоровье врага: {hit_enemy.health}")
                
                # Проверить смерть волка
                if hit_enemy.health <= 0:
                    self.wolves.remove(hit_enemy)
                    print("💀 Волк убит шашкой!")
                continue
            
            # Проверить выход за экран
            if shashka.x < -100 or shashka.x > self.WINDOW_WIDTH + 100:
                self.player.active_shashkas.remove(shashka)
        
        # Обновляем волков
        for wolf in self.wolves[:]:  # Копия списка для безопасного удаления
            if wolf.is_dead:
                self.wolves.remove(wolf)
                continue
            
            wolf.update(delta_time)
            
            # Проверяем коллизии волка с платформами
            wolf.is_grounded = False
            for platform in self.platforms:
                wolf.check_platform_collision(platform.rect)
        
        # Обрабатываем атаки игрока
        if self.player.input_attack:
            hit_wolves = self.combat_system.perform_attack(self.player, self.wolves, delta_time)
        
        # Проверяем победу
        if len(self.wolves) == 0:
            self._show_victory_message()
        
        # Обновляем камеру
        self._update_camera(delta_time)
        
        # Проверяем границы мира
        self._check_world_bounds()
    
    def _handle_input(self):
        """Обрабатывает ввод."""
        # Горизонтальное движение
        horizontal = 0.0
        if pygame.K_a in self.keys_pressed or pygame.K_LEFT in self.keys_pressed:
            horizontal -= 1.0
        if pygame.K_d in self.keys_pressed or pygame.K_RIGHT in self.keys_pressed:
            horizontal += 1.0
        
        # Прыжок
        jump = (pygame.K_w in self.keys_pressed or 
                pygame.K_UP in self.keys_pressed or 
                pygame.K_SPACE in self.keys_pressed)
        
        # Атака
        attack = (pygame.K_x in self.keys_pressed or 
                 pygame.K_LCTRL in self.keys_pressed or
                 pygame.K_RCTRL in self.keys_pressed)
        
        # Метание шашки
        throw_shashka = pygame.K_z in self.keys_pressed
        
        self.player.set_input(horizontal, jump, attack, throw_shashka)
    
    def _update_camera(self, delta_time: float):
        """Обновляет позицию камеры."""
        # Следуем за игроком
        target_x = self.player.position.x - self.WINDOW_WIDTH // 2
        target_y = self.player.position.y - self.WINDOW_HEIGHT // 2
        
        # Плавное движение камеры
        self.camera_position.x += (target_x - self.camera_position.x) * self.camera_smoothing * delta_time
        self.camera_position.y += (target_y - self.camera_position.y) * self.camera_smoothing * delta_time
        
        # Ограничиваем камеру границами мира
        self.camera_position.x = max(0, min(self.camera_position.x, 2000 - self.WINDOW_WIDTH))
        self.camera_position.y = max(-200, min(self.camera_position.y, 700 - self.WINDOW_HEIGHT))
    
    def _check_world_bounds(self):
        """Проверяет границы мира."""
        # Если игрок упал слишком низко, возрождаем его
        if self.player.position.y > 800:
            self.player.position = Vector2D(100, 300)
            self.player.velocity = Vector2D(0, 0)
            self.player.health = self.player.max_health
            print("💀 Player respawned!")
    
    def _show_victory_message(self):
        """Показывает сообщение о победе."""
        if not hasattr(self, 'victory_shown'):
            self.victory_shown = True
            print("🎉 VICTORY! All wolves defeated!")
            print("🏆 You have defended Ingushetia!")
    
    def _render_victory_screen(self):
        """Рендерит экран победы."""
        if len(self.wolves) == 0:
            # Полупрозрачный оверлей
            overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            # Текст победы
            font_large = pygame.font.Font(None, 72)
            font_medium = pygame.font.Font(None, 48)
            
            victory_text = font_large.render("VICTORY!", True, (255, 215, 0))
            victory_rect = victory_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(victory_text, victory_rect)
            
            subtitle_text = font_medium.render("All wolves defeated!", True, (255, 255, 255))
            subtitle_rect = subtitle_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 20))
            self.screen.blit(subtitle_text, subtitle_rect)
            
            restart_text = font_medium.render("Press R to restart or ESC to quit", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 80))
            self.screen.blit(restart_text, restart_rect)
    
    def render(self):
        """Рендерит игру."""
        # Рендерим фон
        if self.background:
            # Масштабируем фон под размер экрана
            bg_scaled = pygame.transform.scale(self.background, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            self.screen.blit(bg_scaled, (0, 0))
        else:
            # Очищаем экран небесно-голубым цветом
            self.screen.fill((135, 206, 235))
        
        # Рендерим платформы
        for platform in self.platforms:
            platform.render(self.screen, self.camera_position)
        
        # Рендерим игрока
        self.player.render(self.screen, self.camera_position, self.debug_mode)
        
        # Рендерим шашки игрока
        self.player.render_shashkas(self.screen, self.camera_position)
        
        # Рендерим оружие игрока
        self.combat_system.render_weapon(self.screen, self.player, self.camera_position)
        
        # Рендерим волков
        for wolf in self.wolves:
            wolf.render(self.screen, self.camera_position)
        
        # Отладочная информация
        if self.debug_mode:
            self._render_debug_info()
        
        # Рендерим UI
        self._render_ui()
        
        # Рендерим экран победы если нужно
        self._render_victory_screen()
        
        # Обновляем экран
        pygame.display.flip()
    
    def _render_debug_info(self):
        """Рендерит отладочную информацию."""
        font = pygame.font.Font(None, 24)
        
        # Эффективное состояние "на земле"
        effective_on_ground = self.player.is_grounded and self.player.in_air_frames < 3
        
        debug_info = [
            f"Player Pos: ({self.player.position.x:.1f}, {self.player.position.y:.1f})",
            f"Player Vel: ({self.player.velocity.x:.1f}, {self.player.velocity.y:.1f})",
            f"Player State: {self.player.current_state}",
            f"Grounded: {self.player.is_grounded}",
            f"Effective Grounded: {effective_on_ground}",
            f"In Air Frames: {self.player.in_air_frames}",
            f"Wolves: {len(self.wolves)}",
            f"Camera: ({self.camera_position.x:.1f}, {self.camera_position.y:.1f})",
        ]
        
        y_offset = 50
        for info in debug_info:
            # Цветовая индикация проблем
            color = (255, 255, 255)
            if "Effective Grounded: False" in info and self.player.is_grounded:
                color = (255, 255, 0)  # Желтый - потенциальная проблема
            elif "In Air Frames:" in info and self.player.in_air_frames > 3 and self.player.is_grounded:
                color = (255, 150, 0)  # Оранжевый - нестабильность
            
            text_surface = font.render(info, True, color)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25
        
        # Рендерим области атаки
        self.combat_system.render_attack_area(self.screen, self.player, self.camera_position, True)
    
    def _render_ui(self):
        """Рендерит пользовательский интерфейс."""
        font = pygame.font.Font(None, 36)
        
        # FPS
        fps = self.clock.get_fps()
        fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 0))
        self.screen.blit(fps_text, (self.WINDOW_WIDTH - 150, 10))
        
        # Счетчик волков
        wolves_text = font.render(f"Wolves: {len(self.wolves)}", True, (255, 255, 255))
        self.screen.blit(wolves_text, (10, 10))
        
        # Здоровье игрока (большое)
        health_text = font.render(f"Health: {self.player.health}/{self.player.max_health}", True, (255, 255, 255))
        self.screen.blit(health_text, (self.WINDOW_WIDTH // 2 - 100, 10))
        
        # Количество шашек и восстановление
        shashkas_text = font.render(f"Shashkas: {self.player.shashka_count}/{self.player.MAX_SHASHKAS}", True, (255, 255, 255))
        self.screen.blit(shashkas_text, (10, 50))
        
        # Активные шашки в полете
        active_text = font.render(f"In flight: {len(self.player.active_shashkas)}", True, (200, 200, 200))
        self.screen.blit(active_text, (10, 75))
        
        # Кулдаун шашки
        if self.player.shashka_cooldown > 0:
            cooldown_text = font.render(f"Cooldown: {self.player.shashka_cooldown:.1f}s", True, (255, 255, 0))
            self.screen.blit(cooldown_text, (10, 100))
        
        # Восстановление шашек
        if self.player.shashka_count < self.player.MAX_SHASHKAS:
            regen_progress = self.player.shashka_regen_timer / self.player.SHASHKA_REGEN_TIME
            regen_text = font.render(f"Regen: {regen_progress*100:.0f}%", True, (0, 255, 255))
            self.screen.blit(regen_text, (10, 125))
            
            # Полоска прогресса восстановления
            bar_width = 100
            bar_height = 8
            bar_x = 150
            bar_y = 130
            
            # Фон полоски
            bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            pygame.draw.rect(self.screen, (100, 100, 100), bg_rect)
            
            # Прогресс
            progress_width = int(bar_width * regen_progress)
            if progress_width > 0:
                progress_rect = pygame.Rect(bar_x, bar_y, progress_width, bar_height)
                pygame.draw.rect(self.screen, (0, 255, 255), progress_rect)
            
            # Рамка
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 1)
    
    def _restart_game(self):
        """Перезапускает игру."""
        print("🔄 Restarting game...")
        self.victory_shown = False
        self._create_game_objects()
    
    async def run(self):
        """Основной игровой цикл."""
        if not self.initialize():
            return
        
        print("Starting simple game loop...")
        
        try:
            while self.running:
                # Вычисляем delta time
                self.delta_time = self.clock.tick(self.TARGET_FPS) / 1000.0
                
                # Обрабатываем события
                self.handle_events()
                
                # Обновляем игру
                self.update(self.delta_time)
                
                # Рендерим
                self.render()
                
                # Уступаем управление для async
                await asyncio.sleep(0)
                
        except KeyboardInterrupt:
            print("Game interrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Очищает ресурсы."""
        print("Cleaning up...")
        pygame.quit()


async def main():
    """Главная функция."""
    print("Starting Ingushetia Platformer - Simple Version")
    
    game = SimpleGame()
    await game.run()
    
    print("Game finished.")


if __name__ == "__main__":
    asyncio.run(main())