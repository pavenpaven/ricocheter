import pygame
import math
import src.world as world
import src.tile_types as tile_types
import src.actor as actor
import src.animation as ani

tile = world.tile

ANIMATION_DELAY = 7
TURNING_SPEED = 0.2
ACCELERATION_SPEED = 0.25
BREAK_DIVISION = 1.02

NOCLIP = [0]

vec_invert = lambda x: tuple(map(lambda v:-v, x))
vec_add = lambda x, y:tuple(map(lambda v:v[0]+v[1], zip(x,y)))
scaler_vec_mul = lambda s,v:tuple(map(lambda x:s*x, v))

class Player:
  def __init__(self, pos, filename, proporsion, speed):
    self.rect = pygame.Rect(pos, proporsion)
    self.speed = speed
    self.animation = ani.Animation(filename, self.rect.size, ANIMATION_DELAY)
    self.velocity = (0,0)
    self.angle = 0

  def render(self, framecount):
    self.animation.update(framecount)
    image = pygame.transform.rotate(self.animation.texture, math.degrees(self.angle)) # very stupid
    self.rect = image.get_rect(center=self.rect.center)
    return image

  def use_button(self, actors: [actor.Sprite]): #or inherited from Sprite
    actors = list(filter(lambda x:x.interactable, actors))
    
    actors_in_range = list(
      map(
        lambda x: (x, math.sqrt((((self.rect.x, self.rect.y)[0]-x.pos[0])**2)+((self.rect.x, self.rect.y)[1]-x.pos[1])**2)), actors
      )
    ) #lol creats a list of touples were actors in the scene isn index 0 and distance is index 1

    actors_in_range = list(filter(lambda x: x[1]<tile*1.5, actors_in_range))
    if not actors_in_range:
      return 0
    actors_in_range.sort(key=(lambda x: x[1]))
    actors_in_range[0][0].player_action()
    return 1
    
    
  
  def check_loading_zone(self, player_hitbox, scene, music):
      x = player_hitbox.collidelistall(list(map(lambda x: x.rect, scene.loading_zone)))
      if x:
        x=x[0] #yes
        lz = scene.loading_zone[x]
        scene.load_room("Level/tile_map", lz.segname, music)
        (self.rect.x, self.rect.y) = lz.spawn_pos
        
  def walk(self, input_vector, scene, music): #input_vector is like (Forward, Right/Left, Break) wtf
    accel_vector = scaler_vec_mul(input_vector[0]*ACCELERATION_SPEED, (-math.sin(self.angle), -math.cos(self.angle))) #down is positive y
    self.velocity = vec_add(self.velocity, accel_vector)
    travel_pos = vec_add((self.rect.x, self.rect.y), self.velocity)
    
    self.velocity = scaler_vec_mul(1/ (1 + (BREAK_DIVISION - 1)*input_vector[2]), self.velocity) #magi
    self.angle += input_vector[1]*TURNING_SPEED

    player_hitbox_x = ((travel_pos[0], self.rect.y), (travel_pos[0] + self.rect.size[0], self.rect.y + self.rect.height )) #FIXME
    player_hitbox_y = ((self.rect.x, travel_pos[1]), (self.rect.x + self.rect.size[0], travel_pos[1] + self.rect.height))
    if not NOCLIP[0]: 
        can_go_x=check_collision(player_hitbox_x,scene, (pygame.Rect(player_hitbox_x[0], (self.rect.size[0], self.rect.size[1]/3))))
        can_go_y=check_collision(player_hitbox_y,scene, (pygame.Rect(player_hitbox_y[0], (self.rect.size[0], self.rect.size[1]/3))))
    else:
        can_go_x = True
        can_go_y = True

    if can_go_x:
        self.rect.x = travel_pos[0]
    else:
        self.velocity = (-self.velocity[0], self.velocity[1])
    
    if can_go_y:
        self.rect.y =  travel_pos[1]
    else:
        self.velocity = (self.velocity[0], -self.velocity[1])
    

    self.check_loading_zone(pygame.Rect(player_hitbox_x[0], (self.rect.size[0], self.rect.size[1]/3)), scene, music) #wierd coordinate asyemtry


def check_collision(player_hitbox, scene, player_rect):
    tiles = get_touching_tiles(player_hitbox, scene)
    can_go = True
    for i in tiles:
        if tile_types.Tile_type.types[scene.tiles[i[1]][i[0]]].collision:
            can_go = False

    for i in scene.actors:
      if i.collision:  
        if player_rect.colliderect(pygame.Rect(i.pos,i.size)):
          can_go = False
      else:
        if player_rect.colliderect(pygame.Rect(i.pos,i.size)):
            i.step_on()
        
    return can_go
  


def get_touching_tiles(rect, sce): #sce for scene idk why
    out = []
    points = [rect[0], rect[1], (rect[0][0], rect[1][1]), (rect[1][0], rect[0][1])]
    for i in points:
        out.append((math.trunc(i[0]/tile), math.trunc(i[1]/tile)))
    return out
