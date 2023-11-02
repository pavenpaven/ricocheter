import pygame
import math
import src.world as world
import src.tile_types as tile_types
import src.actor as actor
import src.animation as ani
from src.physics import vec_add, scaler_vec_mul, vec_invert, magnitude, normalize
import src.physics as physics
import src.bullet as bullet
import src.pickup as pickup

tile = world.tile

c = lambda f,x:lambda :f(x)

ANIMATION_DELAY = 7
TURNING_SPEED = 0.2
ACCELERATION_SPEED = 0.60
BREAK_DIVISION = 1.04
MAX_SPEED = 15
BOUNDS_SLOWDOWN = 0.8
DRY_FRICTION = 0.1
DRAG = 0.02
MAX_HEALTH = 10
SHOOT_COOLDOWN = 15


blank = pygame.image.load("Art/unknown.png")
blank = pygame.transform.scale(blank, (0,0))

class Ship:
  def __init__(self, pos, filename, proporsion, speed):
    self.rect = pygame.Rect(pos, proporsion)
    self.speed = speed
    self.animation = ani.Animation.from_dir(filename, self.rect.size, ANIMATION_DELAY)
    def f(self): self.velocity = scaler_vec_mul(BOUNDS_SLOWDOWN, self.velocity)
    self.physics = physics.Physics_object(self.rect.copy(), (0, 0), max_speed = MAX_SPEED, on_bounds = f, dry_friction = DRY_FRICTION, drag = DRAG)
    self.angle = 0
    self.items = []
    self.lives = MAX_HEALTH
    self.accel = ACCELERATION_SPEED
    self.last_hit = 0
    self.max_health = MAX_HEALTH
    self.max_speed = MAX_SPEED
    self.shoot_on_cooldown = 0
    self.shoot_cooldown = SHOOT_COOLDOWN
    
  def render(self, framecount):
    self.animation.update(framecount)
    image = pygame.transform.rotate(self.animation.texture, math.degrees(self.angle)) # very stupid
    self.rect = image.get_rect(center = self.physics.rect.center)
    if self.last_hit + 30 <= framecount or math.floor(framecount/3) % 2:
      return image
    else:
      return blank

      
        
  def walk(self, input_vector, scene, move_vector, music): #input_vector is like (Forward, Right/Left, Break, Shoot) wtf
    self.shoot_on_cooldown = max(self.shoot_on_cooldown-1, 0)
    if input_vector[3]:
        self.shoot(scene)
    #accel_vector = scaler_vec_mul(input_vector[0]*ACCELERATION_SPEED, (-math.sin(self.angle), -math.cos(self.angle))) #down is positive y
    accel_vector = scaler_vec_mul(self.accel, move_vector) #down is positive y
    self.physics.accelerate(accel_vector)
    

    self.physics.velocity = scaler_vec_mul(1/ (1 + (BREAK_DIVISION - 1)*input_vector[2]), self.physics.velocity) #magi
    #self.angle += input_vector[1]*TURNING_SPEED
    if move_vector[0] or move_vector[1]:
      if move_vector[1]:
        if move_vector[1]>0:
          self.angle = math.pi + math.atan(move_vector[0]/move_vector[1])
        else:
          self.angle = math.atan(move_vector[0]/move_vector[1])
      else:
        self.angle = math.pi + (move_vector[0]*math.pi/2)
      
    self.physics.update(scene)

    
  def shoot(self, scene):
    if not self.shoot_on_cooldown:
      self.shoot_on_cooldown = self.shoot_cooldown
      bull = bullet.Bullet((self.rect.center), "trolololololololo", scene.kill_actor)
      bull.physics.velocity = scaler_vec_mul(40, (-math.sin(self.angle), -math.cos(self.angle)))
      scene.actors[scene.segname].append(bull)

  def hit(self, actor, framecount):
    if framecount - self.last_hit > 30:
      self.last_hit = framecount
      self.lives += -1


class Player(Ship):
  money = 0 # wtf
  def use_button(self, actors: list[actor.Sprite]): #or inherited from Sprite
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
    
  def walk(self, input_vector, scene, move_vector, music):
    self.check_loading_zone(self.physics.rect, scene, music) #wierd coordinate asyemtry
    super().walk(input_vector, scene, move_vector, music)
  
  def check_loading_zone(self, player_hitbox, scene, music):
      x = player_hitbox.collidelistall(list(map(lambda x: x.rect, scene.loading_zone)))
      if x:
        x=x[0] #yes
        lz = scene.loading_zone[x]
        scene.load_room("Level/gamefile", lz.segname, music)
        (self.physics.rect.x, self.physics.rect.y) = lz.spawn_pos

  def get(self, item: pickup.Item):
    item.on_pickup(self)
    if item.PERMANENT:
      self.items.append(item)
















