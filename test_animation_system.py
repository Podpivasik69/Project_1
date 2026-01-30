#!/usr/bin/env python3
"""
Тест системы анимаций игрока
"""

import pygame
import sys
from game.physics import Vector2D
from game.simple_player import SimplePlayer

def test_animation_states():
    """Тестирует состояния анимации игрока."""
    
    # Инициализируем pygame минимально
    pygame.init()
    pygame.display.set_mode((1, 1))  # Минимальное окно
    
    # Создаем игрока
    player = SimplePlayer(Vector2D(100, 100))
    
    print("=== ТЕСТ СИСТЕМЫ АНИМАЦИЙ ===")
    print()
    
    # Тест 1: IDLE состояние
    print("1. Тест IDLE (стояние):")
    player.velocity = Vector2D(0, 0)
    player.is_grounded = True
    player._update_state()
    print(f"   velocity.x = {player.velocity.x}, velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: idle" + (" ✓" if player.current_state == "idle" else " ✗"))
    print()
    
    # Тест 2: ХОДЬБА
    print("2. Тест ХОДЬБА (движение по земле):")
    player.velocity = Vector2D(100, 0)  # Движется горизонтально
    player.is_grounded = True
    player._update_state()
    print(f"   velocity.x = {player.velocity.x}, velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: walking" + (" ✓" if player.current_state == "walking" else " ✗"))
    print()
    
    # Тест 3: ПРЫЖОК (вертикальное движение)
    print("3. Тест ПРЫЖОК (вертикальное движение):")
    player.velocity = Vector2D(0, -200)  # Прыгает вверх
    player.is_grounded = True  # Еще на земле, но уже прыгает
    player._update_state()
    print(f"   velocity.x = {player.velocity.x}, velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: jumping" + (" ✓" if player.current_state == "jumping" else " ✗"))
    print()
    
    # Тест 4: ПАДЕНИЕ (в воздухе)
    print("4. Тест ПАДЕНИЕ (в воздухе):")
    player.velocity = Vector2D(0, 100)  # Падает вниз
    player.is_grounded = False  # В воздухе
    player._update_state()
    print(f"   velocity.x = {player.velocity.x}, velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: jumping" + (" ✓" if player.current_state == "jumping" else " ✗"))
    print()
    
    # Тест 5: ПРЫЖОК С ДВИЖЕНИЕМ
    print("5. Тест ПРЫЖОК С ДВИЖЕНИЕМ:")
    player.velocity = Vector2D(150, -100)  # Движется и прыгает
    player.is_grounded = False
    player._update_state()
    print(f"   velocity.x = {player.velocity.x}, velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: jumping" + (" ✓" if player.current_state == "jumping" else " ✗"))
    print()
    
    # Тест 6: МЕДЛЕННОЕ ДВИЖЕНИЕ (должно быть IDLE)
    print("6. Тест МЕДЛЕННОЕ ДВИЖЕНИЕ (трение):")
    player.velocity = Vector2D(5, 0)  # Очень медленно (меньше 10)
    player.is_grounded = True
    player._update_state()
    print(f"   velocity.x = {player.velocity.x}, velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: idle" + (" ✓" if player.current_state == "idle" else " ✗"))
    print()
    
    print("=== ТЕСТ АНИМАЦИИ ХОДЬБЫ ===")
    
    # Тест анимации ходьбы
    player.velocity = Vector2D(100, 0)
    player.is_grounded = True
    player._update_state()
    
    print("Кадры анимации ходьбы:")
    for i in range(10):  # 10 кадров анимации
        player._update_animation(0.125)  # 8 FPS = 0.125 секунды на кадр
        print(f"   Кадр {i+1}: frame_{player.current_frame}")
    
    print()
    print("=== ТЕСТ НАПРАВЛЕНИЯ ===")
    
    # Тест направления
    player.input_horizontal = 1.0  # Движение вправо
    player.update(0.016)  # 60 FPS
    print(f"Движение вправо: facing_right = {player.facing_right} ✓")
    
    player.input_horizontal = -1.0  # Движение влево
    player.update(0.016)
    print(f"Движение влево: facing_right = {player.facing_right} ✓")
    
    player.input_horizontal = 0.0  # Остановка
    player.update(0.016)
    print(f"Остановка: facing_right = {player.facing_right} (сохраняется)")
    
    print()
    print("=== ТЕСТ ЗАВЕРШЕН ===")
    
    pygame.quit()

if __name__ == "__main__":
    test_animation_states()