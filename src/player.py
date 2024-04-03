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
import random


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
VEL_SCALER = 0.8
MAX_HEALTH = 10
SHOOT_COOLDOWN = 15
MINIGUN_ANGLE_SHIFT = 2*math.pi/30
MINIGUN_VARIATION = 0.1


blank = pygame.image.load("Art/unknown.png")
blank = pygame.transform.scale(blank, (0,0))

SMOKE_1 = pygame.image.load("Art/smoke_1.png")
SMOKE_1 = ani.Animation([SMOKE_1], (tile, tile), 1)
SMOKE_2 = ani.Animation.from_dir("Art/Cute_smoke_1_ani", (tile*0.8, tile*0.8), 3)
SMOKE_3 = ani.Animation.from_dir("Art/Cute_smoke_2_ani", (tile*0.8, tile*0.8), 3)
SMOKE_4 = ani.Animation.from_dir("Art/Cute_smoke_3_ani", (tile*0.8, tile*0.8), 3)

SHOOT_SOUND = pygame.mixer.Sound("Sound/sfx_shot_player.wav")
SHOOT_SOUND.set_volume(0.5)

RELOAD_SOUND = pygame.mixer.Sound("Sound/reload.wav")
RELOAD_SOUND.set_volume(0.5)

class Smoke(actor.Sprite):
  size = (tile*0.8, tile*0.8)
  
  def startup_process(self, extra):
    ex = extra.split(",")
    self.physics = physics.Physics_object(pygame.Rect(self.pos, self.size), (float(ex[0]), float(ex[1])), dry_friction = 0.1, drag = 0.02)
    self.age = 0
    self.life = random.randint(10, 15)
    self.tex = random.choice([SMOKE_1, SMOKE_3, SMOKE_4])

  def step(self, scene, player):
    self.physics.update(scene)
    self.pos = self.physics.rect.topleft
    self.age += 1
    if self.age >= self.life:
      self.kill(self.index)

  def render(self, scene, framecount):
    if self.age >= 10:
      SMOKE_2.update(framecount)
      scene.blit(SMOKE_2.texture, self.pos)
    else:
      self.tex.update(framecount)
      scene.blit(self.tex.texture, self.pos)
    

class Counter:
  def __init__(self):
    self.value = 0

  def tick(self):
    self.value += 1

  def reset(self):
    self.value = 0


