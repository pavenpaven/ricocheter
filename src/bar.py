from __future__ import annotations

import math
import pygame
from src.actor import tile
import src.pickup as pickup
from src.pickup import display_number
import src.animation as animation
from src.fps import FONT

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import src.player as player

ITEM_HUD_TEXTURE = pygame.image.load("Art/Cute_hud.png")
ITEM_HUD_TEXTURE = pygame.transform.scale(ITEM_HUD_TEXTURE, (tile, tile))

heart_anim = animation.Animation.from_dir("Art/Cute_health_ani", (tile,tile), 10)
tiny_heart_anim = animation.Animation.from_dir("Art/Cute_health_ani_tiny", (tile, tile), 10)
EMPTY_HEART= pygame.image.load("Art/Cute_health_empty.png")
EMPTY_HEART = pygame.transform.scale(EMPTY_HEART, (tile, tile))
anim = animation.Animation("Art/Cute_money_money_money", (tile,tile), 1)

AMMO_HUD_FULL = pygame.image.load("Art/Cute_ammo_hud.png")
AMMO_HUD_FULL = pygame.transform.scale(AMMO_HUD_FULL, (tile, tile))
AMMO_HUD_EMPTY = pygame.image.load("Art/Cute_ammo_hud_empty.png")
AMMO_HUD_EMPTY = pygame.transform.scale(AMMO_HUD_EMPTY, (tile, tile))
AMMO_HUD_RELOAD = pygame.image.load("Art/Cute_ammo_hud_reload.png")
AMMO_HUD_RELOAD = pygame.transform.scale(AMMO_HUD_RELOAD, (tile, tile))



def render_item(item, framecount):
    anim = pickup.ITEM_ANIMATIONS[item.__class__]
    anim.update(framecount)
    surface = pygame.Surface(anim.texture.get_size(), pygame.SRCALPHA)
    surface.blit(anim.texture, (0,0))
    fade_rect         = surface.get_rect().copy()
    scale_factor      = item.cooldown / item.COOLDOWN
    y_cord            = fade_rect.height*(1-scale_factor)
    fade_rect.height *= scale_factor

    rect_surface = pygame.Surface(fade_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(rect_surface, (100, 100, 100, 200), fade_rect)

    surface.blit(rect_surface, (0, y_cord))

    return surface
    

def draw(size, framecount: int, player: player.Player):
    surface = pygame.Surface(size)
    for n in range(5):
        surface.blit(ITEM_HUD_TEXTURE, (tile*(n+4), 1))
    surface.blit(FONT.render(str(player.money), True, (255,255,255)), (10*tile, tile))
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

    for n in range(player.magazine_size):
        if n < player.magazine and not player.reloading:
            surface.blit(AMMO_HUD_FULL, (tile*(n + 10), 0))
        elif n <= player.magazine and player.reloading:
            surface.blit(AMMO_HUD_RELOAD, (tile*(n + 10), 0))
        else:
            surface.blit(AMMO_HUD_EMPTY, (tile*(n + 10), 0))
            
            
    for n,i in enumerate(player.items):
        surface.blit(render_item(i, framecount), (tile*(n + 4), 1))
            
    return surface
