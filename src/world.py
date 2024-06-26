import math
import pygame
import src.tile_types as tile_types
import src.actor as actor
import src.state as state
import src.music as music
import src.conf as conf
import src.bar as bar
from itertools import chain

from typing import Iterable

tile = 38
Segname = str

BAR_SIZE = (tile*16, tile*2)

def vec2_add(v, w): return (v[0] + w[0], v[1] + w[1])

class Loading_zone_cluster:
    def __init__(self, point_index, segname, posx, posy, sizex, sizey, spawnx, spawny):
        self.rect = pygame.Rect((posx*tile, posy*tile), (sizex*tile, sizey*tile))
        self.linking_index = point_index
        self.spawn_pos = (spawnx*tile, spawny*tile)
        self.segname = segname

    def get_tiles(self):
        out = []
        n=0
        for i in range(self.rect.height):
            k = []
            for f in range(self.rect.width):
                k.append((f, n))
            out.append(k)
            n+=1
        return out

    def string(self):
        # Converts object into storable string needs to round because 9 / 3 = 3.0 and that will become "3.0"
        str_rect = ".".join([str(round(self.rect.x / tile)), str(round(self.rect.y / tile)), str(round(self.rect.w / tile)), str(round(self.rect.h / tile))])
        str_spawn = ".".join([str(round(self.spawn_pos[0] / tile)), str(round(self.spawn_pos[1] / tile))])
        #print(self.spawn_pos)
        return ".".join([str(self.linking_index), self.segname, str_rect, str_spawn]) 

def get_segname_room(filename, segname: Segname | None): #returns segment if not found returns -1
    with open(filename, "r") as fil:
        text = fil.read()
        
    for i in text.split("?"):
        segments = i.split("#")
        if segments[0].replace("\n", "") == segname:
            break
    else:
        print(f"no segment name named: { segname}")
        return -1
    return "#".join(segments)    

class Map:
        def __init__(self, size, pos, current_state: state.State): #size is a tuple
            self.size = size
            self.pos = pos
            #texture= pygame.image.load(backgrund_filename)
            #self.backgrund_tile = pygame.transform.scale(texture,size)
            self.surface = pygame.Surface((size[0]*tile, size[1]*tile))
            self.tiles = []
            self.loading_zone = []
            self.actors = {"Title": [actor.Earth((10*tile,4*tile), self.change_state ,self.kill_actor)]}
            self.state = current_state
            self.segname = None # dont try access the segname if nothing is 
            self.CAMERA_SHAKE = True
            self.IS_LEVEL_EDIT = False
            self.framecount = 0
            self.opendoor = -10000

            
        @property
        def loaded_actors(self) -> list[actor.Sprite]:
            if self.segname in self.actors:
                return list(dict.fromkeys(self.actors[self.segname]
                                        + list(filter(lambda x:x.IS_GLOBALLY_LOADED, chain(*self.actors.values())))))
            return []
        def change_state(self, changed_state: state.State) -> None:
          self.state = changed_state
      
        def load_room(self, filename, segname: Segname | None, music): # segname None means find spawn
            if not segname:
                with open(filename, "r") as fil:
                    text = fil.read()
                segname = text.split("=")[1]
                print(segname)

            segments = get_segname_room(filename, segname)
            if segments == -1:
                return -1
            self.segname = segname
            segments = segments.split("#")
            row = segments[1].split("\n")
            self.tiles=[]
            u=0
            for i in row:
                row_tiles = []
                for f in i:
                    if f[0] == "1" or f[0] == "2" or f[0] == "3" or f[0] == "|":
                        if f[0] == "|":
                            u = -1
                        else:
                            u = int(f[0])
                    else:
                        row_tiles.append(tile_types.Tile_type.find(f).index - u)
                        u = 0
                self.tiles.append(row_tiles)


            lz_segs = segments[2].split(";") # lz_segs for loading_zone_segments
            if lz_segs[0]:
                func = lambda x: Loading_zone_cluster(int(x[0]), x[1], int(x[2]), int(x[3]), int(x[4]), int(x[5]), int(x[6]), int(x[7]))
                #print(list(map(lambda x: x.split("."), lz_segs)))
                self.loading_zone = list(map(func, list(map(lambda x: x.split(".") ,lz_segs))))
            else:
                self.loading_zone = []
