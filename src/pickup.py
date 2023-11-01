import pygame
from src.animation import Animation
import src.actor as actor
from src.actor import tile


SHADOW = pygame.image.load("Art/shadow_test.png")
SHADOW = pygame.transform.scale(SHADOW, (tile, tile))

class Item:
    TEXTURE = "pancake"
    FRAME_DELAY = 4
    PERMANENT = True
    def on_pickup(self, player) -> None:# no type lol
        pass
    
    
class Pancake(Item):
    TEXTURE = "Art/Cute_food_panke_beter"
    FRAME_DELAY = 15
    PERMANENT = False
    def on_pickup(self, player) -> None:
        player.lives += 2
    
class Barrel (Item):
    TEXTURE = "Art/Cute_item_barrel"
    FRAME_DELAY = 4

class Shopkeeper(Item):
    TEXTURE = "Art/Cute_npc_vampir_ani"
    FRAME_DELAY = 4
    def on_pickup(self, player) -> None:
        player.accel*=1.4
        player.dry_friction *= 1.8
        player.drag *= 1.8

class Key(Item):
    TEXTURE = "Art/Cute_key_ani"
    FRAME_DELAY = 10
    
    
ITEM_DICT = {"pancake" : Pancake, "barrel": Barrel, "shopkeeper": Shopkeeper, "key": Key}
ITEM_ANIMATIONS = dict([(i, Animation.from_dir(i.TEXTURE, (tile, tile), i.FRAME_DELAY)) for i in ITEM_DICT.values()])

sparkle = Animation.from_dir("Art/Cute_item_sparkel", (tile, tile), 5)



class Item_sprite(actor.Animation_sprite):
    size = (tile, tile)
    name = "item"

    def render(self, scene, framecount):
        scene.blit(SHADOW, (self.pos[0], self.pos[1] + 5))
        super().render(scene, framecount)
        sparkle.update(framecount)
        scene.blit(sparkle.texture, self.pos)
    
    def startup_process(self, extra):
        self.item = ITEM_DICT[extra]()
        print("created", self.item)
        self.anim = (self.item.TEXTURE, (actor.tile, actor.tile), self.item.FRAME_DELAY) 
        super().startup_process("")

    def step_on(self, player):
        player.get(self.item)
        self.kill(self.index)

actor.SPRITE_CLASSES.append(Item_sprite)
