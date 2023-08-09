import pygame
import pygame_menu
import src.state as state
import src.saves as saves

c = lambda f, *x: lambda *y: f(*x, *y)

MENU = [None] #i know
STATE = [None]

def change_state(state):
    STATE[0] = state

def get_title_menu(change_state):
    menu = pygame_menu.Menu("Jack and Jackies Jurney", 608, 540, theme = pygame_menu.themes.THEME_SOLARIZED)
    menu.add.button("load game", c(change_state, state.State.OVERWORLD))
    menu.add.button("new game")
    return menu

def startup(music):
    music.change_segname("title")
    STATE[0] = state.State.TITLE
    MENU[0] = get_title_menu(change_state)
    print("statup")

def title_handler(window, framecount, eventlist):
    graphics(window, MENU[0], eventlist)
    return STATE[0]

def graphics(window, menu, eventlist):
    menu.update(eventlist)
    menu.draw(window)