#           self.actors = actor.load_sprites(segname, "Level/actors", self.change_state, self.kill_actor)
            music.change_segname(segname) # idk self.music should alsow be in combat


        def render(self, window, player, music, framecount):
            self.surface.fill((0,0,0))
            self.framecount = framecount
            #self.surface.blit(self.backgrund_tile, (0,0))
            if not self.tiles: #yes i know
                self.load_room(conf.conf_search("starting_filename"), conf.conf_search("starting_segname"), music)
            
            for i in tile_types.Tile_type.types:
                i.update(framecount)

            y = 0
            for i in self.tiles:
                x = 0
                for f in i:
                    self.surface.blit(tile_types.Tile_type.types[f].texture, (x,y))
                    x += tile
                y += tile
            
            mouse = pygame.mouse.get_pos()
            mouse = mouse[0] - self.pos[0], mouse[1] - self.pos[1]
            for i in self.loaded_actors:
              i.step(self, player) #tf
              if i.rect.collidepoint(mouse):
                  i.mouse_over()
              if i.rect.colliderect(player.rect):
                  i.step_on(player)
                  if i.IS_ENEMY:
                      player.hit(i, framecount)
              i.render(self.surface, framecount)
            
            imag = player.render(framecount)
            self.surface.blit(imag, (player.rect.x, player.rect.y))

            if not self.IS_LEVEL_EDIT and self.segname in self.actors:
                door_index = tile_types.Tile_type.find("x").index # x is door (yellow wall)
                if door_index in chain(*self.tiles) or list(filter(lambda x:x.IS_GHOST, self.loaded_actors)): 
                    if not list(filter(lambda x: x.IS_ENEMY and not x.IS_GHOST, self.loaded_actors)):
                        self.actors[self.segname] = list(filter(lambda x: not x.IS_GHOST, self.actors[self.segname]))
                        yellow_plate_index = tile_types.Tile_type.find("O").index # O is yellow plate
                        self.tiles = list(map(lambda y:
                                              list(map(lambda x: yellow_plate_index if x == door_index else x, y)), self.tiles))


            if not self.IS_LEVEL_EDIT:
                bluewall_index = tile_types.Tile_type.find("G").index
                redwall_index = tile_types.Tile_type.find("g").index
                if bluewall_index in chain(*self.tiles) or redwall_index in chain(*self.tiles): 
                    if not framecount % (96):
                        blue_plate_index = tile_types.Tile_type.find("d").index # O is yellow plate
                        red_plate_index = tile_types.Tile_type.find("E").index
                        self.tiles = list(map(lambda y:
                                              list(map(lambda x: blue_plate_index if x == bluewall_index else (bluewall_index if x == blue_plate_index else x ), y)), self.tiles))
                        self.tiles = list(map(lambda y:
                                              list(map(lambda x: red_plate_index if x == redwall_index else (redwall_index if x == red_plate_index else x ), y)), self.tiles))


                if player.open_door:
                    player.physics.last_hit_tile = tile_types.Tile_type.find("a")
                    player.open_door = False 
                    self.opendoor = framecount 
                    boss_door_index = tile_types.Tile_type.find("U").index
                    plate_index = tile_types.Tile_type.find("a").index
                    self.tiles = list(map(lambda y:
                                          list(map(lambda x: plate_index if x == boss_door_index else x, y)), self.tiles))
                                    
                
            if self.CAMERA_SHAKE:
                if player.last_hit == framecount or self.opendoor == framecount:
                    window.blit(self.surface, vec2_add(self.pos, (5, 4)))
                elif player.last_hit + 1 == framecount or self.opendoor + 1 == framecount:
                    window.blit(self.surface, vec2_add(self.pos, (-3, -2)))
                else:
                    window.blit(self.surface, self.pos)
            else:
                window.blit(self.surface, self.pos)
            window.blit(bar.draw(BAR_SIZE, framecount, player), (0,0))


        def save(self, filename, segname):
            with open(filename, "r") as fil:
                tex = fil.read()
            n = 0
            seg = tex.split("?") 
            for i in seg:
                if i.split("#")[0].replace("\n", "") == segname:
                    break
                n+=1
            #print(tex)
            #print(n, seg, segname)
            seg.pop(n)
            str_loading_info = ";".join(list(map(Loading_zone_cluster.string, self.loading_zone)))
            room_info = segname + "#" + self.convert_to_letters() + "#" + str_loading_info
            seg.insert(n, room_info)
            result = "?".join(seg)

            with open(filename, "w") as fil:
                fil.write(result)
                
        def convert_to_letters(self):
            out = ""
            n=0
            for i in self.tiles:
                for f in i:
                    out += tile_types.Tile_type.find_letter(f)
                if not n == len(self.tiles) -1:
                    out += "\n"
                n+=1
            return out
        
        def rotate(self, n: int) -> None:
            if n == 0:
                return None
            self.tiles.pop(len(self.tiles)-1)
            tuples = zip(*self.tiles[::-1])
            self.tiles = [list(i) for i in tuples]
            types = tile_types.Tile_type.types
            def magic(tile_type: tile_types.Tile_type) -> tile_types.Tile_type: # what the actual
                x = tile_types.get_ordered_family(tile_type, tile_type)
                return x[(x.index(tile_type)+1)%len(x)]

            self.tiles = [[magic(types[i]).index for i in j] for j in self.tiles]

            self.tiles.append([])
            self.rotate(n-1)

        def kill_actor(self, n:int) -> None:
            self.actors = dict(map(lambda y:
                                   (y, list(filter(lambda x: x.index != n, self.actors[y]))),
                                   self.actors))
            
