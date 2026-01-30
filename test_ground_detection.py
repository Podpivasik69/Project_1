#!/usr/bin/env python3
"""
Тест обнаружения земли
"""

import pygame
import sys
from game.physics import Vector2D
from game.simple_player import SimplePlayer

def test_ground_detection():
    """Тестирует обнаружение земли."""
    
    # Инициализируем pygame минимально
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    # Создаем игрока
    player = SimplePlayer(Vector2D(100, 500))
    
    # Создаем платформу
    platform_rect = pygame.Rect(50, 572, 200, 20)  # Игрок должен стоять на ней
    
    print("=== ТЕСТ ОБНАРУЖЕНИЯ ЗЕМЛИ ===")
    print()
    
    # Тест 1: Игрок стоит на платформе
    print("1. Игрок стоит на платформе:")
    player.position = Vector2D(100, 500)  # 500 + 72 = 572 (касается платформы)
    player.velocity = Vector2D(0, 0)
    player.is_grounded = True
    
    on_ground = player.check_if_on_ground([platform_rect])
    print(f"   Позиция игрока: ({player.position.x}, {player.position.y})")
    print(f"   Платформа: ({platform_rect.x}, {platform_rect.y}, {platform_rect.width}, {platform_rect.height})")
    print(f"   Игрок на земле: {on_ground}")
    print(f"   is_grounded: {player.is_grounded}")
    
    # Симулируем обновление состояния
    if player.is_grounded and abs(player.velocity.y) < 0.5:
        player.velocity.y = 0
        player.in_air_frames = 0
    else:
        player.in_air_frames += 1
    
    player._update_state()
    effective_on_ground = player.is_grounded and player.in_air_frames < 3
    
    print(f"   effective_on_ground: {effective_on_ground}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: idle" + (" ✓" if player.current_state == "idle" else " ✗"))
    print()
    
    # Тест 2: Игрок в воздухе
    print("2. Игрок в воздухе:")
    player.position = Vector2D(100, 400)  # Высоко над платформой
    player.velocity = Vector2D(0, 50)  # Падает
    player.is_grounded = False
    player.in_air_frames = 10
    
    on_ground = player.check_if_on_ground([platform_rect])
    print(f"   Позиция игрока: ({player.position.x}, {player.position.y})")
    print(f"   Игрок на земле: {on_ground}")
    print(f"   is_grounded: {player.is_grounded}")
    
    player._update_state()
    effective_on_ground = player.is_grounded and player.in_air_frames < 3
    
    print(f"   effective_on_ground: {effective_on_ground}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: jumping" + (" ✓" if player.current_state == "jumping" else " ✗"))
    print()
    
    # Тест 3: Игрок на краю платформы
    print("3. Игрок на краю платформы:")
    player.position = Vector2D(240, 500)  # На правом краю платформы (250-48=202, платформа до 250)
    player.velocity = Vector2D(0, 0)
    player.is_grounded = True
    player.in_air_frames = 0
    
    on_ground = player.check_if_on_ground([platform_rect])
    print(f"   Позиция игрока: ({player.position.x}, {player.position.y})")
    print(f"   Игрок на земле: {on_ground}")
    print(f"   is_grounded: {player.is_grounded}")
    
    player._update_state()
    effective_on_ground = player.is_grounded and player.in_air_frames < 3
    
    print(f"   effective_on_ground: {effective_on_ground}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: idle" + (" ✓" if player.current_state == "idle" else " ✗"))
    print()
    
    # Тест 4: Игрок сошел с платформы
    print("4. Игрок сошел с платформы:")
    player.position = Vector2D(300, 500)  # За пределами платформы
    player.velocity = Vector2D(0, 0)
    player.is_grounded = True  # Еще считается на земле
    player.in_air_frames = 0
    
    on_ground = player.check_if_on_ground([platform_rect])
    print(f"   Позиция игрока: ({player.position.x}, {player.position.y})")
    print(f"   Игрок на земле: {on_ground}")
    print(f"   is_grounded ДО обновления: {player.is_grounded}")
    
    # Симулируем логику из simple_game.py
    if not on_ground and player.is_grounded:
        player.is_grounded = False
        print("   -> is_grounded сброшен в False")
    
    player._update_state()
    effective_on_ground = player.is_grounded and player.in_air_frames < 3
    
    print(f"   is_grounded ПОСЛЕ обновления: {player.is_grounded}")
    print(f"   effective_on_ground: {effective_on_ground}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: jumping" + (" ✓" if player.current_state == "jumping" else " ✗"))
    print()
    
    print("=== ТЕСТ ЗАВЕРШЕН ===")
    
    pygame.quit()

if __name__ == "__main__":
    test_ground_detection()