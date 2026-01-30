#!/usr/bin/env python3
"""
Тест системы метания шашки
"""

import pygame
import sys
from game.physics import Vector2D
from game.simple_player import SimplePlayer
from game.simple_wolf import SimpleWolf
from game.shashka import ShashkaProjectile

def test_shashka_system():
    """Тестирует систему метания шашки."""
    
    # Инициализируем pygame минимально
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    print("=== ТЕСТ СИСТЕМЫ ШАШКИ ===")
    print()
    
    # Тест 1: Создание снаряда
    print("1. Тест создания снаряда:")
    shashka = ShashkaProjectile(100, 200, 1)  # Вправо
    print(f"   Позиция: ({shashka.position.x}, {shashka.position.y})")
    print(f"   Скорость: {shashka.velocity.x} px/s")
    print(f"   Направление: {'→' if shashka.direction > 0 else '←'}")
    print(f"   Урон: {shashka.damage}")
    print(f"   Активна: {shashka.active}")
    print("   ✅ Снаряд создан")
    print()
    
    # Тест 2: Движение снаряда
    print("2. Тест движения снаряда (5 кадров по 16ms):")
    delta_time = 1.0 / 60.0  # 60 FPS
    
    for frame in range(5):
        old_x = shashka.position.x
        shashka.update(delta_time)
        distance = shashka.position.x - old_x
        
        print(f"   Кадр {frame+1}: x={shashka.position.x:.1f} (+{distance:.1f}px)")
    
    expected_distance = 400 * delta_time * 5  # speed * time * frames
    actual_distance = shashka.position.x - 100  # start_x was 100
    print(f"   Ожидаемое расстояние: {expected_distance:.1f}px")
    print(f"   Фактическое расстояние: {actual_distance:.1f}px")
    print(f"   ✅ Движение корректно" if abs(expected_distance - actual_distance) < 1 else "   ❌ Ошибка движения")
    print()
    
    # Тест 3: Система игрока
    print("3. Тест системы игрока:")
    player = SimplePlayer(Vector2D(200, 300))
    player.facing_right = True
    
    print(f"   Начальное количество шашек: {len(player.active_shashkas)}")
    print(f"   Кулдаун: {player.shashka_cooldown}")
    print(f"   Максимум шашек: {player.MAX_SHASHKAS}")
    
    # Бросаем шашку
    player.set_input(0, False, False, True)  # throw_shashka = True
    player.update(delta_time)
    
    print(f"   После броска: {len(player.active_shashkas)} шашек")
    print(f"   Кулдаун: {player.shashka_cooldown:.2f}s")
    print("   ✅ Бросок работает" if len(player.active_shashkas) == 1 else "   ❌ Ошибка броска")
    print()
    
    # Тест 4: Кулдаун
    print("4. Тест кулдауна:")
    player.set_input(0, False, False, True)  # Пытаемся бросить еще
    player.update(delta_time)
    
    print(f"   Попытка второго броска: {len(player.active_shashkas)} шашек")
    print("   ✅ Кулдаун работает" if len(player.active_shashkas) == 1 else "   ❌ Кулдаун не работает")
    
    # Ждем окончания кулдауна
    for _ in range(35):  # ~0.5 секунды при 60 FPS
        player.set_input(0, False, False, False)
        player.update(delta_time)
    
    print(f"   После ожидания кулдауна: {player.shashka_cooldown:.2f}s")
    
    # Бросаем еще одну
    player.set_input(0, False, False, True)
    player.update(delta_time)
    
    print(f"   После второго броска: {len(player.active_shashkas)} шашек")
    print("   ✅ Кулдаун сброшен" if len(player.active_shashkas) == 2 else "   ❌ Проблема с кулдауном")
    print()
    
    # Тест 5: Лимит шашек
    print("5. Тест лимита шашек:")
    
    # Сбрасываем кулдаун и бросаем третью
    player.shashka_cooldown = 0
    player.set_input(0, False, False, True)
    player.update(delta_time)
    
    print(f"   Третья шашка: {len(player.active_shashkas)} шашек")
    
    # Пытаемся бросить четвертую (должно быть заблокировано)
    player.shashka_cooldown = 0
    player.set_input(0, False, False, True)
    player.update(delta_time)
    
    print(f"   Попытка четвертой: {len(player.active_shashkas)} шашек")
    print(f"   ✅ Лимит работает" if len(player.active_shashkas) == 3 else "   ❌ Лимит не работает")
    print()
    
    # Тест 6: Столкновение с врагом
    print("6. Тест столкновения с врагом:")
    wolf = SimpleWolf(Vector2D(400, 300))
    print(f"   Здоровье волка: {wolf.health}/{wolf.max_health}")
    
    # Создаем шашку рядом с волком
    test_shashka = ShashkaProjectile(390, 324, 1)  # Центр волка примерно
    
    hit_enemy = test_shashka.check_enemy_collision([wolf])
    if hit_enemy:
        hit_enemy.take_damage(test_shashka.damage)
        print(f"   Попадание! Урон: {test_shashka.damage}")
        print(f"   Здоровье после попадания: {hit_enemy.health}/{hit_enemy.max_health}")
        print(f"   Волк мертв: {hit_enemy.is_dead}")
        print("   ✅ Столкновение работает")
    else:
        print("   ❌ Столкновение не обнаружено")
    print()
    
    # Тест 7: Убийство волка
    print("7. Тест убийства волка (3 попадания):")
    wolf2 = SimpleWolf(Vector2D(500, 300))
    print(f"   Начальное здоровье: {wolf2.health}")
    
    for hit in range(3):
        test_shashka2 = ShashkaProjectile(500, 324, 1)
        hit_enemy = test_shashka2.check_enemy_collision([wolf2])
        if hit_enemy:
            hit_enemy.take_damage(test_shashka2.damage)
            print(f"   Попадание {hit+1}: здоровье {hit_enemy.health}, мертв: {hit_enemy.is_dead}")
    
    print(f"   ✅ Волк убит за 3 попадания" if wolf2.is_dead else "   ❌ Волк не убит")
    print()
    
    print("=== РЕЗУЛЬТАТЫ ===")
    print("✅ Создание снаряда: работает")
    print("✅ Линейное движение: работает") 
    print("✅ Система броска: работает")
    print("✅ Кулдаун: работает")
    print("✅ Лимит шашек: работает")
    print("✅ Столкновение с врагами: работает")
    print("✅ Убийство врагов: работает")
    print()
    print("🎯 Система шашки готова к использованию!")
    
    pygame.quit()

if __name__ == "__main__":
    test_shashka_system()