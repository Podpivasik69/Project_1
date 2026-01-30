"""
Simple Combat System
Simplified combat for minimal working platformer
"""

import pygame
import math
from typing import List, Optional
from game.physics import Vector2D
from game.assets import asset_manager


class SimpleCombat:
    """Простая система боя."""
    
    def __init__(self):
        self.weapon_sprite = None  # Загрузим позже
        self.attack_range = 80.0
        self.attack_damage = 25
        self.attack_cooldown = 0.8
        self.attack_duration = 0.3
    
    def _ensure_weapon_loaded(self):
        """Загружает оружие если еще не загружено."""
        if self.weapon_sprite is None:
            self.weapon_sprite = asset_manager.get_weapon_sprite('shashka', (32, 64))
    
    def perform_attack(self, attacker, targets: List, delta_time: float) -> List:
        """
        Выполняет атаку.
        
        Args:
            attacker: Атакующий объект (должен иметь position, facing_right)
            targets: Список целей для атаки
            delta_time: Время кадра
            
        Returns:
            Список пораженных целей
        """
        if not hasattr(attacker, 'last_attack_time'):
            attacker.last_attack_time = 0.0
        
        if not hasattr(attacker, 'is_attacking'):
            attacker.is_attacking = False
        
        if not hasattr(attacker, 'attack_timer'):
            attacker.attack_timer = 0.0
        
        attacker.last_attack_time += delta_time
        
        # Обновляем таймер атаки
        if attacker.is_attacking:
            attacker.attack_timer += delta_time
            if attacker.attack_timer >= self.attack_duration:
                attacker.is_attacking = False
                attacker.attack_timer = 0.0
        
        # Проверяем, можем ли атаковать
        if attacker.last_attack_time < self.attack_cooldown:
            return []
        
        # Начинаем атаку
        if not attacker.is_attacking:
            attacker.is_attacking = True
            attacker.attack_timer = 0.0
            attacker.last_attack_time = 0.0
        
        # Определяем область атаки
        attack_area = self._get_attack_area(attacker)
        
        # Проверяем попадания
        hit_targets = []
        for target in targets:
            if hasattr(target, 'get_rect') and hasattr(target, 'take_damage'):
                target_rect = target.get_rect()
                if attack_area.colliderect(target_rect):
                    if target.take_damage(self.attack_damage):
                        print(f"⚔️ Target defeated!")
                    else:
                        print(f"⚔️ Hit target for {self.attack_damage} damage!")
                    hit_targets.append(target)
        
        return hit_targets
    
    def _get_attack_area(self, attacker) -> pygame.Rect:
        """Возвращает область атаки."""
        # Размер области атаки
        attack_width = self.attack_range
        attack_height = attacker.size.y if hasattr(attacker, 'size') else 64
        
        # Позиция области атаки зависит от направления
        if attacker.facing_right:
            attack_x = attacker.position.x + (attacker.size.x if hasattr(attacker, 'size') else 48)
        else:
            attack_x = attacker.position.x - attack_width
        
        attack_y = attacker.position.y
        
        return pygame.Rect(int(attack_x), int(attack_y), int(attack_width), int(attack_height))
    
    def get_attack_rect(self, attacker) -> Optional[pygame.Rect]:
        """Возвращает прямоугольник атаки если атакующий атакует."""
        if hasattr(attacker, 'is_attacking') and attacker.is_attacking:
            return self._get_attack_area(attacker)
        return None
    
    def render_weapon(self, surface: pygame.Surface, attacker, camera_offset: Vector2D = None):
        """Рендерит оружие при атаке."""
        if not hasattr(attacker, 'is_attacking') or not attacker.is_attacking:
            return
        
        self._ensure_weapon_loaded()
        
        if camera_offset is None:
            camera_offset = Vector2D(0, 0)
        
        # Позиция оружия
        weapon_size = (32, 64)
        if attacker.facing_right:
            weapon_x = attacker.position.x + (attacker.size.x if hasattr(attacker, 'size') else 48)
            weapon_y = attacker.position.y + 10
        else:
            weapon_x = attacker.position.x - weapon_size[0]
            weapon_y = attacker.position.y + 10
        
        # Отражаем оружие если нужно
        weapon_sprite = self.weapon_sprite
        if not attacker.facing_right:
            weapon_sprite = pygame.transform.flip(weapon_sprite, True, False)
        
        # Рендерим оружие
        render_pos = (
            int(weapon_x - camera_offset.x),
            int(weapon_y - camera_offset.y)
        )
        surface.blit(weapon_sprite, render_pos)
    
    def render_attack_area(self, surface: pygame.Surface, attacker, camera_offset: Vector2D = None, debug: bool = False):
        """Рендерит область атаки (для отладки)."""
        if not debug or not hasattr(attacker, 'is_attacking') or not attacker.is_attacking:
            return
        
        if camera_offset is None:
            camera_offset = Vector2D(0, 0)
        
        attack_area = self._get_attack_area(attacker)
        debug_rect = pygame.Rect(
            int(attack_area.x - camera_offset.x),
            int(attack_area.y - camera_offset.y),
            attack_area.width,
            attack_area.height
        )
        
        # Рендерим полупрозрачную область атаки
        attack_surface = pygame.Surface((attack_area.width, attack_area.height), pygame.SRCALPHA)
        attack_surface.fill((255, 0, 0, 100))  # Красный с прозрачностью
        surface.blit(attack_surface, (debug_rect.x, debug_rect.y))
        
        # Рамка
        pygame.draw.rect(surface, (255, 0, 0), debug_rect, 2)