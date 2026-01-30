"""
Asset Management System
Handles loading and caching of game assets (images, sounds, etc.)
"""

import pygame
import os
from typing import Dict, Optional, Tuple
from game.physics import Vector2D


class AssetManager:
    """
    Manages loading and caching of game assets.
    """
    
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.loaded_themes: Dict[str, Dict] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}  # Добавляем звуки
        
        # Default placeholder colors
        self.placeholder_colors = {
            'player_idle': (100, 150, 255),
            'player_walk': (120, 170, 255),
            'player_jump': (150, 255, 150),
            'player_fall': (255, 150, 150),
            'player_crouch': (255, 255, 150),
            'platform': (139, 69, 19),
            'background': (135, 206, 235)
        }
    
    def load_image(self, path: str, scale: Tuple[int, int] = None) -> Optional[pygame.Surface]:
        """
        Load an image from file path.
        
        Args:
            path: Path to image file
            scale: Optional (width, height) to scale image
            
        Returns:
            Loaded pygame Surface or None if failed
        """
        if path in self.images:
            return self.images[path]
        
        try:
            if os.path.exists(path):
                # Initialize display if not already done
                if pygame.get_init() and not pygame.display.get_init():
                    pygame.display.set_mode((1, 1))
                
                image = pygame.image.load(path).convert_alpha()
                
                if scale:
                    image = pygame.transform.scale(image, scale)
                
                self.images[path] = image
                print(f"Loaded image: {path}")
                return image
            else:
                print(f"Image not found: {path}")
                return None
                
        except pygame.error as e:
            print(f"Failed to load image {path}: {e}")
            return None
    
    def create_placeholder(self, size: Tuple[int, int], color: Tuple[int, int, int], 
                          text: str = None) -> pygame.Surface:
        """
        Create a placeholder surface when image is missing.
        
        Args:
            size: (width, height) of placeholder
            color: RGB color
            text: Optional text to draw on placeholder
            
        Returns:
            Placeholder pygame Surface
        """
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(color)
        
        # Add border
        pygame.draw.rect(surface, (0, 0, 0), (0, 0, size[0], size[1]), 2)
        
        # Add text if provided and pygame is initialized
        if text and pygame.get_init() and pygame.font.get_init():
            try:
                font = pygame.font.Font(None, min(size[0] // 4, size[1] // 4, 24))
                text_surface = font.render(text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(size[0] // 2, size[1] // 2))
                surface.blit(text_surface, text_rect)
            except:
                pass  # Ignore font errors
        
        return surface
    
    def get_player_sprite(self, state: str, size: Tuple[int, int] = (48, 72)) -> pygame.Surface:
        """
        Get player sprite for given state.
        
        Args:
            state: Player state ('idle', 'walk', 'jump', 'fall', 'crouch')
            size: Size of sprite
            
        Returns:
            Player sprite surface
        """
        # Map states to your actual file names (обновленные пути)
        sprite_mapping = {
            'idle': 'assets/player/player_static.png',
            'walk': 'assets/player/player_walk/0.png',  # Default walk frame
            'jump': 'assets/player/player_jump.png',
            'fall': 'assets/player/player_jump.png',  # Use jump sprite for falling if no separate fall sprite
            'crouch': 'assets/player/player_shift.png'
        }
        
        sprite_path = sprite_mapping.get(state)
        if sprite_path:
            sprite = self.load_image(sprite_path, size)
            if sprite:
                return sprite
        
        # Create placeholder if file not found
        color = self.placeholder_colors.get(f'player_{state}', (100, 150, 255))
        return self.create_placeholder(size, color, state.upper())
    
    def get_walk_animation_frame_by_number(self, frame_number: int, size: Tuple[int, int] = (48, 72)) -> pygame.Surface:
        """
        Get specific walk animation frame by file number.
        
        Args:
            frame_number: Frame file number (0, 1, 2, 4, 5)
            size: Size of sprite
            
        Returns:
            Walk animation frame
        """
        sprite_path = f'assets/player/player_walk/{frame_number}.png'  # Обновленный путь
        sprite = self.load_image(sprite_path, size)
        
        if sprite:
            return sprite
        
        # Fallback to idle sprite
        return self.get_player_sprite('idle', size)
    
    def get_wolf_sprite(self, state: str, size: Tuple[int, int] = (64, 48)) -> pygame.Surface:
        """
        Get wolf sprite for given state.
        
        Args:
            state: Wolf state ('idle', 'walk', 'attack')
            size: Size of sprite
            
        Returns:
            Wolf sprite surface
        """
        sprite_mapping = {
            'idle': 'assets/wolf/static.png',
            'walk': 'assets/wolf/wolf_walk/0.png',  # Default walk frame
            'attack': 'assets/wolf/static.png'  # Use static for attack if no separate sprite
        }
        
        sprite_path = sprite_mapping.get(state)
        if sprite_path:
            sprite = self.load_image(sprite_path, size)
            if sprite:
                return sprite
        
        # Create placeholder if file not found
        color = (150, 100, 50)  # Brown for wolf
        return self.create_placeholder(size, color, f"WOLF_{state.upper()}")
    
    def get_wolf_walk_frame(self, frame_number: int, size: Tuple[int, int] = (64, 48)) -> pygame.Surface:
        """
        Get specific wolf walk animation frame.
        
        Args:
            frame_number: Frame file number (0, 1, 3, 4, 5, 6)
            size: Size of sprite
            
        Returns:
            Wolf walk animation frame
        """
        sprite_path = f'assets/wolf/wolf_walk/{frame_number}.png'
        sprite = self.load_image(sprite_path, size)
        
        if sprite:
            return sprite
        
        # Fallback to idle sprite
        return self.get_wolf_sprite('idle', size)
    
    def get_bear_sprite(self, state: str, size: Tuple[int, int] = (80, 64)) -> pygame.Surface:
        """
        Get bear sprite for given state.
        
        Args:
            state: Bear state ('idle', 'walk', 'attack')
            size: Size of sprite
            
        Returns:
            Bear sprite surface
        """
        sprite_mapping = {
            'idle': 'assets/bear/static.png',  # Теперь есть статичный медведь!
            'walk': 'assets/bear/bear_walk/0.png',  # Default walk frame
            'attack': 'assets/bear/bear_attack/0.png'  # Default attack frame
        }
        
        sprite_path = sprite_mapping.get(state)
        if sprite_path:
            sprite = self.load_image(sprite_path, size)
            if sprite:
                return sprite
        
        # Create placeholder if file not found
        color = (100, 50, 25)  # Dark brown for bear
        return self.create_placeholder(size, color, f"BEAR_{state.upper()}")
    
    def get_balalaika_sprite(self, size: Tuple[int, int] = (48, 32)) -> pygame.Surface:
        """Get balalaika sprite."""
        sprite = self.load_image("assets/balalaika.png", size)
        
        if sprite:
            return sprite
        
        # Create placeholder
        color = (139, 69, 19)  # Brown for wood
        return self.create_placeholder(size, color, "♪")
    
    def get_bear_walk_frame(self, frame_number: int, size: Tuple[int, int] = (80, 64)) -> pygame.Surface:
        """
        Get specific bear walk animation frame.
        
        Args:
            frame_number: Frame file number (0, 1, 2, 3, 4, 5)
            size: Size of sprite
            
        Returns:
            Bear walk animation frame
        """
        sprite_path = f'assets/bear/bear_walk/{frame_number}.png'
        sprite = self.load_image(sprite_path, size)
        
        if sprite:
            return sprite
        
        # Fallback to idle sprite
        return self.get_bear_sprite('idle', size)
    
    def get_bear_attack_frame(self, frame_number: int, size: Tuple[int, int] = (80, 64)) -> pygame.Surface:
        """
        Get specific bear attack animation frame.
        
        Args:
            frame_number: Frame file number (0, 1, 2, 3, 4, 5)
            size: Size of sprite
            
        Returns:
            Bear attack animation frame
        """
        sprite_path = f'assets/bear/bear_attack/{frame_number}.png'
        sprite = self.load_image(sprite_path, size)
        
        if sprite:
            return sprite
        
        # Fallback to idle sprite
        return self.get_bear_sprite('idle', size)
    
    def get_weapon_sprite(self, weapon_type: str, size: Tuple[int, int] = (32, 64)) -> pygame.Surface:
        """
        Get weapon sprite.
        
        Args:
            weapon_type: Type of weapon ('shashka')
            size: Size of sprite
            
        Returns:
            Weapon sprite surface
        """
        sprite_mapping = {
            'shashka': 'assets/shpaga.png'
        }
        
        sprite_path = sprite_mapping.get(weapon_type)
        if sprite_path:
            sprite = self.load_image(sprite_path, size)
            if sprite:
                return sprite
        
        # Create placeholder
        color = (200, 200, 200)  # Silver for weapon
        return self.create_placeholder(size, color, weapon_type.upper())
    
    def get_platform_texture(self, platform_type: str = "default", 
                           size: Tuple[int, int] = (100, 20)) -> pygame.Surface:
        """
        Get platform texture.
        
        Args:
            platform_type: Type of platform
            size: Size of texture
            
        Returns:
            Platform texture surface
        """
        # Пробуем разные пути для платформ
        possible_paths = [
            "assets/grass_ground.jpg",  # Новая текстура земли
            "assets/triangles.png",     # Новая текстура платформ
            f"assets/ingushetia/platform_{platform_type}.png",
            f"assets/platform_{platform_type}.png",
            f"assets/platform.png"
        ]
        
        for texture_path in possible_paths:
            texture = self.load_image(texture_path, size)
            if texture:
                return texture
        
        # Create nice-looking platform placeholder
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Gradient effect for stone-like appearance
        for y in range(size[1]):
            brightness = 1.0 - (y / size[1]) * 0.3  # Darker at bottom
            color = (
                int(139 * brightness),  # Brown
                int(69 * brightness),
                int(19 * brightness)
            )
            pygame.draw.line(surface, color, (0, y), (size[0], y))
        
        # Add some texture lines
        for i in range(0, size[0], 20):
            pygame.draw.line(surface, (100, 50, 10), (i, 0), (i, size[1]), 1)
        
        # Border
        pygame.draw.rect(surface, (80, 40, 10), (0, 0, size[0], size[1]), 2)
        
        return surface
    
    def get_background(self, bg_type: str = "sky") -> Optional[pygame.Surface]:
        """
        Get background image.
        
        Args:
            bg_type: Type of background
            
        Returns:
            Background surface or None
        """
        # Пробуем новые фоны
        possible_paths = [
            "assets/background/back.jpg",
            "assets/background/tower.png", 
            "assets/background/tree.png",
            f"assets/ingushetia/background_{bg_type}.png"
        ]
        
        for bg_path in possible_paths:
            bg = self.load_image(bg_path)
            if bg:
                return bg
        
        return None
    
    def get_background(self, bg_type: str = "sky") -> Optional[pygame.Surface]:
        """
        Get background image.
        
        Args:
            bg_type: Type of background
            
        Returns:
            Background surface or None
        """
        bg_path = f"assets/ingushetia/background_{bg_type}.png"
        return self.load_image(bg_path)
    
    def load_theme_config(self, theme_name: str) -> Dict:
        """
        Load theme configuration from JSON.
        
        Args:
            theme_name: Name of theme (e.g., 'ingushetia')
            
        Returns:
            Theme configuration dictionary
        """
        if theme_name in self.loaded_themes:
            return self.loaded_themes[theme_name]
        
        config_path = f"game/regions/{theme_name}.json"
        
        try:
            import json
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.loaded_themes[theme_name] = config
                    print(f"Loaded theme config: {theme_name}")
                    return config
        except Exception as e:
            print(f"Failed to load theme config {theme_name}: {e}")
        
        # Return default config
        default_config = {
            "name": theme_name.title(),
            "assets": {
                "background": f"assets/{theme_name}/background.png",
                "platform": f"assets/{theme_name}/platform.png",
                "player": f"assets/{theme_name}/player.png"
            },
            "gameplay": {
                "gravity": 980.0,
                "jump_force": 400.0,
                "move_speed": 200.0
            }
        }
        
        self.loaded_themes[theme_name] = default_config
        return default_config
    
    def preload_player_sprites(self, size: Tuple[int, int] = (48, 72)) -> Dict[str, pygame.Surface]:
        """
        Preload all player sprites.
        
        Args:
            size: Size of sprites
            
        Returns:
            Dictionary of state -> sprite
        """
        states = ['idle', 'walk', 'jump', 'fall', 'crouch']
        sprites = {}
        
        for state in states:
            sprites[state] = self.get_player_sprite(state, size)
        
        return sprites
    
    def clear_cache(self) -> None:
        """Clear all cached assets."""
        self.images.clear()
        self.fonts.clear()
        self.loaded_themes.clear()
        self.sounds.clear()
        print("Asset cache cleared")
    
    def load_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound from file path.
        
        Args:
            path: Path to sound file
            
        Returns:
            Loaded pygame Sound or None if failed
        """
        if path in self.sounds:
            return self.sounds[path]
        
        try:
            if os.path.exists(path):
                # Инициализируем mixer если не инициализирован
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                
                sound = pygame.mixer.Sound(path)
                self.sounds[path] = sound
                print(f"Loaded sound: {path}")
                return sound
            else:
                print(f"Sound not found: {path}")
                return None
                
        except pygame.error as e:
            print(f"Failed to load sound {path}: {e}")
            return None
    
    def get_wolf_sound(self) -> Optional[pygame.mixer.Sound]:
        """Get wolf attack sound."""
        return self.load_sound("assets/wolf/wolf_sound.mp3")


# Global asset manager instance
asset_manager = AssetManager()