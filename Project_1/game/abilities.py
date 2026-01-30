"""
Abilities System Module
Система способностей и заклинаний
"""

import pygame
import math
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from game.physics import Vector2D
from game.utils import Colors


@dataclass
class AbilityData:
    """Данные способности."""
    name: str
    description: str
    mana_cost: int
    cooldown: float
    damage: int = 0
    range: float = 100.0
    area_of_effect: float = 0.0
    duration: float = 0.0
    icon_path: str = ""
    sound_path: str = ""


class AbilitySystem:
    """
    Система управлени