import pygame
import os
import math

comp = lambda f,g:lambda *x:f(g(*x))

class Animation:
    def __init__(self, directory, size, frame_delay):
        self.frame_delay = frame_delay
        self.frames = list(map(comp(pygame.image.load, lambda x:f"{directory}/{x}"), sorted(os.listdir(directory), key=lambda x:int(x.replace(".png", "").split("-")[2])))) #normal magic
        self.frames = list(map(lambda x:pygame.transform.scale(x, size), self.frames))
        self.texture = self.frames[0]

    def update(self, framecount):
        self.texture = self.frames[math.floor(framecount/self.frame_delay) % len(self.frames)]


