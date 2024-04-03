import pygame

import src.actor as actor
from src.actor import re
import src.physics as physics 

blue_bullet_texture = re("Art/Cute_bullet_blue.png", (15, 15))

class Bullet(actor.Sprite):
    texture = re("Art/Cute_bullet.png", (15,15))
    size = (15,15)
    name = "bullet"
    IS_BULLET = True
    MAX_BOUNDS = 2
    COUNTER = None
    DAMAGE = 1
    
    def startup_process(self, extra):
        self.bounds_count = 0
        def f(_):
            self.bounds_count += 1
            self.texture = blue_bullet_texture
            if self.bounds_count > self.MAX_BOUNDS:
                self.kill(self.index)
                if self.COUNTER:
                    self.COUNTER.reset()
        self.physics = physics.Physics_object(pygame.Rect(self.pos, self.size), (0,0), 20, f)

    def step(self, scene, player):
       self.physics.update(scene)
       self.pos = (self.physics.rect.x, self.physics.rect.y)

actor.SPRITE_CLASSES.append(Bullet)
