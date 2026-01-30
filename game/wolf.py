"""
Wolf Enemy Module
Враг-волк для игры
"""

import pygame
import math
from typing import Optional, List
from game.physics import Vector2D, PhysicsBody
from game.collision import Collider, CollisionLayer
from game.health import HealthComponent, HealthBar
from game.assets import asset_manager


class WolfState:
    """Состояния волка."""
    IDLE = "idle"
    WALKING = "walking"
    ATTACKING = "attacking"
    HURT = "hurt"
    DEAD = "dead"


class Wolf:
    """Класс врага-волка."""
    
    def __init__(self, start_position: Vector2D, size: Vector2D = None):
        """
        Инициализация волка.
        
        Args:
            start_position: Начальная позиция
            size: Размер волка
        """
        if size is None:
            size = Vector2D(64, 48)  # Размер волка
        
        self.size = size
        
        # Физика
        self.physics_body = PhysicsBody(
            position=Vector2D(start_position.x, start_position.y),
            velocity=Vector2D.zero(),
            acceleration=Vector2D.zero(),
            mass=1.0,
            friction=0.8,
            gravity_scale=1.0
        )
        
        # Коллизия
        self.collider = Collider(
            physics_body=self.physics_body,
            size=self.size,
            layer=CollisionLayer.ENEMY,
            is_trigger=False
        )
        
        # Здоровье
        self.health = HealthComponent(max_health=50)
        self.health.on_death = self._on_death
        self.health.on_damage = self._on_damage
        
        # Health bar
        self.health_bar = HealthBar(width=50, height=6)
        
        # Состояние
        self.current_state = WolfState.IDLE
        self.facing_right = True
        
        # ИИ и движение
        self.move_speed = 80.0  # пикселей в секунду
        self.attack_range = 60.0  # дистанция атаки
        self.detection_range = 200.0  # дистанция обнаружения игрока
        self.attack_damage = 15
        self.attack_cooldown = 1.5  # секунд между атаками
        self.last_attack_time = 0.0
        
        # Цель (игрок)
        self.target = None
        self.target_last_seen_pos = None
        
        # Визуализация
        self.sprites = {}
        self.current_sprite = None
        self.sprite_flip = False
        
        # Анимация
        self.animation_timer = 0.0
        self.walk_frames = []
        self.walk_animation_speed = 6.0  # кадров в секунду
        
        # Загружаем спрайты
        self._load_sprites()
        
        # Отладочная информация
        self.debug_info = {}
        
        # Флаги
        self.is_grounded = False
        self.marked_for_removal = False
    
    def _load_sprites(self) -> None:
        """Загружает спрайты волка."""
        sprite_size = (int(self.size.x), int(self.size.y))
        
        try:
            # Загружаем статичный спрайт
            static_sprite = asset_manager.load_image("assets/wolf/static.png", sprite_size)
            
            self.sprites = {
                WolfState.IDLE: static_sprite,
                WolfState.ATTACKING: static_sprite,
                WolfState.HURT: static_sprite,
                WolfState.DEAD: static_sprite
            }
            
            # Загружаем кадры анимации ходьбы
            self.walk_frames = []
            walk_frame_numbers = [0, 1, 3, 4, 5, 6]  # Доступные кадры
            
            for frame_num in walk_frame_numbers:
                try:
                    frame_path = f"assets/wolf/wolf_walk/{frame_num}.png"
                    frame = asset_manager.load_image(frame_path, sprite_size)
                    self.walk_frames.append(frame)
                except:
                    # Если кадр не загрузился, используем статичный спрайт
                    self.walk_frames.append(static_sprite)
            
            # Устанавливаем начальный спрайт
            self.current_sprite = self.sprites[WolfState.IDLE]
            
            print(f"Wolf: загружено {len(self.sprites)} спрайтов и {len(self.walk_frames)} кадров анимации")
            
        except Exception as e:
            print(f"Ошибка загрузки спрайтов волка: {e}")
            # Создаем заглушку
            fallback_sprite = pygame.Surface(sprite_size)
            fallback_sprite.fill((100, 100, 100))  # Серый прямоугольник
            
            self.sprites = {state: fallback_sprite for state in [WolfState.IDLE, WolfState.WALKING, WolfState.ATTACKING, WolfState.HURT, WolfState.DEAD]}
            self.walk_frames = [fallback_sprite] * 6
            self.current_sprite = fallback_sprite
    
    def set_target(self, target) -> None:
        """Устанавливает цель для волка."""
        self.target = target
    
    def _on_death(self) -> None:
        """Вызывается при смерти волка."""
        self._change_state(WolfState.DEAD)
        self.marked_for_removal = True
        print("Wolf died!")
    
    def _on_damage(self, damage: int, remaining_health: int) -> None:
        """Вызывается при получении урона."""
        self._change_state(WolfState.HURT)
        self.health.set_invulnerable(0.5)  # 0.5 секунды неуязвимости
        print(f"Wolf took {damage} damage, {remaining_health} health remaining")
    
    def _change_state(self, new_state: str) -> None:
        """Изменяет состояние волка."""
        if self.current_state != new_state:
            self.current_state = new_state
    
    def _update_sprite(self) -> None:
        """Обновляет текущий спрайт."""
        # Определяем направление поворота спрайта
        self.sprite_flip = not self.facing_right
        
        # Выбираем спрайт в зависимости от состояния
        if self.current_state == WolfState.WALKING and self.walk_frames:
            # Анимация ходьбы
            frame_duration = 1.0 / self.walk_animation_speed
            frame_index = int(self.animation_timer / frame_duration) % len(self.walk_frames)
            self.current_sprite = self.walk_frames[frame_index]
        else:
            # Статичные состояния
            if self.current_state in self.sprites:
                self.current_sprite = self.sprites[self.current_state]
    
    def _update_ai(self, delta_time: float) -> None:
        """Обновляет ИИ волка."""
        if not self.health.is_alive or not self.target:
            return
        
        # Вычисляем расстояние до цели
        distance_to_target = self.physics_body.position.distance_to(self.target.physics_body.position)
        
        # Обновляем время последней атаки
        self.last_attack_time += delta_time
        
        # Логика ИИ
        if distance_to_target <= self.attack_range and self.last_attack_time >= self.attack_cooldown:
            # Атакуем
            self._attack_target()
        elif distance_to_target <= self.detection_range:
            # Идем к цели
            self._move_towards_target()
        else:
            # Цель слишком далеко, стоим на месте
            self._change_state(WolfState.IDLE)
    
    def _attack_target(self) -> None:
        """Атакует цель."""
        if not self.target or not self.target.health.is_alive:
            return
        
        self._change_state(WolfState.ATTACKING)
        
        # Наносим урон цели
        self.target.health.take_damage(self.attack_damage)
        self.last_attack_time = 0.0
        
        print(f"Wolf attacked target for {self.attack_damage} damage!")
    
    def _move_towards_target(self) -> None:
        """Двигается к цели."""
        if not self.target:
            return
        
        # Вычисляем направление к цели
        direction = self.target.physics_body.position - self.physics_body.position
        if direction.magnitude() > 0:
            direction = direction.normalize()
            
            # Обновляем направление взгляда
            if direction.x > 0:
                self.facing_right = True
            elif direction.x < 0:
                self.facing_right = False
            
            # Применяем силу движения
            move_force = Vector2D(direction.x * self.move_speed * 10, 0)
            self.physics_body.apply_force(move_force)
            
            self._change_state(WolfState.WALKING)
    
    def take_damage(self, damage: int) -> bool:
        """
        Получить урон.
        
        Args:
            damage: Количество урона
            
        Returns:
            True если волк еще жив
        """
        return self.health.take_damage(damage)
    
    def update(self, delta_time: float) -> None:
        """Обновляет волка."""
        if not self.health.is_alive:
            return
        
        self.animation_timer += delta_time
        
        # Обновляем здоровье
        self.health.update(delta_time)
        
        # Обновляем ИИ
        self._update_ai(delta_time)
        
        # Обновляем спрайт
        self._update_sprite()
        
        # Применяем трение
        self.physics_body.velocity = Vector2D(
            self.physics_body.velocity.x * 0.85,
            self.physics_body.velocity.y
        )
        
        # Обновляем отладочную информацию
        self._update_debug_info()
    
    def _update_debug_info(self) -> None:
        """Обновляет отладочную информацию."""
        target_distance = "No target"
        if self.target:
            distance = self.physics_body.position.distance_to(self.target.physics_body.position)
            target_distance = f"{distance:.1f}"
        
        self.debug_info = {
            "position": f"({self.physics_body.position.x:.1f}, {self.physics_body.position.y:.1f})",
            "state": self.current_state,
            "health": f"{self.health.current_health}/{self.health.max_health}",
            "target_dist": target_distance,
            "facing_right": self.facing_right,
            "grounded": self.is_grounded
        }
    
    def render(self, surface: pygame.Surface, camera_offset: Vector2D = None) -> None:
        """Отрисовывает волка."""
        if camera_offset is None:
            camera_offset = Vector2D.zero()
        
        # Вычисляем позицию на экране
        screen_pos = self.physics_body.position - camera_offset
        
        # Получаем текущий спрайт
        sprite = self.current_sprite
        
        if sprite:
            # Позиционируем спрайт
            sprite_rect = sprite.get_rect()
            sprite_rect.center = (int(screen_pos.x), int(screen_pos.y))
            
            # Поворачиваем спрайт если нужно
            if self.sprite_flip:
                sprite = pygame.transform.flip(sprite, True, False)
            
            # Эффект мигания при получении урона
            if self.health.is_invulnerable:
                # Создаем эффект мигания
                import time
                if int(time.time() * 8) % 2:  # 8 раз в секунду
                    # Делаем спрайт полупрозрачным
                    sprite = sprite.copy()
                    sprite.set_alpha(128)
            
            # Рисуем спрайт
            surface.blit(sprite, sprite_rect)
        else:
            # Заглушка - цветной прямоугольник
            self._render_fallback(surface, screen_pos)
        
        # Рисуем полоску здоровья
        if self.health.is_alive:
            self.health_bar.render(surface, self.physics_body.position, self.health, camera_offset)
    
    def _render_fallback(self, surface: pygame.Surface, screen_pos: Vector2D) -> None:
        """Отрисовка заглушки."""
        # Цвет в зависимости от состояния
        if self.current_state == WolfState.DEAD:
            color = (50, 50, 50)  # Серый
        elif self.current_state == WolfState.HURT:
            color = (200, 100, 100)  # Красноватый
        elif self.current_state == WolfState.ATTACKING:
            color = (200, 50, 50)  # Красный
        else:
            color = (100, 100, 150)  # Синеватый
        
        # Рисуем прямоугольник
        wolf_rect = pygame.Rect(
            screen_pos.x - self.size.x / 2,
            screen_pos.y - self.size.y / 2,
            self.size.x,
            self.size.y
        )
        
        pygame.draw.rect(surface, color, wolf_rect)
        pygame.draw.rect(surface, (255, 255, 255), wolf_rect, 2)  # Белая обводка
        
        # Рисуем "глаза"
        eye_size = 4
        if self.facing_right:
            eye_pos = (wolf_rect.right - 10, wolf_rect.top + 8)
        else:
            eye_pos = (wolf_rect.left + 10, wolf_rect.top + 8)
        
        pygame.draw.circle(surface, (255, 0, 0), eye_pos, eye_size)
    
    def get_bounds(self) -> pygame.Rect:
        """Получает границы коллизии волка."""
        return self.collider.get_bounds()
    
    def reset_position(self, position: Vector2D) -> None:
        """Сбрасывает позицию волка."""
        self.physics_body.position = Vector2D(position.x, position.y)
        self.physics_body.velocity = Vector2D.zero()
        self.physics_body.acceleration = Vector2D.zero()
        self.is_grounded = False