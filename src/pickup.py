import pygame
from src.animation import Animation
import src.actor as actor
from src.actor import tile
import src.physics as physics

def scaler_mul(n, v): return (n*v[0], n*v[1])


SHADOW = pygame.image.load("Art/shadow_test.png")
SHADOW = pygame.transform.scale(SHADOW, (tile, tile))

class Item:
    TEXTURE = "pancake"
    FRAME_DELAY = 4
    PERMANENT = True
    SPARKLE = True
    SHADOW = True
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
        player.physics.dry_friction *= 1.8
        player.physics.drag *= 1.8

class Key(Item):
    TEXTURE = "Art/Cute_key_ani"
    FRAME_DELAY = 10

class Money(Item):
    TEXTURE = "Art/Cute_money_money_money"
    FRAME_DELAY = 10
    PERMANENT = False
    SPARKLE = False
    SHADOW = False

    def on_pickup(self, player) -> None:
        player.money += 1
    
ITEM_DICT = {"pancake" : Pancake, "barrel": Barrel, "shopkeeper": Shopkeeper, "key": Key, "money": Money}
ITEM_ANIMATIONS = dict([(i, Animation.from_dir(i.TEXTURE, (tile, tile), i.FRAME_DELAY)) for i in ITEM_DICT.values()])

sparkle = Animation.from_dir("Art/Cute_item_sparkel", (tile, tile), 5)



class Item_sprite(actor.Animation_sprite):
    size = (tile, tile)
    name = "item"

    def render(self, scene, framecount):
        if self.item.SHADOW:
            scene.blit(SHADOW, (self.pos[0], self.pos[1] + 5))

        super().render(scene, framecount)

        if self.item.SPARKLE:
            sparkle.update(framecount)
            scene.blit(sparkle.texture, self.pos)
    
    def startup_process(self, extra):
        self.item = ITEM_DICT[extra]()
        self.anim = (self.item.TEXTURE, self.size, self.item.FRAME_DELAY) 
        super().startup_process("")

    def step_on(self, player):
        player.get(self.item)
        self.kill(self.index)

class Moving_item(Item_sprite):
    size = scaler_mul(0.75, (tile,tile)) # wtf
    name = "money"

    def startup_process(self, extra):
        self.physics = physics.Physics_object(pygame.Rect(self.pos, self.size),
                                              (float(extra.split(",")[0]),
                                               float(extra.split(",")[1])),
                                              dry_friction = 0.15,
                                              drag = 0.02)
        super().startup_process(extra.split(",")[2])
    
    def step(self, scene, player):
        self.physics.update(scene)
        self.pos = self.physics.rect.topleft
        
actor.SPRITE_CLASSES + [Item_sprite, Moving_item]
