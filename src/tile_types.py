import pygame
import os
import math
from src.animation import Animation

tile=38

comp = lambda f,g:lambda *x:f(g(*x))

def no_stepfunc():
    pass

def rotate_tile():
    pass

class Tile_type:
    types_length=0
    types=[]
    def __init__(self, texture_filename: str, collision, letter, key = None, rotate=0, flipx=False, flipy=False, animation=False, frame_delay = 1, stepfunc=no_stepfunc, parent = None):
        self.index = __class__.types_length
        __class__.types_length += 1
        
        self.key = key
        self.collision = collision
        self.letter = letter 
        self.stepfunc = stepfunc
        self.parent = parent
        self.animation = animation
        __class__.types.append(self)
        

        if not animation:
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
            self.ani = Animation.from_dir(texture_filename, (tile, tile), frame_delay) 
    
    def update(self, framecount):
        if self.animation:
            self.ani.update(framecount)
            self.texture = self.ani.texture
    
    def children(self):
        return [i for i in [j for j in __class__.types if j.parent] if i.parent.index == self.index]

    def parent(self):
        return self.parent


    def find(letter):
        for i in __class__.types:
            if i.letter == letter:
                return i
        print(letter)
        k # letter not found
    def find_letter(index):
        return __class__.types[index].letter

def get_ordered_family(tile_type: Tile_type, caller: Tile_type | None) -> list[Tile_type]: #asume no recursive family
    child = tile_type.children()
    if child:
        child = child[0]
    else:
        child = None

    parent = tile_type.parent
    child_path = []
    if child:
        if child.index != caller.index:
            child_path = get_ordered_family(child, tile_type)
    
    parent_path = []
    if parent:
        if parent.index != caller.index:
            parent_path = get_ordered_family(parent, tile_type) 

    return parent_path + [tile_type] + child_path



Tile_type("Art/unknown.png", True, "u", key=pygame.K_u)
jack_type = Tile_type("Art/jack.png", True, "j", rotate=3)
Tile_type("Art/Cute_plate.png", False, "a", key=pygame.K_c)
Tile_type("Art/Cute_ani_3", False, "A", animation=True, frame_delay = 8, key=pygame.K_v)
Tile_type("Art/Empty_space.png", False, "L", key=pygame.K_b)
Tile_type("Art/Cute_wall_bubble_ani", True, "l", animation=True, frame_delay = 6, key=pygame.K_f)
Tile_type("Art/Cute_wall_bubble_2", True, "x", animation=True, frame_delay = 6, key=pygame.K_f)
Tile_type("Art/Cute_text_room_boss", True, "U", animation=True, frame_delay= 7)
t = Tile_type("Art/Cute_boost_arow_north", False, "c", animation=True, frame_delay=2, key = pygame.K_h, parent = None)
t = Tile_type("Art/Cute_boost_arow_east", False, "C", animation=True, frame_delay=2, parent = t )
t = Tile_type("Art/Cute_boost_arow_south", False, "b", animation=True, frame_delay=2, parent = t)
Tile_type("Art/Cute_boost_arow_west", False, "B", animation=True, frame_delay=2, parent = t)
Tile_type('Art/Cute_death_ani', False, 'o', animation=True, frame_delay=6)
Tile_type('Art/Cute_plate_yellow.png', False, 'O', key=pygame.K_g)
Tile_type('Art/Cute_plate_blue.png', False, 'd')
Tile_type('Art/Cute_plate_magenta.png', False, 'D')
Tile_type('Art/Cute_plate_orange.png', False, 'e')
Tile_type('Art/Cute_plate_red.png', False, 'E', )
Tile_type("Art/Cute_plate_green.png", False, 'f')
Tile_type("Art/Cute_plate_pride.png", False, 'F')
