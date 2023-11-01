from __future__ import annotations

import math
import pygame
from src.actor import tile
import src.pickup as pickup
import src.animation as animation

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import src.player as player

ITEM_HUD_TEXTURE = pygame.image.load("Art/Cute_hud.png")
ITEM_HUD_TEXTURE = pygame.transform.scale(ITEM_HUD_TEXTURE, (tile, tile))

heart_anim = animation.Animation.from_dir("Art/Cute_health_ani", (tile,tile), 10)
tiny_heart_anim = animation.Animation.from_dir("Art/Cute_health_ani_tiny", (tile, tile), 10)
EMPTY_HEART= pygame.image.load("Art/Cute_health_empty.png")
EMPTY_HEART = pygame.transform.scale(EMPTY_HEART, (tile, tile))

def draw(size, framecount: int, player: player.Player):
    surface = pygame.Surface(size)
    for n in range(5):
        surface.blit(ITEM_HUD_TEXTURE, (tile*(n+4), 1))
    heart_anim.update(framecount)
    for n in range(player.max_health):
        if n < player.lives:
            surface.blit(heart_anim.texture, (tile*(math.floor(n/2)+4), tile))
        elif n==player.lives:
            if player.lives % 2:
                tiny_heart_anim.update(framecount)
                surface.blit(tiny_heart_anim.texture, (tile*(math.floor(player.lives/2) + 4), tile))
            else:
                surface.blit(heart_anim.texture, (tile*(math.floor(n/2)+4), tile))
        else:
            surface.blit(EMPTY_HEART, (tile*(math.floor(n/2)+4), tile))
    
    for n,i in enumerate(player.items):
        anim = pickup.ITEM_ANIMATIONS[i.__class__]
        anim.update(framecount)
        surface.blit(anim.texture, (tile*(n + 4), 1))
            
    return surface
