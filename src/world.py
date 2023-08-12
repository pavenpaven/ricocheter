import math
import pygame
import src.tile_types as tile_types
import src.actor as actor
import src.state as state
import src.music as music
import src.conf as conf

tile = 38

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

def get_segname_room(filename, segname): #returns segment if not found returns -1
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
            self.actors = []
            self.state = current_state

        def change_state(self, changed_state: state.State) -> None:
          self.state = changed_state
      
        def load_room(self, filename, segname, music):
            segments = get_segname_room(filename, segname)
            if segments == -1:
                return -1
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

            self.actors = actor.load_sprites(segname, "Level/actors", self.change_state)
            music.change_segname(segname) # idk self.music should alsow be in combat


        def render(self, window, player, music, framecount):
            self.surface.fill((0,0,0))
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

            for i in self.actors:
              i.render(self.surface)
            
            imag = player.render(framecount)
            self.surface.blit(imag, (player.rect.x, player.rect.y))
          
            window.blit(self.surface, self.pos)
        
        def save(self, filename, segname):
            with open(filename, "r") as fil:
                tex = fil.read()
            n = 0
            seg = tex.split("?") 
            for i in seg:
                if i.split("#")[0].replace("\n", "") == segname:
                    break
                n+=1
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
            self.tiles.append([])
            self.rotate(n-1)
