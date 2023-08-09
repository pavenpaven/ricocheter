import pygame
import pygame_menu
import src.world_handler as world_handler
import src.state as state
import src.conf as conf
#import saves add later

c = lambda f,x: lambda :f(x)

MENU = [None] #i know
STATE = [None]

def change_state(music):
    world_handler.scene.load_room(conf.conf_search("starting_filename"), conf.conf_search("starting_segname"), music)
    world_handler.jack.pos = (100,100)
    STATE[0] = state.State.OVERWORLD

def get_gameover_menu(change_state,music):
    menu = pygame_menu.Menu("Game over", 600, 500, theme = pygame_menu.themes.THEME_SOLARIZED)
    menu.add.button("resume", c(change_state, music))
    return menu

def startup(music):
    music.change_segname("gameover")
    STATE[0] = state.State.GAMEOVER
    MENU[0] = get_gameover_menu(change_state, music)

def gameover_handler(window, framecount, eventlist):
    graphics(window, MENU[0], eventlist)
    return STATE[0]

def graphics(window, menu, eventlist):
    menu.update(eventlist)
    menu.draw(window)
