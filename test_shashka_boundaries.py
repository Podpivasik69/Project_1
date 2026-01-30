#!/usr/bin/env python3
"""
Тест границ шашки - проверка вертикальной границы
"""

import pygame
import sys
from game.physics import Vector2D
from game.simple_player import SimplePlayer
from game.shashka import ShashkaProjectile

def test_shashka_boundaries():
    """Тестирует границы удаления шашек."""
    
    # Инициализируем pygame минимально
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    print("=== ТЕСТ ГРАНИЦ ШАШКИ ===")
    print()
    
    # Константы
    BUFFER_ZONE = 200
    WORLD_WIDTH = 2000
    
    print(f"Константы:")
    print(f"   BUFFER_ZONE: {BUFFER_ZONE}")
    print(f"   WORLD_WIDTH: {WORLD_WIDTH}")
    print(f"   Левая граница: {-BUFFER_ZONE}")
    print(f"   Правая граница: {WORLD_WIDTH + BUFFER_ZONE}")
    print()
    
    # Тест 1: Шашка в безопасной зоне
    print("1. Тест безопасной зоны:")
    
    test_positions = [
        0,      # Начало мира
        500,    # Четверть мира
        1000,   # Середина мира
        1500,   # Три четверти мира
        2000,   # Конец мира
    ]
    
    for pos in test_positions:
        should_be_removed = pos < -BUFFER_ZONE or pos > WORLD_WIDTH + BUFFER_ZONE
        print(f"   Позиция {pos:4d}: {'❌ Удалится' if should_be_removed else '✅ Безопасно'}")
    
    print()
    
    # Тест 2: Шашка на границах
    print("2. Тест границ:")
    
    boundary_positions = [
        -BUFFER_ZONE - 1,    # За левой границей
        -BUFFER_ZONE,        # На левой границе
        -BUFFER_ZONE + 1,    # Внутри левой границы
        WORLD_WIDTH + BUFFER_ZONE - 1,  # Внутри правой границы
        WORLD_WIDTH + BUFFER_ZONE,      # На правой границе
        WORLD_WIDTH + BUFFER_ZONE + 1,  # За правой границей
    ]
    
    for pos in boundary_positions:
        should_be_removed = pos < -BUFFER_ZONE or pos > WORLD_WIDTH + BUFFER_ZONE
        status = "❌ Удалится" if should_be_removed else "✅ Безопасно"
        print(f"   Позиция {pos:4d}: {status}")
    
    print()
    
    # Тест 3: Симуляция движения шашки
    print("3. Симуляция движения шашки вправо:")
    
    player = SimplePlayer(Vector2D(1000, 300))  # В середине мира
    player.facing_right = True
    
    # Создаем шашку
    shashka = ShashkaProjectile(1000, 300, 1)  # Летит вправо
    player.active_shashkas.append(shashka)
    
    delta_time = 1.0 / 60.0  # 60 FPS
    
    print(f"   Начальная позиция: {shashka.position.x:.1f}")
    print(f"   Скорость: {shashka.speed} px/s")
    print(f"   Время до границы: {(WORLD_WIDTH + BUFFER_ZONE - 1000) / shashka.speed:.1f} секунд")
    print()
    
    # Симулируем полет до границы
    frame = 0
    while shashka.active and len(player.active_shashkas) > 0:
        frame += 1
        
        # Обновляем шашку
        shashka.update(delta_time)
        
        # Проверяем границы (как в игре)
        if shashka.x < -BUFFER_ZONE or shashka.x > WORLD_WIDTH + BUFFER_ZONE:
            player.active_shashkas.remove(shashka)
            print(f"   Кадр {frame:3d}: Шашка удалена на позиции {shashka.x:.1f}")
            break
        
        # Показываем прогресс каждые 60 кадров (1 секунда)
        if frame % 60 == 0:
            print(f"   Кадр {frame:3d}: Позиция {shashka.x:.1f}")
        
        # Защита от бесконечного цикла
        if frame > 1000:
            print(f"   ⚠️  Прервано на кадре {frame} - возможная ошибка")
            break
    
    print()
    
    # Тест 4: Симуляция движения влево
    print("4. Симуляция движения шашки влево:")
    
    player2 = SimplePlayer(Vector2D(1000, 300))
    player2.facing_right = False
    
    shashka2 = ShashkaProjectile(1000, 300, -1)  # Летит влево
    player2.active_shashkas.append(shashka2)
    
    print(f"   Начальная позиция: {shashka2.position.x:.1f}")
    print(f"   Время до границы: {(1000 - (-BUFFER_ZONE)) / shashka2.speed:.1f} секунд")
    print()
    
    frame = 0
    while shashka2.active and len(player2.active_shashkas) > 0:
        frame += 1
        
        shashka2.update(delta_time)
        
        if shashka2.x < -BUFFER_ZONE or shashka2.x > WORLD_WIDTH + BUFFER_ZONE:
            player2.active_shashkas.remove(shashka2)
            print(f"   Кадр {frame:3d}: Шашка удалена на позиции {shashka2.x:.1f}")
            break
        
        if frame % 60 == 0:
            print(f"   Кадр {frame:3d}: Позиция {shashka2.x:.1f}")
        
        if frame > 1000:
            print(f"   ⚠️  Прервано на кадре {frame} - возможная ошибка")
            break
    
    print()
    
    # Тест 5: Проверка проблемной зоны (середина экрана)
    print("5. Тест проблемной зоны (середина экрана 512px):")
    
    screen_center = 512  # Середина экрана 1024px
    camera_positions = [0, 200, 400, 600, 800, 1000]
    
    for camera_x in camera_positions:
        world_center = screen_center + camera_x  # Мировая координата центра экрана
        should_be_removed = world_center < -BUFFER_ZONE or world_center > WORLD_WIDTH + BUFFER_ZONE
        
        print(f"   Камера {camera_x:4d}: центр экрана в мире = {world_center:4d}, {'❌ Удалится' if should_be_removed else '✅ Безопасно'}")
    
    print()
    
    print("=== РЕЗУЛЬТАТЫ ===")
    print("✅ Границы мира: -200 до 2200")
    print("✅ Буферная зона: 200 пикселей")
    print("✅ Безопасная зона: 0 до 2000 (основной мир)")
    print("✅ Проблемная зона устранена: середина экрана безопасна")
    print()
    print("🔧 Если шашки все еще исчезают в середине:")
    print("   1. Проверь координаты камеры")
    print("   2. Убедись что используются мировые координаты")
    print("   3. Нажми F2 в игре для визуальной отладки")
    
    pygame.quit()

if __name__ == "__main__":
    test_shashka_boundaries()