#!/usr/bin/env python3
"""
Финальный тест анимации - симуляция реальной игры
"""

import pygame
import sys
from game.physics import Vector2D
from game.simple_player import SimplePlayer

def simulate_game_loop():
    """Симулирует игровой цикл с проверкой анимации."""
    
    # Инициализируем pygame минимально
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    # Создаем игрока
    player = SimplePlayer(Vector2D(100, 528))  # На земле (600-72=528)
    
    # Создаем платформы как в игре
    platforms = [
        pygame.Rect(0, 600, 2000, 100),      # Земля
        pygame.Rect(300, 500, 200, 20),      # Платформа для прыжков
    ]
    
    print("=== СИМУЛЯЦИЯ ИГРОВОГО ЦИКЛА ===")
    print()
    
    delta_time = 1.0 / 60.0  # 60 FPS
    
    # Симуляция 10 кадров стояния на земле
    print("🎮 СТОЯНИЕ НА ЗЕМЛЕ (10 кадров):")
    player.set_input(0, False, False)  # Никаких действий
    
    for frame in range(10):
        # Обновляем игрока
        player.update(delta_time)
        
        # Проверяем коллизии (как в simple_game.py)
        for platform in platforms:
            player.check_platform_collision(platform)
        
        # Проверяем, стоит ли на земле
        if not player.check_if_on_ground(platforms) and player.is_grounded:
            player.is_grounded = False
        
        effective_on_ground = player.is_grounded and player.in_air_frames < 3
        
        print(f"Кадр {frame+1:2d}: state={player.current_state:8s} | grounded={player.is_grounded} | effective={effective_on_ground} | vel_y={player.velocity.y:5.1f} | air_frames={player.in_air_frames}")
    
    print()
    
    # Симуляция движения вправо
    print("🎮 ДВИЖЕНИЕ ВПРАВО (5 кадров):")
    player.set_input(1.0, False, False)  # Движение вправо
    
    for frame in range(5):
        player.update(delta_time)
        
        for platform in platforms:
            player.check_platform_collision(platform)
        
        if not player.check_if_on_ground(platforms) and player.is_grounded:
            player.is_grounded = False
        
        effective_on_ground = player.is_grounded and player.in_air_frames < 3
        
        print(f"Кадр {frame+1:2d}: state={player.current_state:8s} | grounded={player.is_grounded} | effective={effective_on_ground} | vel_x={player.velocity.x:5.1f} | facing_right={player.facing_right}")
    
    print()
    
    # Симуляция остановки
    print("🎮 ОСТАНОВКА (5 кадров):")
    player.set_input(0, False, False)  # Остановка
    
    for frame in range(5):
        player.update(delta_time)
        
        for platform in platforms:
            player.check_platform_collision(platform)
        
        if not player.check_if_on_ground(platforms) and player.is_grounded:
            player.is_grounded = False
        
        effective_on_ground = player.is_grounded and player.in_air_frames < 3
        
        print(f"Кадр {frame+1:2d}: state={player.current_state:8s} | grounded={player.is_grounded} | effective={effective_on_ground} | vel_x={player.velocity.x:5.1f} | facing_right={player.facing_right}")
    
    print()
    
    # Симуляция прыжка
    print("🎮 ПРЫЖОК (10 кадров):")
    player.set_input(0, True, False)  # Прыжок
    
    for frame in range(10):
        player.update(delta_time)
        
        for platform in platforms:
            player.check_platform_collision(platform)
        
        if not player.check_if_on_ground(platforms) and player.is_grounded:
            player.is_grounded = False
        
        effective_on_ground = player.is_grounded and player.in_air_frames < 3
        
        print(f"Кадр {frame+1:2d}: state={player.current_state:8s} | grounded={player.is_grounded} | effective={effective_on_ground} | vel_y={player.velocity.y:6.1f} | air_frames={player.in_air_frames}")
        
        # Отпускаем прыжок после первого кадра
        if frame == 0:
            player.set_input(0, False, False)
    
    print()
    
    # Симуляция приземления
    print("🎮 ПРИЗЕМЛЕНИЕ (5 кадров):")
    # Принудительно ставим игрока почти на землю
    player.position.y = 520
    player.velocity.y = 50  # Небольшая скорость падения
    
    for frame in range(5):
        player.update(delta_time)
        
        for platform in platforms:
            player.check_platform_collision(platform)
        
        if not player.check_if_on_ground(platforms) and player.is_grounded:
            player.is_grounded = False
        
        effective_on_ground = player.is_grounded and player.in_air_frames < 3
        
        print(f"Кадр {frame+1:2d}: state={player.current_state:8s} | grounded={player.is_grounded} | effective={effective_on_ground} | vel_y={player.velocity.y:6.1f} | pos_y={player.position.y:5.1f}")
    
    print()
    print("=== РЕЗУЛЬТАТЫ ===")
    print("✅ Стояние на земле: должно быть ТОЛЬКО 'idle'")
    print("✅ Движение по земле: должно быть ТОЛЬКО 'walking'") 
    print("✅ Остановка: должно вернуться к 'idle'")
    print("✅ Прыжок/падение: должно быть ТОЛЬКО 'jumping'")
    print("✅ Приземление: должно стабильно перейти в 'idle'")
    print()
    print("Если все состояния корректны - дрожание исправлено! 🎉")
    
    pygame.quit()

if __name__ == "__main__":
    simulate_game_loop()