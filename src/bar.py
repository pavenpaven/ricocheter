from __future__ import annotations

import pygame
from src.actor import tile
import src.pickup as pickup

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import src.player as player


def draw(size, framecount: int, player: player.Player):
    surface = pygame.Surface(size)
    for n,i in enumerate(player.items):
        anim = pickup.ITEM_ANIMATIONS[i.__class__]
        anim.update(framecount)
        surface.blit(anim.texture, (tile*(n + 4), 1))
            
    return surface
