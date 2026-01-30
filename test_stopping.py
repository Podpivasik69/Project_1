#!/usr/bin/env python3
"""
Тест остановки и перехода в idle
"""

import pygame
import sys
from game.physics import Vector2D
from game.simple_player import SimplePlayer

def test_stopping():
    """Тестирует остановку и переход в idle."""
    
    # Инициализируем pygame минимально
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    # Создаем игрока на земле
    player = SimplePlayer(Vector2D(100, 528))
    player.is_grounded = True
    player.in_air_frames = 0
    
    # Создаем платформы
    platforms = [pygame.Rect(0, 600, 2000, 100)]
    
    print("=== ТЕСТ ОСТАНОВКИ ===")
    print()
    
    delta_time = 1.0 / 60.0  # 60 FPS
    
    # Сначала двигаемся
    print("🎮 ДВИЖЕНИЕ (3 кадра):")
    player.set_input(1.0, False, False)
    
    for frame in range(3):
        player.update(delta_time)
        for platform in platforms:
            player.check_platform_collision(platform)
        if not player.check_if_on_ground(platforms) and player.is_grounded:
            player.is_grounded = False
        
        print(f"Кадр {frame+1}: state={player.current_state:8s} | vel_x={player.velocity.x:5.1f}")
    
    print()
    
    # Теперь останавливаемся и смотрим как скорость уменьшается
    print("🎮 ОСТАНОВКА (15 кадров):")
    player.set_input(0, False, False)  # Отпускаем кнопки
    
    for frame in range(15):
        player.update(delta_time)
        for platform in platforms:
            player.check_platform_collision(platform)
        if not player.check_if_on_ground(platforms) and player.is_grounded:
            player.is_grounded = False
        
        print(f"Кадр {frame+1:2d}: state={player.current_state:8s} | vel_x={player.velocity.x:6.1f} | порог=50.0")
        
        # Показываем когда произойдет переход
        if abs(player.velocity.x) <= 50.0 and player.current_state == "walking":
            print("    ⚠️  Скорость упала ниже порога, но состояние еще walking")
        elif abs(player.velocity.x) <= 50.0 and player.current_state == "idle":
            print("    ✅ Переход в idle!")
    
    print()
    print("=== РЕЗУЛЬТАТ ===")
    final_state = player.current_state
    final_vel = player.velocity.x
    
    if final_state == "idle" and abs(final_vel) < 50.0:
        print("✅ УСПЕХ: Игрок корректно перешел в состояние idle при остановке")
    else:
        print(f"❌ ПРОБЛЕМА: Финальное состояние {final_state}, скорость {final_vel}")
    
    pygame.quit()

if __name__ == "__main__":
    test_stopping()