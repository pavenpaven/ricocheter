import pygame
import src.conf as conf

class Music:
    def __init__(self, theme_info_filename):
        pygame.mixer.init()

        self.is_music_on = conf.conf_search("is_music_on") == "True"
        self.volume = float(conf.conf_search("music_volume"))

        self.current_music = None

        with open(theme_info_filename, "r") as fil:
            txt = fil.read()

        self.theme_list = txt.split("\n;\n")
        self.theme_list = list(map(lambda x: x.split(":\n"), self.theme_list))
        self.theme_list = list(map(lambda x: (x[0], x[1].split("\n")), self.theme_list))

        self.theme_dict = {
                "Pine": conf.conf_search("pine_music"),
                "Cave": conf.conf_search("cave_music"),
                "Desert": conf.conf_search("desert_music"),
                "Title": conf.conf_search("title_music"),
                }


    def change_segname(self, segname: str) -> bool:
        if not self.is_music_on:
            return False
        music_filename = self.music_file_from_theme_name(self.theme_name_from_segname(segname))
        if music_filename == None:
            print("segname has no theme")
            return False
        if music_filename != self.current_music:
            self.current_music = music_filename
            pygame.mixer.music.load(music_filename)
            pygame.mixer.music.play(loops = -1)
            pygame.mixer.music.set_volume(self.volume)
            return True
        return False
    
    def increace_volume(self, x):
        self.volume *= x
        pygame.mixer.music.set_volume(self.volume)
    
    def set_volume(self, x):
        self.volume = x
        pygame.mixer.music.set_volume(self.volume)
    
    def theme_name_from_segname(self, segname: str) -> str: # can return None if not found
        for i in self.theme_list:
            if segname in i[1]:
                return i[0]

    def music_file_from_theme_name(self, theme_name: str) -> str: # can return None
        if theme_name == None:
            return None
        return self.theme_dict[theme_name]


