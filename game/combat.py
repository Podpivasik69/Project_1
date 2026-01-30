"""
Combat System Module
Система боя для игры
"""

import pygame
import math
from typing import List, Optional
from game.physics import Vector2D
from game.assets import asset_manager


class WeaponType:
    """Типы оружия."""
    SHASHKA = "shashka"


class Weapon:
    """Базовый класс оружия."""
    
    def __init__(self, weapon_type: str, damage: int, range_: float, attack_speed: float):
        self.weapon_type = weapon_type
        self.damage = damage
        self.range = range_
        self.attack_speed = attack_speed  # атак в секунду
        self.last_attack_time = 0.0
        
        # Визуализация
        self.sprite = None
        self.attack_animation_duration = 0.3  # секунд
        self.attack_animation_timer = 0.0
        self.is_attacking = False
        
        # Загружаем спрайт
        self._load_sprite()
    
    def _load_sprite(self) -> None:
        """Загружает спрайт оружия."""
        try:
            if self.weapon_type == WeaponType.SHASHKA:
                self.sprite = asset_manager.load_image("assets/shpaga.png", (32, 64))
        except Exception as e:
            print(f"Не удалось загрузить спрайт оружия {self.weapon_type}: {e}")
            # Создаем заглушку
            self.sprite = pygame.Surface((32, 64))
            self.sprite.fill((150, 150, 150))
    
    def can_attack(self) -> bool:
        """Проверяет можно ли атаковать."""
        cooldown = 1.0 / self.attack_speed
        return self.last_attack_time >= cooldown
    
    def start_attack(self) -> None:
        """Начинает атаку."""
        if self.can_attack():
            self.is_attacking = True
            self.attack_animation_timer = 0.0
            self.last_attack_time = 0.0
    
    def update(self, delta_time: float) -> None:
        """Обновляет оружие."""
        self.last_attack_time += delta_time
        
        if self.is_attacking:
            self.attack_animation_timer += delta_time
            if self.attack_animation_timer >= self.attack_animation_duration:
                self.is_attacking = False
                self.attack_animation_timer = 0.0
    
    def get_attack_area(self, wielder_pos: Vector2D, facing_right: bool) -> pygame.Rect:
        """
        Получает область атаки.
        
        Args:
            wielder_pos: Позиция владельца оружия
            facing_right: Направление взгляда
            
        Returns:
            Прямоугольник области атаки
        """
        # Размер области атаки
        attack_width = self.range
        attack_height = 40
        
        if facing_right:
            attack_x = wielder_pos.x
            attack_y = wielder_pos.y - attack_height / 2
        else:
            attack_x = wielder_pos.x - attack_width
            attack_y = wielder_pos.y - attack_height / 2
        
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def render(self, surface: pygame.Surface, wielder_pos: Vector2D, facing_right: bool, 
               camera_offset: Vector2D = None) -> None:
        """
        Отрисовывает оружие.
        
        Args:
            surface: Поверхность для рисования
            wielder_pos: Позиция владельца
            facing_right: Направление взгляда
            camera_offset: Смещение камеры
        """
        if not self.sprite:
            return
        
        if camera_offset is None:
            camera_offset = Vector2D.zero()
        
        screen_pos = wielder_pos - camera_offset
        
        # Позиция оружия относительно владельца
        weapon_offset_x = 20 if facing_right else -20
        weapon_offset_y = 0
        
        # Анимация атаки
        if self.is_attacking:
            # Во время атаки оружие поворачивается
            progress = self.attack_animation_timer / self.attack_animation_duration
            if facing_right:
                weapon_offset_x += int(15 * math.sin(progress * math.pi))
                weapon_offset_y -= int(10 * math.sin(progress * math.pi))
            else:
                weapon_offset_x -= int(15 * math.sin(progress * math.pi))
                weapon_offset_y -= int(10 * math.sin(progress * math.pi))
        
        weapon_pos = (
            int(screen_pos.x + weapon_offset_x),
            int(screen_pos.y + weapon_offset_y)
        )
        
        # Поворачиваем спрайт если нужно
        sprite = self.sprite
        if not facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        
        # Поворот во время атаки
        if self.is_attacking:
            progress = self.attack_animation_timer / self.attack_animation_duration
            angle = int(45 * math.sin(progress * math.pi))
            if not facing_right:
                angle = -angle
            sprite = pygame.transform.rotate(sprite, angle)
        
        # Рисуем оружие
        weapon_rect = sprite.get_rect(center=weapon_pos)
        surface.blit(sprite, weapon_rect)


class Shashka(Weapon):
    """Шашка - традиционное кавказское оружие."""
    
    def __init__(self):
        super().__init__(
            weapon_type=WeaponType.SHASHKA,
            damage=25,
            range_=50.0,
            attack_speed=1.5  # 1.5 атаки в секунду
        )


class CombatSystem:
    """Система боя."""
    
    def __init__(self):
        self.active_attacks = []  # Список активных атак
    
    def perform_attack(self, attacker, weapon: Weapon, targets: List) -> List:
        """
        Выполняет атаку.
        
        Args:
            attacker: Атакующий объект
            weapon: Оружие
            targets: Список потенциальных целей
            
        Returns:
            Список пораженных целей
        """
        if not weapon.can_attack():
            return []
        
        weapon.start_attack()
        
        # Получаем область атаки
        attack_area = weapon.get_attack_area(
            attacker.physics_body.position,
            attacker.facing_right
        )
        
        # Проверяем попадания
        hit_targets = []
        for target in targets:
            if not hasattr(target, 'health') or not target.health.is_alive:
                continue
            
            # Проверяем пересечение с целью
            target_bounds = target.get_bounds()
            if attack_area.colliderect(target_bounds):
                # Наносим урон
                if target.take_damage(weapon.damage):
                    hit_targets.append(target)
                else:
                    # Цель умерла
                    hit_targets.append(target)
        
        return hit_targets
    
    def render_attack_area(self, surface: pygame.Surface, attacker, weapon: Weapon, 
                          camera_offset: Vector2D = None, debug: bool = False) -> None:
        """
        Отрисовывает область атаки (для отладки).
        
        Args:
            surface: Поверхность для рисования
            attacker: Атакующий
            weapon: Оружие
            camera_offset: Смещение камеры
            debug: Показывать ли область атаки
        """
        if not debug or not weapon.is_attacking:
            return
        
        if camera_offset is None:
            camera_offset = Vector2D.zero()
        
        # Получаем область атаки
        attack_area = weapon.get_attack_area(
            attacker.physics_body.position,
            attacker.facing_right
        )
        
        # Смещаем для камеры
        screen_area = pygame.Rect(
            attack_area.x - camera_offset.x,
            attack_area.y - camera_offset.y,
            attack_area.width,
            attack_area.height
        )
        
        # Рисуем полупрозрачную область
        attack_surface = pygame.Surface((screen_area.width, screen_area.height))
        attack_surface.set_alpha(100)
        attack_surface.fill((255, 0, 0))  # Красный цвет
        surface.blit(attack_surface, (screen_area.x, screen_area.y))
        
        # Рисуем границу
        pygame.draw.rect(surface, (255, 0, 0), screen_area, 2)