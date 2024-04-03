from __future__ import annotations
import pygame
from typing import Callable
import math
from math import floor
import operator
from functools import reduce
from itertools import product, chain


import src.world as world
from src.tile_types import Tile_type
import src.tile_types as tile_types

tile = 38 #sadlife dude like cyklic dependensies are cursed

BOOSTER_ACCEL = 1
TURN_BOOST = 0.1

Vec = tuple[float, ...]
Vec2 = tuple[float, float]

NOCLIP = [0]

rotate90 = lambda x: (-x[1], x[0])
def rotate(n:int, x:tuple[int, int]) -> tuple[int, int]:
    if n:
        return rotate(n-1, rotate90(x))
    else:
        return x

def vec_invert(x: Vec) -> Vec: 
        return tuple(map(lambda v:-v, x))

def vec_add(x:Vec, y:Vec) -> Vec: 
        return tuple(map(lambda v:v[0]+v[1], zip(x,y)))

def scaler_vec_mul(s: float, v:Vec) -> Vec: 
        return tuple(map(lambda x:s*x, v)) # is this disgusting

def dot_product(v: Vec, u: Vec) -> float:
    return sum(map(operator.mul, v, u))

def magnitude(v: Vec) -> float:
    return math.sqrt(sum(map(lambda x:x**2, v)))

def normalize(v: Vec) -> Vec:
    return scaler_vec_mul(1/magnitude(v), v)

def reduce_magnitude(x: int, y: Vec) -> Vec:
    pass

class Physics_object:
    def __init__(self, rect: pygame.Rect, velocity: Vec2, max_speed = 15, on_bounds: Callable[[Physics_object], None] = lambda x:None, dry_friction = 0, drag = 0, velocity_scaler = 1):
        self.velocity = velocity
        self.rect = rect
        self.max_speed = max_speed
        self.on_bounds = on_bounds
        self.dry_friction = dry_friction
        self.drag = drag
        self.last_hit_tile = None
        self.velocity_scaler = velocity_scaler
        
    def accelerate(self, accel_vec: Vec2) -> None:
        #self.velocity = vec_add(self.velocity, 
         #                       scaler_vec_mul(-TURN_BOOST*dot_product(self.velocity, accel_vec)+1, accel_vec))

        self.velocity = vec_add(self.velocity, accel_vec)

        if  magnitude(self.velocity) > self.max_speed:
            self.velocity = scaler_vec_mul(self.max_speed, normalize(self.velocity))


    def update(self, scene: world.Map) -> None:           
        travel_pos = vec_add((self.rect.x, self.rect.y), scaler_vec_mul(self.velocity_scaler, self.velocity))

        hitbox_x = pygame.Rect((travel_pos[0], self.rect.y), self.rect.size)
        hitbox_y = pygame.Rect((self.rect.x, travel_pos[1]), self.rect.size)
        if not NOCLIP[0]: 
            can_go_x, booster_vec = check_collision(hitbox_x, scene)
            can_go_y, _ =           check_collision(hitbox_y, scene)
            if can_go_x:
                self.last_hit_tile = can_go_x[0]
                can_go_x = False                
            else:
                can_go_x = True
            if can_go_y:
                self.last_hit_tile = can_go_y[0]
                can_go_y = False
            else:
                can_go_y = True
        else:
            booster_vec = (0,0)
            can_go_x = True
            can_go_y = True
        
        self.accelerate(booster_vec)
        
        

        #if not check_collision(self.rect, scene)[0]:            
        #    can_go_x = True
        #    can_go_y = True
        
        if magnitude(self.velocity) != 0:
            friction = min((self.velocity, scaler_vec_mul(self.dry_friction + self.drag * magnitude(self.velocity), normalize(self.velocity))), key = magnitude)
            self.accelerate(vec_invert(friction))

        if can_go_x:
            self.rect.x = travel_pos[0]
        else:
            self.velocity = (-self.velocity[0], self.velocity[1])
            self.on_bounds(self)
        
        if can_go_y:
            self.rect.y =  travel_pos[1]
        else:
            self.velocity = (self.velocity[0], -self.velocity[1])
            self.on_bounds(self)


def check_collision(hitbox: pygame.Rect, scene: world.Map) -> tuple[bool, Vec2]:
    tiles = get_touching_tiles(hitbox, scene)
        
    can_go = not reduce(operator.__or__, [i.collision for i in tiles], False)
    booster_vec = reduce(vec_add, 
                         [rotate("cCbB".index(i.letter), (0, -1*BOOSTER_ACCEL)) 
                          for i in tiles if i.letter in "cCbB"],
                         (0,0))


    collisions = list(filter(lambda x: x.collision, tiles))

        
    
    
    for i in scene.loaded_actors:
      if i.collision:  
        if hitbox.colliderect(pygame.Rect(i.pos,i.size)):
          can_go = False

    return collisions, booster_vec
 

def get_touching_tiles(rect: pygame.Rect, scene: world.Map) -> list[Tile_type]: # check that inbounds before use 
    return [tile_types.Tile_type.types[scene.tiles[j][i]] for i,j in 
            product(range(floor(rect.x/tile), floor((rect.x + rect.width)/tile) + 1), 
                    range(floor(rect.y/tile), floor((rect.y + rect.height)/tile) + 1))
            if 0 <= i <= 15 and 0 <= j <= 15]
