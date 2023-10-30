from src.animation import Animation
import src.actor as actor
from src.actor import tile

class Item:
    TEXTURE = "pancake"
    FRAME_DELAY = 4
    def on_pickup(self, player) -> None:# no type lol
        print(self.__class__)
    
    
class Pancake(Item):
    TEXTURE = "Art/Cute_food_panke_beter"
    FRAME_DELAY = 15

class Barrel (Item):
    TEXTURE = "Art/Cute_item_barrel"
    FRAME_DELAY = 4

class Shopkeeper(Item):
    TEXTURE = "Art/Cute_npc_vampir_ani"
    FRAME_DELAY = 4

    
ITEM_DICT = {"pancake" : Pancake, "barrel": Barrel, "shopkeeper": Shopkeeper}
ITEM_ANIMATIONS = dict([(i, Animation.from_dir(i.TEXTURE, (tile, tile), i.FRAME_DELAY)) for i in ITEM_DICT.values()])

class Item_sprite(actor.Animation_sprite):
    name = "item"
    def startup_process(self, extra):
        self.item = ITEM_DICT[extra]()
        print("created", self.item)
        self.anim = (self.item.TEXTURE, (actor.tile, actor.tile), self.item.FRAME_DELAY) 
        super().startup_process("")

    def step_on(self, player):
        player.get(self.item)
        self.kill(self.index)

actor.SPRITE_CLASSES.append(Item_sprite)
