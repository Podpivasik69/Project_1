#!/usr/bin/env python3
"""
Тест стабилизации анимации игрока
Проверяет устранение дрожания при стоянии на платформах
"""

import pygame
import sys
from game.physics import Vector2D
from game.simple_player import SimplePlayer

def test_animation_stability():
    """Тестирует стабилизацию анимации игрока."""
    
    # Инициализируем pygame минимально
    pygame.init()
    pygame.display.set_mode((1, 1))  # Минимальное окно
    
    # Создаем игрока
    player = SimplePlayer(Vector2D(100, 100))
    
    print("=== ТЕСТ СТАБИЛИЗАЦИИ АНИМАЦИИ ===")
    print()
    
    # Тест 1: Стабильное стояние на платформе
    print("1. Тест стабильного стояния:")
    player.velocity = Vector2D(0, 0)
    player.is_grounded = True
    player.in_air_frames = 0
    player._update_state()
    
    effective_on_ground = player.is_grounded and player.in_air_frames < 3
    print(f"   velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   in_air_frames = {player.in_air_frames}")
    print(f"   effective_on_ground = {effective_on_ground}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: idle" + (" ✓" if player.current_state == "idle" else " ✗"))
    print()
    
    # Тест 2: Микро-дрожание (должно игнорироваться)
    print("2. Тест микро-дрожания (velocity.y = 0.3):")
    player.velocity = Vector2D(0, 0.3)  # Микро-скорость
    player.is_grounded = True
    player.in_air_frames = 1  # Недавно был в воздухе
    
    # Симулируем стабилизацию
    if player.is_grounded and abs(player.velocity.y) < 0.5:
        player.velocity.y = 0
        player.in_air_frames = 0
    else:
        player.in_air_frames += 1
    
    player._update_state()
    effective_on_ground = player.is_grounded and player.in_air_frames < 3
    
    print(f"   velocity.y после стабилизации = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   in_air_frames = {player.in_air_frames}")
    print(f"   effective_on_ground = {effective_on_ground}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: idle" + (" ✓" if player.current_state == "idle" else " ✗"))
    print()
    
    # Тест 3: Реальное падение (не должно стабилизироваться)
    print("3. Тест реального падения (velocity.y = 50):")
    player.velocity = Vector2D(0, 50)  # Реальная скорость падения
    player.is_grounded = False
    player.in_air_frames = 10
    
    # Симулируем стабилизацию (не должна сработать)
    if player.is_grounded and abs(player.velocity.y) < 0.5:
        player.velocity.y = 0
        player.in_air_frames = 0
    else:
        player.in_air_frames += 1
    
    player._update_state()
    effective_on_ground = player.is_grounded and player.in_air_frames < 3
    
    print(f"   velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   in_air_frames = {player.in_air_frames}")
    print(f"   effective_on_ground = {effective_on_ground}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: jumping" + (" ✓" if player.current_state == "jumping" else " ✗"))
    print()
    
    # Тест 4: Буферная зона (2 кадра в воздухе, но на земле)
    print("4. Тест буферной зоны (2 кадра в воздухе):")
    player.velocity = Vector2D(0, 0)
    player.is_grounded = True
    player.in_air_frames = 2  # В пределах буфера (< 3)
    player._update_state()
    
    effective_on_ground = player.is_grounded and player.in_air_frames < 3
    print(f"   velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   in_air_frames = {player.in_air_frames}")
    print(f"   effective_on_ground = {effective_on_ground}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: idle" + (" ✓" if player.current_state == "idle" else " ✗"))
    print()
    
    # Тест 5: Превышение буфера (4 кадра в воздухе)
    print("5. Тест превышения буфера (4 кадра в воздухе):")
    player.velocity = Vector2D(0, 0)
    player.is_grounded = True  # Физически на земле
    player.in_air_frames = 4  # Но превышен буфер (>= 3)
    player._update_state()
    
    effective_on_ground = player.is_grounded and player.in_air_frames < 3
    print(f"   velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   in_air_frames = {player.in_air_frames}")
    print(f"   effective_on_ground = {effective_on_ground}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: jumping" + (" ✓" if player.current_state == "jumping" else " ✗"))
    print()
    
    # Тест 6: Медленное движение по земле
    print("6. Тест медленного движения (velocity.x = 0.05):")
    player.velocity = Vector2D(0.05, 0)  # Очень медленное движение
    player.is_grounded = True
    player.in_air_frames = 0
    player._update_state()
    
    effective_on_ground = player.is_grounded and player.in_air_frames < 3
    print(f"   velocity.x = {player.velocity.x}")
    print(f"   velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   in_air_frames = {player.in_air_frames}")
    print(f"   effective_on_ground = {effective_on_ground}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: idle" + (" ✓" if player.current_state == "idle" else " ✗"))
    print()
    
    # Тест 7: Нормальное движение по земле
    print("7. Тест нормального движения (velocity.x = 1.0):")
    player.velocity = Vector2D(1.0, 0)  # Нормальное движение
    player.is_grounded = True
    player.in_air_frames = 0
    player._update_state()
    
    effective_on_ground = player.is_grounded and player.in_air_frames < 3
    print(f"   velocity.x = {player.velocity.x}")
    print(f"   velocity.y = {player.velocity.y}")
    print(f"   is_grounded = {player.is_grounded}")
    print(f"   in_air_frames = {player.in_air_frames}")
    print(f"   effective_on_ground = {effective_on_ground}")
    print(f"   Состояние: {player.current_state}")
    print(f"   ✓ Ожидается: walking" + (" ✓" if player.current_state == "walking" else " ✗"))
    print()
    
    print("=== СИМУЛЯЦИЯ ПРИЗЕМЛЕНИЯ ===")
    
    # Симуляция приземления с дрожанием
    print("Симуляция приземления на платформу:")
    player.velocity = Vector2D(0, 100)  # Падает
    player.is_grounded = False
    player.in_air_frames = 20
    
    for frame in range(10):
        print(f"Кадр {frame + 1}:")
        
        # Симуляция коллизии с платформой на 5-м кадре
        if frame == 4:
            print("   -> Коллизия с платформой!")
            player.position.y = 500  # Четкое позиционирование
            player.velocity.y = 0    # Полное обнуление
            player.is_grounded = True
        
        # Симуляция стабилизации
        if player.is_grounded and abs(player.velocity.y) < 0.5:
            player.velocity.y = 0
            player.in_air_frames = 0
        else:
            player.in_air_frames += 1
        
        player._update_state()
        effective_on_ground = player.is_grounded and player.in_air_frames < 3
        
        print(f"   velocity.y = {player.velocity.y:.1f}")
        print(f"   is_grounded = {player.is_grounded}")
        print(f"   in_air_frames = {player.in_air_frames}")
        print(f"   effective_on_ground = {effective_on_ground}")
        print(f"   Состояние: {player.current_state}")
        print()
    
    print("=== ТЕСТ ЗАВЕРШЕН ===")
    
    pygame.quit()

if __name__ == "__main__":
    test_animation_stability()