class Ship:
  def __init__(self, pos, filename, proporsion, speed):
    self.rect = pygame.Rect(pos, proporsion)
    self.speed = speed
    self.animation = ani.Animation.from_dir(filename, self.rect.size, ANIMATION_DELAY)
    self.physics = physics.Physics_object(self.rect.copy(), (0, 0), max_speed = MAX_SPEED, on_bounds = self.f, dry_friction = DRY_FRICTION, drag = DRAG, velocity_scaler = VEL_SCALER)
    self.angle = 0
    self.items = [pickup.Dash()] #not cursed that enemies have dash item maybe i should make them drop items
    self.lives = MAX_HEALTH
    self.accel = ACCELERATION_SPEED
    self.last_hit = 0
    self.max_health = MAX_HEALTH
    self.max_speed = MAX_SPEED
    self.shoot_on_cooldown = 0
    self.shoot_cooldown = SHOOT_COOLDOWN
    self.magazine_size = 4
    self.magazine = self.magazine_size
    self.reloading = 0
    self.reloading_speed = 15
    self.open_door = False
    self.is_breaking = False
    self.using_shotgun = False
    self.using_sniper = False
    self.bullet_bounds = 2
    self.consecutive_hit_counter = Counter()


    
  def f(self, phys):
    if self.is_breaking:
      phys.velocity = scaler_vec_mul(BOUNDS_SLOWDOWN*0.3, phys.velocity)
    else:
      self.velocity = scaler_vec_mul(BOUNDS_SLOWDOWN, phys.velocity)
    
  def render(self, framecount):
    self.animation.update(framecount)
    image = pygame.transform.rotate(self.animation.texture, math.degrees(self.angle)) # very stupid
    self.rect = image.get_rect(center = self.physics.rect.center)
    if self.last_hit + 30 <= framecount or math.floor(framecount/3) % 2:
      return image
    else:
      return blank

      
        
  def walk(self, input_vector, scene, move_vector, music): #input_vector is like (Forward, Right/Left, Break, Shoot, Reload) wtf
    self.shoot_on_cooldown = max(self.shoot_on_cooldown-1, 0)
    if input_vector[3]:
        self.shoot(scene)
    #accel_vector = scaler_vec_mul(input_vector[0]*ACCELERATION_SPEED, (-math.sin(self.angle), -math.cos(self.angle))) #down is positive y
    accel_vector = scaler_vec_mul(self.accel, move_vector) #down is positive y
    self.physics.accelerate(accel_vector)

    if (self.magazine <= 0 or input_vector[4]) and (self.reloading <= 0):
      self.reloading = self.reloading_speed + 1
     
    if self.reloading == 1:
      if self.magazine < self.magazine_size:
        self.magazine += 1
        self.reloading = self.reloading_speed + 1
      else:
        RELOAD_SOUND.play()        
      
    if self.reloading > 0:
      self.reloading -= 1

      
    self.is_breaking = input_vector[2]
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

    

    if self.physics.last_hit_tile:
      if self.physics.last_hit_tile.letter == "U": # U is letter for bossdoor
        if list(filter(lambda x: isinstance(x, pickup.Key), self.items)):
          self.open_door = True
    
  def shoot(self, scene):
    if not self.shoot_on_cooldown and self.reloading <= 0 and self.magazine > 0:
      self.magazine -= 1
      self.shoot_on_cooldown = self.shoot_cooldown
      if not self.using_shotgun:
        bull = bullet.Bullet((self.rect.center), "", scene.kill_actor)
        bull.COUNTER = self.consecutive_hit_counter
        bull.MAX_BOUNDS = self.bullet_bounds
        bull.DAMAGE = 1 + self.using_sniper * (self.consecutive_hit_counter.value > 2)
        bull.physics.velocity = scaler_vec_mul(40, (-math.sin(self.angle), -math.cos(self.angle)))
        scene.actors[scene.segname].append(bull)
      else:
        bull1 = bullet.Bullet((self.rect.center), "", scene.kill_actor)
        bull1.MAX_BOUNDS = self.bullet_bounds
        bull1.DAMAGE = 1 + self.using_sniper * (self.consecutive_hit_counter.value > 2)
        r = random.random()*MINIGUN_VARIATION - (MINIGUN_VARIATION/2)
        bull1.physics.velocity = scaler_vec_mul(40, (-math.sin(self.angle + MINIGUN_ANGLE_SHIFT + r), -math.cos(self.angle + MINIGUN_ANGLE_SHIFT + r)))        
        scene.actors[scene.segname].append(bull1)
        r = random.random()*MINIGUN_VARIATION - (MINIGUN_VARIATION/2)
        bull2 = bullet.Bullet((self.rect.center), "", scene.kill_actor)
        bull2.MAX_BOUNDS = self.bullet_bounds
        bull2.DAMAGE = 1 + self.using_sniper * (self.consecutive_hit_counter.value > 2)
        bull2.physics.velocity = scaler_vec_mul(40, (-math.sin(self.angle - MINIGUN_ANGLE_SHIFT + r), -math.cos(self.angle - MINIGUN_ANGLE_SHIFT + r)))
        scene.actors[scene.segname].append(bull2)
      SHOOT_SOUND.play()

  def hit(self, actor, framecount):
    if framecount - self.last_hit > 30:
      self.last_hit = framecount
      self.lives += -1

MAX_DASH_SPEED = 5
dash_accel = 3
      
class Player(Ship):
  money = 0 # wtf
  dash = 0
  dash_cooldown = 0
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
    if not (scene.framecount % 1) and (move_vector[0] or move_vector[1]):
      ang = self.angle + math.pi + (math.pi*(random.random() - (0.5))/4)
      offset = (-math.sin(ang)*20, -math.cos(ang)*20)
      vel = scaler_vec_mul(random.randint(3,5), (-math.sin(ang), -math.cos(ang)))
      #scene.actors[scene.segname].insert(0, Smoke(vec_add(offset, self.rect.topleft), scene.change_state, scene.kill_actor, f"{vel[0]},{vel[1]}"))
    for i in range(5):
      if input_vector[5+i]:
        if len(self.items) > i:
          self.items[i].active(self) 
    if self.dash:
     # self.physics.accelerate(scaler_vec_mul(dash_accel*(1 - magnitude(self.physics.velocity) / MAX_DASH_SPEED), (-math.sin(self.angle), -math.cos(self.angle))))
      self.physics.accelerate(scaler_vec_mul(dash_accel, (-math.sin(self.angle), -math.cos(self.angle))))
      self.dash -=1
    for i in self.items:
      i.update()
    
    super().walk(input_vector, scene, move_vector, music)
  
  def check_loading_zone(self, player_hitbox, scene, music):
      x = player_hitbox.collidelistall(list(map(lambda x: x.rect, scene.loading_zone)))
      if x:
        x=x[0] #yes
        lz = scene.loading_zone[x]
        scene.load_room("Level/gamefile", lz.segname, music)
        (self.physics.rect.x, self.physics.rect.y) = lz.spawn_pos

  def get(self, item: pickup.Item):
    item.SOUND.play()
    item.on_pickup(self)
    if item.PERMANENT:
      self.items.append(item)
