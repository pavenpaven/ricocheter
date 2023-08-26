import pygame
from typing import Callable
import math
from math import floor
import operator
from functools import reduce
from itertools import product

from src.create_map import rotate
import src.world as world
from src.world import tile
from src.tile_types import Tile_type
import src.tile_types as tile_types

BOOSTER_ACCEL = 1
TURN_BOOST = 0.1

Vec = tuple[float, ...]
Vec2 = tuple[float, float]

NOCLIP = [0]


def vec_invert(x: Vec) -> Vec: 
        return tuple(map(lambda v:-v, x))

def vec_add(x:Vec, y:Vec) -> Vec: 
        return tuple(map(lambda v:v[0]+v[1], zip(x,y)))

def scaler_vec_mul(s: float, v:Vec) -> Vec: 
        return tuple(map(lambda x:s*x, v)) # is this disgusting

def dot_product(v: Vec, u: Vec) -> float:
    return sum(map(operator.mul, v, u))

class Physics_object:
    def __init__(self, rect: pygame.Rect, velocity: Vec2, max_speed = 15, on_bounds: Callable[[], None] = lambda :None):
        self.velocity = velocity
        self.rect = rect
        self.max_speed = max_speed
        self.on_bounds = on_bounds
    
    def accelerate(self, accel_vec: Vec2) -> None:
        #self.velocity = vec_add(self.velocity, 
         #                       scaler_vec_mul(-TURN_BOOST*dot_product(self.velocity, accel_vec)+1, accel_vec))

        self.velocity = vec_add(self.velocity, accel_vec)

        speed = math.sqrt((self.velocity[0]**2) + (self.velocity[1]**2)) 
        if  speed > self.max_speed:
            self.velocity = scaler_vec_mul(self.max_speed/speed, self.velocity)


    def update(self, scene: world.Map) -> None:           
        travel_pos = vec_add((self.rect.x, self.rect.y), self.velocity)
        
        hitbox_x = pygame.Rect((travel_pos[0], self.rect.y), self.rect.size)
        hitbox_y = pygame.Rect((self.rect.x, travel_pos[1]), self.rect.size)
        if not NOCLIP[0]: 
            can_go_x, booster_vec = check_collision(hitbox_x, scene)
            can_go_y, _ =           check_collision(hitbox_y, scene)
        else:
            booster_vec = (0,0)
            can_go_x = True
            can_go_y = True
        
        self.accelerate(booster_vec)

        if can_go_x:
            self.rect.x = travel_pos[0]
        else:
            self.velocity = (-self.velocity[0], self.velocity[1])
            self.on_bounds()
        
        if can_go_y:
            self.rect.y =  travel_pos[1]
        else:
            self.velocity = (self.velocity[0], -self.velocity[1])
            self.on_bounds()


def check_collision(hitbox: pygame.Rect, scene: world.Map) -> tuple[bool, Vec2]:
    tiles = get_touching_tiles(hitbox, scene)
        
    can_go = not reduce(operator.__or__, [i.collision for i in tiles], False)
    booster_vec = reduce(vec_add, 
                         [rotate("cCbB".index(i.letter), (0, -1*BOOSTER_ACCEL)) 
                          for i in tiles if i.letter in "cCbB"],
                         (0,0))

    for i in scene.actors:
      if i.collision:  
        if hitbox.colliderect(pygame.Rect(i.pos,i.size)):
          can_go = False
      else:
        if hitbox.colliderect(pygame.Rect(i.pos,i.size)):
            i.step_on()

    return can_go, booster_vec
 

def get_touching_tiles(rect: pygame.Rect, scene: world.Map) -> list[Tile_type]: # check that inbounds before use 
    return [tile_types.Tile_type.types[scene.tiles[j][i]] for i,j in 
            product(range(floor(rect.x/tile), floor((rect.x + rect.width)/tile) + 1), 
                    range(floor(rect.y/tile), floor((rect.y + rect.height)/tile) + 1))
            if 0 <= i <= 15 and 0 <= j <= 15]
