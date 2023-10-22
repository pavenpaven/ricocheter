import src.actor as actor

class Item:
    TEXTURE = "pancake"
    FRAME_DELAY = 4

class Pancake(Item):
    TEXTURE = "Art/Cute_food_panke"
    FRAME_DELAY = 15


ITEM_DICT = {"pancake" : Pancake}

class Item_sprite(actor.Animation_sprite):
    name = "item"
    def startup_process(self, extra):
        self.item = ITEM_DICT[extra]
        print("created", self.item)
        self.anim = (self.item.TEXTURE, (actor.tile, actor.tile), self.item.FRAME_DELAY) 
        super().startup_process("")

    def step_on(self, player):
        player.get(self)

actor.SPRITE_CLASSES.append(Item_sprite)
