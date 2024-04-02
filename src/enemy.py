import pygame
from src.actor import tile
import src.actor as actor
from src.physics import vec_add, vec_invert, normalize, scaler_vec_mul, magnitude
from src.player import Ship
from src.animation import Animation
from src.pickup import Moving_item
import src.conf as conf
import src.bullet as bullet
import random
from itertools import repeat


SPEED = 2.5

class Enemy (actor.Animation_sprite):
    anim = ("Art/Cute_npc_vampir_ani", (tile, tile), 4)
    size = (tile, tile)
    name = "enemy"
    IS_ENEMY = True
    LIVES = 1
    DIES_OF_BULLET = True
    DROPS_MONEY = True
    
    def startup_process(self, extra):
        self.lives = self.LIVES
        super().startup_process(extra)
        
    def step(self, scene, player):
        for i in scene.loaded_actors:
            if i.IS_BULLET and self.DIES_OF_BULLET:
                if self.rect.colliderect(i.rect):
                    self.lives -= 1
                    self.kill(i.index)
        if self.lives <= 0:
            self.kill(self.index)
            r = random.random
            for i in range(random.randint(1,3)):
                scene.actors[scene.segname].append(Moving_item(self.pos, self.change_state, self.kill, f"{14*r() - 7},{14*r()-7},money")) #14


SHADOW = pygame.image.load("Art/shadow_test.png")
SHADOW = pygame.transform.scale(SHADOW, (tile, tile))
            
class Ghost (Enemy):
    anim = ("Art/Cute_npc_vampir_ani", (tile, tile), 4)
    name = "ghost"
    DIES_OF_BULLET = False
    IS_GHOST = True
    DROPS_MONEY = False
    #IS_GLOBALLY_LOADED = True FIXME

    def startup_process(self, extra):
        self.animN = Animation.from_dir("Art/Cute_npc_ghost_up", (tile, tile), 15)
        self.animS = Animation.from_dir("Art/Cute_npc_ghost_down", (tile, tile), 15)
        self.animW = Animation.from_dir("Art/Cute_npc_ghost_right", (tile, tile), 15)
        self.animE = Animation.from_dir("Art/Cute_npc_ghost_left", (tile, tile), 15)
        
        super().startup_process(extra)
        
    def render(self, scene, framecount):
        scene.blit(SHADOW, vec_add(self.pos, (0,5)))
        super().render(scene, framecount)

    def step(self, scene, player):
        self.pos = vec_add(self.pos,
                           scaler_vec_mul(SPEED,
                           normalize(vec_add(vec_invert(self.pos),
                                    (player.rect.center)))))

        vec = normalize(vec_add(vec_invert(self.pos), (player.rect.center)))
        if abs(vec[0]) > abs(vec[1]):
            if vec[0] < 0:
                self.ani = self.animE
            else:
                self.ani = self.animW
        else:
            if vec[1] < 0:
                self.ani = self.animN
            else:
                self.ani = self.animS


        super().step(scene, player)


        
 
       
class Rammer (Enemy):
    name = "rammer"
    anim = ("Art/Cute_enemy_ram_2", (tile, tile), 10)
    LIVES = 3
    def startup_process(self, extra):
        self.ship = Ship(self.pos, self.anim[0], self.anim[1], 1) # speed is from jack and jackie
        self._is_initiated = False
        self.ship.accel = float(conf.conf_search("enemy_accel"))
        self.ship.physics.drag /= float(conf.conf_search("enemy_drag_scale"))
        super().startup_process(extra) 

    def render(self, scene, framecount):
        scene.blit(self.ship.render(framecount), self.pos)

    def step(self, scene, player):
        if not self._is_initiated:
            self._is_initiated = True
            self.ship.physics.rect.topleft = self.pos
        inpu = self.ai(scene, player)
        self.ship.walk(inpu[0], scene, inpu[1], "music") #FIXME this is why you dont pass music evevrywhere
        self.pos = self.ship.rect.topleft
        super().step(scene, player)

    def ai(self, scene, player) -> tuple[bool, ...]: #dunno the type
        if magnitude(vec_add(vec_invert(self.ship.rect.center), player.rect.center))==0:
            return ((0,0,0,0,0,0,0), (0,0))
        accel = normalize(vec_add(vec_invert(self.ship.rect.center),
                                  player.rect.center))
        
        return ((0,0,0,0,0,0,0,0,0), accel)



TURRET_BODY = pygame.image.load("Art/Cute_enemy_turret_body.png")
TURRET_BODY = pygame.transform.scale(TURRET_BODY, (tile, tile))
class Turret (Rammer):
    name = "turret"
    anim = ("Art/Cute_enemy_turret_head", (tile,tile), 10)
 
    IS_GHOST = True
    DIES_OF_BULLET = False
    DROPS_MONEY = False
    
    def startup_process(self, extra):
        super().startup_process(extra)
        self.ship.accel = 0

    def render(self, scene, framecount):
        scene.blit(TURRET_BODY,
            vec_add(self.ship.rect.center,
            scaler_vec_mul(-0.5, (tile, tile))))
        super().render(scene, framecount)

   


actor.SPRITE_CLASSES += [Enemy, Ghost, Rammer, Turret]
