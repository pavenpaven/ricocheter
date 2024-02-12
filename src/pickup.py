import pygame
from src.animation import Animation
import src.actor as actor
from src.actor import tile
from src.physics import vec_add
import src.physics as physics
from src.fps import FONT


def scaler_mul(n, v): return (n*v[0], n*v[1])


SHADOW = pygame.image.load("Art/shadow_test.png")
SHADOW = pygame.transform.scale(SHADOW, (tile, tile))

class Item:
    TEXTURE = "pancake"
    FRAME_DELAY = 4
    PERMANENT = True
    SPARKLE = True
    SHADOW = True
    PRICE = 0
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
    TEXTURE = "Art/Cute_dash"
    FRAME_DELAY = 8
    PRICE = 20
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


def gen_price_tag(price : int) -> pygame.Surface:
    return FONT.render(str(price), True, (255, 255, 255))


class Item_sprite(actor.Animation_sprite):
    size = (tile, tile)
    name = "item"

    def render(self, scene, framecount):
        if self.item.SHADOW:
            scene.blit(SHADOW, (self.pos[0], self.pos[1] + 5))

        if self.item.PRICE != 0:
            scene.blit(self.price_tag, vec_add(self.pos, (0, -30)))
            
        super().render(scene, framecount)

        if self.item.SPARKLE:
            sparkle.update(framecount)
            scene.blit(sparkle.texture, self.pos)
    
    def startup_process(self, extra):
        self.item = ITEM_DICT[extra]()
        self.anim = (self.item.TEXTURE, self.size, self.item.FRAME_DELAY)
        self.price_tag = gen_price_tag(self.item.PRICE)
        self.partner = None # partner is removed at the same time so its pretty much for reward room
        super().startup_process("")

    def step_on(self, player):
        if player.money >= self.item.PRICE:
            player.money -= self.item.PRICE
            player.get(self.item)
            self.kill(self.index)
            if self.partner:
                self.kill(self.partner)

    def bind(self, partner):
        self.partner = partner
        partner.partner = self

class Moving_item(Item_sprite):
    size = (26, 26) # wtf
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
