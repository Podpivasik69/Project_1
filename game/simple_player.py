"""
Simple Player Module
Simplified player for minimal working platformer
"""

import pygame
from typing import Dict
from game.physics import Vector2D
from game.assets import asset_manager
from game.shashka import ShashkaProjectile


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
        
        # Стабилизация анимации
        self.in_air_frames = 0  # Счетчик кадров в воздухе
        
        # Система метания шашки
        self.active_shashkas = []  # Список активных шашек
        self.shashka_cooldown = 0.0  # Таймер задержки
        
        # Константы шашки
        self.SHASHKA_COOLDOWN = 0.5  # 500ms задержка
        self.MAX_SHASHKAS = 3        # макс 3 в полёте одновременно
        
        # Система восстановления шашек
        self.shashka_count = 3       # Текущее количество доступных шашек
        self.shashka_regen_timer = 0.0  # Таймер восстановления
        self.SHASHKA_REGEN_TIME = 2.0   # 2 секунды на восстановление одной шашки
        
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
        self.input_throw_shashka = False  # Новый ввод для метания шашки
        
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
    
    def set_input(self, horizontal: float, jump: bool, attack: bool = False, throw_shashka: bool = False):
        """Устанавливает ввод игрока."""
        self.input_horizontal = max(-1.0, min(1.0, horizontal))
        self.input_jump = jump
        self.input_attack = attack
        self.input_throw_shashka = throw_shashka
    
    def update(self, delta_time: float):
        """Обновляет игрока."""
        # Горизонтальное движение
        if self.input_horizontal != 0:
            self.velocity.x = self.input_horizontal * self.move_speed
            # Обновляем направление ТОЛЬКО при активном движении
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
        
        # СТАБИЛИЗАЦИЯ СТОЯНИЯ (буфер для устранения дрожания)
        if self.is_grounded and abs(self.velocity.y) < 0.5:
            self.velocity.y = 0  # Обнуляем микро-скорость
            self.in_air_frames = 0  # Счётчик кадров в воздухе
        else:
            self.in_air_frames += 1
        
        # Обновляем таймер шашки
        if self.shashka_cooldown > 0:
            self.shashka_cooldown -= delta_time
        
        # Обновляем систему восстановления шашек
        self._update_shashka_regeneration(delta_time)
        
        # Обрабатываем метание шашки
        self._handle_shashka_throwing()
        
        # Обновляем активные шашки
        self._update_shashkas(delta_time)
        
        # Определяем состояние на основе физики
        self._update_state()
        
        # Обновляем анимацию
        self._update_animation(delta_time)
    
    def check_if_on_ground(self, platforms):
        """Проверяет, стоит ли игрок на какой-либо платформе."""
        player_rect = self.get_rect()
        
        # Проверяем небольшую область под игроком
        ground_check_rect = pygame.Rect(
            player_rect.x + 5,  # Немного отступаем от краев
            player_rect.bottom,
            player_rect.width - 10,
            5  # Проверяем 5 пикселей вниз
        )
        
        for platform in platforms:
            if ground_check_rect.colliderect(platform):
                return True
        
        return False
    
    def _handle_shashka_throwing(self):
        """Обрабатывает метание шашки."""
        if (self.input_throw_shashka and 
            self.shashka_cooldown <= 0 and 
            self.shashka_count > 0 and  # Проверяем наличие шашек
            len(self.active_shashkas) < self.MAX_SHASHKAS):
            
            # Создать шашку из центра игрока
            player_rect = self.get_rect()
            start_x = player_rect.centerx + (40 * (1 if self.facing_right else -1))  # Было 20, стало 40
            start_y = player_rect.centery
            direction = 1 if self.facing_right else -1
            
            new_shashka = ShashkaProjectile(start_x, start_y, direction)
            self.active_shashkas.append(new_shashka)
            self.shashka_cooldown = self.SHASHKA_COOLDOWN
            
            # Тратим шашку
            self.shashka_count -= 1
            
            print(f"🗡️ Шашка брошена! Направление: {'→' if self.facing_right else '←'} (осталось: {self.shashka_count})")
    
    def _update_shashka_regeneration(self, delta_time: float):
        """Обновляет систему восстановления шашек."""
        if self.shashka_count < self.MAX_SHASHKAS:
            self.shashka_regen_timer += delta_time
            
            if self.shashka_regen_timer >= self.SHASHKA_REGEN_TIME:
                self.shashka_count += 1
                self.shashka_regen_timer = 0.0
                print(f"⚡ Шашка восстановлена! Доступно: {self.shashka_count}/{self.MAX_SHASHKAS}")
        else:
            # Если все шашки есть, сбрасываем таймер
            self.shashka_regen_timer = 0.0
    
    def _update_shashkas(self, delta_time: float):
        """Обновляет все активные шашки."""
        for shashka in self.active_shashkas[:]:  # Копия списка
            shashka.update(delta_time)
            
            # Удаляем неактивные шашки
            if not shashka.active:
                self.active_shashkas.remove(shashka)
                continue
            
            # Удаляем шашки за пределами мира с буфером
            BUFFER_ZONE = 200
            WORLD_WIDTH = 2000  # Размер игрового мира
            if shashka.x < -BUFFER_ZONE or shashka.x > WORLD_WIDTH + BUFFER_ZONE:
                self.active_shashkas.remove(shashka)
                print(f"🌀 Шашка удалена в player: x={shashka.x:.1f}, причина: граница мира")
    
    def render_shashkas(self, surface: pygame.Surface, camera_offset: Vector2D = None):
        """Рендерит все активные шашки."""
        for shashka in self.active_shashkas:
            shashka.draw(surface, camera_offset)
    
    def _update_state(self):
        """Определяет текущее состояние игрока на основе физики с буферной зоной."""
        # Эффективное состояние "на земле" с буфером против дрожания
        effective_on_ground = self.is_grounded and self.in_air_frames < 3
        
        # 1. ПРЫЖОК/ПАДЕНИЕ - приоритет (НЕ на земле эффективно)
        if not effective_on_ground:
            self.current_state = "jumping"
        # 2. ХОДЬБА - движется горизонтально по земле (увеличен порог для учета трения)
        elif abs(self.velocity.x) > 50.0:  # Увеличен с 0.1 до 50.0 для учета трения
            self.current_state = "walking"
        # 3. IDLE - стоит стабильно на земле
        else:
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
    
    def render(self, surface: pygame.Surface, camera_offset: Vector2D = None, debug_mode: bool = False):
        """Рендерит игрока."""
        if camera_offset is None:
            camera_offset = Vector2D(0, 0)
        
        # Выбираем спрайт на основе состояния
        if self.current_state == "idle":
            # IDLE: ТОЛЬКО static.png когда стоит на месте
            sprite = self.sprites['idle']
        elif self.current_state == "walking":
            # ХОДЬБА: анимация walk/*.png ТОЛЬКО при движении по земле
            sprite_key = f'walk_{self.current_frame}'
            sprite = self.sprites.get(sprite_key, self.sprites['idle'])
        elif self.current_state == "jumping":
            # ПРЫЖОК/ПАДЕНИЕ: ТОЛЬКО jump.png при любом вертикальном движении или в воздухе
            sprite = self.sprites['jump']
        else:
            # Fallback
            sprite = self.sprites['idle']
        
        # Отражаем спрайт в зависимости от направления (сохраняем ориентацию)
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
        
        # ВИЗУАЛЬНАЯ ОТЛАДКА стабилизации анимации
        if debug_mode:
            self._render_stability_debug(surface, camera_offset)
    
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
    
    def _render_stability_debug(self, surface: pygame.Surface, camera_offset: Vector2D):
        """Рендерит отладочную информацию стабилизации анимации."""
        font = pygame.font.Font(None, 20)
        
        # Эффективное состояние "на земле"
        effective_on_ground = self.is_grounded and self.in_air_frames < 3
        
        debug_info = [
            f"State: {self.current_state}",
            f"is_grounded: {self.is_grounded}",
            f"effective_on_ground: {effective_on_ground}",
            f"velocity.y: {self.velocity.y:.2f}",
            f"in_air_frames: {self.in_air_frames}",
            f"velocity.x: {self.velocity.x:.2f}"
        ]
        
        # Позиция отладочного текста рядом с игроком
        debug_x = int(self.position.x - camera_offset.x + self.size.x + 10)
        debug_y = int(self.position.y - camera_offset.y)
        
        # Фон для текста
        text_bg = pygame.Surface((200, len(debug_info) * 22 + 10), pygame.SRCALPHA)
        text_bg.fill((0, 0, 0, 180))
        surface.blit(text_bg, (debug_x - 5, debug_y - 5))
        
        # Рендерим отладочную информацию
        for i, info in enumerate(debug_info):
            color = (255, 255, 255)
            
            # Цветовая индикация проблем
            if "effective_on_ground: False" in info and self.is_grounded:
                color = (255, 255, 0)  # Желтый - потенциальная проблема
            elif "velocity.y:" in info and abs(self.velocity.y) > 0.5 and self.is_grounded:
                color = (255, 100, 100)  # Красный - дрожание
            elif "in_air_frames:" in info and self.in_air_frames > 3 and self.is_grounded:
                color = (255, 150, 0)  # Оранжевый - нестабильность
            
            text_surface = font.render(info, True, color)
            surface.blit(text_surface, (debug_x, debug_y + i * 22))
    
    def take_damage(self, damage: int) -> bool:
        """Получает урон. Возвращает True если игрок умер."""
        self.health = max(0, self.health - damage)
        return self.health <= 0
    
    def heal(self, amount: int):
        """Лечит игрока."""
        self.health = min(self.max_health, self.health + amount)
    
    def check_platform_collision(self, platform_rect: pygame.Rect):
        """Проверяет коллизию с платформой с улучшенной стабилизацией."""
        player_rect = self.get_rect()
        
        if player_rect.colliderect(platform_rect):
            # Определяем сторону коллизии
            overlap_left = player_rect.right - platform_rect.left
            overlap_right = platform_rect.right - player_rect.left
            overlap_top = player_rect.bottom - platform_rect.top
            overlap_bottom = platform_rect.bottom - player_rect.top
            
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            
            if min_overlap == overlap_top and self.velocity.y >= 0:
                # Приземление на платформу - ЧЕТКОЕ позиционирование
                self.position.y = platform_rect.top - self.size.y
                self.velocity.y = 0  # ПОЛНОЕ обнуление вертикальной скорости
                self.is_grounded = True  # Устанавливается однозначно
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
        else:
            # Если нет коллизии с этой платформой, проверяем не висит ли игрок в воздухе
            # Но НЕ сбрасываем is_grounded сразу - это будет сделано в update() если нужно
            pass