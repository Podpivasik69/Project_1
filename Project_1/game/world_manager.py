"""
World Layer - Система управления игровым миром
Упрощенная версия для тестирования
"""

import pygame
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from game.physics import Vector2D, PhysicsBody
from game.collision import Collider, CollisionLayer
from game.utils import Colors


class TileData:
    """Данные тайла."""
    def __init__(self, sprite_id: int, has_collision: bool = False):
        self.sprite_id = sprite_id
        self.has_collision = has_collision


class TilemapLayer:
    """Слой тайлмапа."""
    
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        self.tiles: Dict[Tuple[int, int], TileData] = {}
        self.colliders: List[Collider] = []
    
    def set_tile(self, x: int, y: int, tile_data: TileData) -> None:
        """Устанавливает тайл в позицию."""
        self.tiles[(x, y)] = tile_data
        
        # Создаем коллайдер если нужно
        if tile_data.has_collision:
            self._create_tile_collider(x, y)
    
    def _create_tile_collider(self, x: int, y: int) -> None:
        """Создает коллайдер для тайла."""
        world_pos = Vector2D(x * self.tile_size, y * self.tile_size)
        size = Vector2D(self.tile_size, self.tile_size)
        
        # Создаем физическое тело для тайла
        physics_body = PhysicsBody(
            position=world_pos,
            velocity=Vector2D.zero(),
            mass=float('inf'),  # Бесконечная масса для статических объектов
            is_static=True
        )
        
        # Создаем коллайдер
        collider = Collider(
            physics_body=physics_body,
            size=size,
            layer=CollisionLayer.PLATFORM,
            is_trigger=False
        )
        
        self.colliders.append(collider)
    
    def render(self, surface: pygame.Surface, camera_offset: Vector2D = None) -> None:
        """Рендерит слой тайлмапа."""
        if camera_offset is None:
            camera_offset = Vector2D.zero()
        
        for (x, y), tile_data in self.tiles.items():
            world_pos = Vector2D(x * self.tile_size, y * self.tile_size)
            screen_pos = world_pos - camera_offset
            
            # Рисуем цветной прямоугольник
            color = self._get_tile_color(tile_data.sprite_id)
            rect = pygame.Rect(int(screen_pos.x), int(screen_pos.y), 
                             self.tile_size, self.tile_size)
            pygame.draw.rect(surface, color, rect)
            
            # Рисуем границу
            pygame.draw.rect(surface, (0, 0, 0), rect, 1)
    
    def _get_tile_color(self, sprite_id: int) -> Tuple[int, int, int]:
        """Получает цвет для тайла."""
        colors = [
            Colors.PLATFORM_BROWN,  # 0 - основная земля
            (100, 100, 100),        # 1 - серые платформы
            (50, 150, 50),          # 2 - зеленые платформы
            (150, 50, 50),          # 3 - красные платформы
            (50, 50, 150),          # 4 - синие платформы
        ]
        return colors[sprite_id % len(colors)]


class LevelData:
    """Данные уровня."""
    
    def __init__(self, level_id: str):
        self.level_id = level_id
        self.name = ""
        self.tilemap_layer: Optional[TilemapLayer] = None
        self.player_start_position = Vector2D(100, 500)


class LevelManager:
    """Менеджер уровней."""
    
    def __init__(self):
        self.current_level: Optional[LevelData] = None
    
    def load_level(self, level_id: str) -> bool:
        """Загружает уровень."""
        level_data = self._create_test_level(level_id)
        self.current_level = level_data
        print(f"Level {level_id} loaded successfully")
        return True
    
    def _create_test_level(self, level_id: str) -> LevelData:
        """Создает тестовый уровень."""
        level = LevelData(level_id)
        level.name = "Test Level"
        
        # Создаем основной слой земли
        ground_layer = TilemapLayer(tile_size=32)
        
        # Добавляем платформы
        ground_tile = TileData(sprite_id=0, has_collision=True)
        platform_tile = TileData(sprite_id=1, has_collision=True)
        high_tile = TileData(sprite_id=2, has_collision=True)
        
        # Нижняя платформа (земля)
        for x in range(0, 40):
            ground_layer.set_tile(x, 22, ground_tile)
        
        # Средние платформы
        for x in range(10, 20):
            ground_layer.set_tile(x, 18, platform_tile)
        
        for x in range(25, 35):
            ground_layer.set_tile(x, 15, high_tile)
        
        level.tilemap_layer = ground_layer
        return level
    
    def get_colliders(self) -> List[Collider]:
        """Получает все коллайдеры уровня."""
        colliders = []
        if self.current_level and self.current_level.tilemap_layer:
            colliders.extend(self.current_level.tilemap_layer.colliders)
        return colliders
    
    def update(self, delta_time: float, player_position: Vector2D, 
               player_size: Vector2D) -> None:
        """Обновляет состояние уровня."""
        pass  # Пока ничего не делаем
    
    def render(self, surface: pygame.Surface, camera_offset: Vector2D = None) -> None:
        """Рендерит уровень."""
        if self.current_level and self.current_level.tilemap_layer:
            self.current_level.tilemap_layer.render(surface, camera_offset)


class WorldManager:
    """Главный менеджер игрового мира."""
    
    def __init__(self):
        self.level_manager = LevelManager()
        self.current_level_id: Optional[str] = None
    
    def load_level(self, level_id: str) -> bool:
        """Загружает уровень."""
        success = self.level_manager.load_level(level_id)
        if success:
            self.current_level_id = level_id
        return success
    
    def get_player_start_position(self) -> Vector2D:
        """Получает стартовую позицию игрока."""
        if self.level_manager.current_level:
            return self.level_manager.current_level.player_start_position
        return Vector2D(100, 500)
    
    def get_colliders(self) -> List[Collider]:
        """Получает все коллайдеры мира."""
        return self.level_manager.get_colliders()
    
    def update(self, delta_time: float, player_position: Vector2D, 
               player_size: Vector2D) -> None:
        """Обновляет мир."""
        self.level_manager.update(delta_time, player_position, player_size)
    
    def render(self, surface: pygame.Surface, camera_offset: Vector2D = None) -> None:
        """Рендерит мир."""
        self.level_manager.render(surface, camera_offset)