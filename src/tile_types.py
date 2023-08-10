import pygame
import os
import math

tile=38

comp = lambda f,g:lambda *x:f(g(*x))

def no_stepfunc():
    pass

def rotate_tile():
    pass

class Tile_type:
    types_length=0
    types=[]
    def __init__(self, texture_filename, collision, letter, key = None, rotate=0, flipx=False, flipy=False, animation=False, frame_delay = 1, stepfunc=no_stepfunc):
        self.index = __class__.types_length
        __class__.types_length += 1
        
        self.key = key
        self.collision = collision
        self.letter = letter 
        self.stepfunc = stepfunc
        __class__.types.append(self)
        
        if not animation:
            self.animation = False
            untransformed_texture = pygame.image.load(texture_filename)
            self.texture = pygame.transform.scale(untransformed_texture, (tile, tile))
            self.texture = pygame.transform.rotate(self.texture, 90 * rotate)
        

            if flipx or flipy:
                self.letter = "1" + letter
                self.texture = pygame.transform.flip(self.texture ,flipx , flipy)
                Tile_type(texture_filename, collision, letter)

            if rotate != 0:
                self.letter = str(rotate)+ letter
                Tile_type(texture_filename, collision, letter, rotate = rotate -1)
        else:
            self.animation = True
            self.frame_delay = frame_delay
            self.frames = list(map(comp(pygame.image.load, lambda x:f"{texture_filename}/{x}"), sorted(os.listdir(texture_filename), key=lambda x:int(x.replace(".png", "").split("-")[2])))) #normal magic
            self.frames = list(map(lambda x:pygame.transform.scale(x, (tile, tile)), self.frames))
            self.texture = self.frames[0]
    
    def update(self, framecount):
        if self.animation:
            self.texture = self.frames[math.floor(framecount/self.frame_delay) % len(self.frames)]



    def find(letter):
        for i in __class__.types:
            if i.letter == letter:
                return i
        print(letter)
        k # letter not found
    def find_letter(index):
        return __class__.types[index].letter

Tile_type("Art/unknown.png", True, "u", key=pygame.K_u)
jack_type = Tile_type("Art/jack.png", True, "j", rotate=3)
Tile_type("Art/Cute_plate.png", False, "a", key=pygame.K_c)
Tile_type("Art/Cute_ani_3", False, "A", animation=True, frame_delay = 8, key=pygame.K_v)
Tile_type("Art/Empty_space.png", False, "L", key=pygame.K_b)
Tile_type("Art/Cute_wall_bubble_ani", True, "l", animation=True, frame_delay = 6, key=pygame.K_f)
Tile_type("Art/Cute_text_room_boss", False, "U", animation=True, frame_delay= 7)
Tile_type("Art/Cute_boost_arow_north", False, "c", animation=True, frame_delay=2)
Tile_type("Art/Cute_boost_arow_east", False, "C", animation=True, frame_delay=2)
Tile_type("Art/Cute_boost_arow_south", False, "b", animation=True, frame_delay=2)
Tile_type("Art/Cute_boost_arow_west", False, "B", animation=True, frame_delay=2)
Tile_type('Art/Cute_death_ani', False, 'o', animation=True, frame_delay=6)