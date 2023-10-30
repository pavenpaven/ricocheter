import pygame
import pygame_menu
import src.state as state
import src.saves as saves
import src.world_handler as world_handler
from src.world import tile

c = lambda f, *x: lambda *y: f(*x, *y)

def sv(scaler: int, vec: (float, float)) -> (float, float): return (scaler * vec[0], scaler * vec[1])

title_texture = pygame.image.load("Art/title.png")
title_rect    = title_texture.get_rect()
title_texture = pygame.transform.scale(title_texture, sv(600 / title_rect.width, title_rect.size))


credit = " Programer: pavenpaven (on github) \n Art: Chiminiio, Blagurka \n Font: Daniel Linssen (check out on itch.io) "

MENU = [None] #i know
STATE = [None]
CREDIT_FONT = pygame.font.Font("Art/m3x6.ttf", 50)
CREDIT_TEXT_SURFACE = CREDIT_FONT.render(credit, False, (0, 0, 0))

them = pygame_menu.themes.THEME_SOLARIZED.copy()
them.widget_font = CREDIT_FONT
them.widget_font_color = (255,255,255)
them.widget_selection_color = (215, 190, 105)
them.widget_font_background_color = (0,0,0)

them.title = False
them.title_font = CREDIT_FONT
them.title_font_color = (255, 255, 255)
them.background_color = (int("47", 16), int("19", 16), int("61", 16), 0)
them.widget_selection_effect = pygame_menu.widgets.SimpleSelection()
#them.widget_selection_effect = pygame_menu.widgets.LeftArrowSelection()

def change_state(state: state.State):
    STATE[0] = state
    world_handler.jack.physics.rect.x, world_handler.jack.physics.rect.y = (7*tile, 7*tile) 
    world_handler.scene.tiles = [] # what the

def get_credit_menu():
    menu = pygame_menu.Menu("Credits", 608, 540, theme=them)
    menu.add.button("back", pygame_menu.events.BACK)
    for i in credit.split("\n"):
        menu.add.label(i)
    return menu


def get_title_menu(change_state):
    credit_menu = get_credit_menu()

    menu = pygame_menu.Menu("the Ricocheter and the Broken Moon", 608, 540, theme = them )
    a = menu.add.button("Start", c(change_state, state.State.MAP_GEN))
    d = menu.add.button("Load", c(change_state, state.State.OVERWORLD))
    b = menu.add.button("Credits", credit_menu)
    a.set_font(CREDIT_FONT, 50, (255,255,255), (215, 190, 105), (0,0,0), (83, 68, 21), None, antialias=False )
    b.set_font(CREDIT_FONT, 50, (255,255,255), (215, 190, 105), (0,0,0), (83, 68, 21), None, antialias=False )
    d.set_font(CREDIT_FONT, 50, (255,255,255), (215, 190, 105), (0,0,0), (83, 68, 21), None, antialias=False )
    return menu

def startup(music):
    world_handler.scene.load_room("Level/tile_map", "Title", music)
    world_handler.jack.physics.rect.x, world_handler.jack.physics.rect.y = (-30,0)
    STATE[0] = state.State.TITLE
    MENU[0] = get_title_menu(change_state)
    print("statup")

def title_handler(window, framecount, eventlist, music):
    graphics(window, MENU[0], eventlist, framecount, music)
    return STATE[0]

def graphics(window, menu, eventlist, framecount, music):
    world_handler.graphics(window, music, framecount)
    menu.update(eventlist)
    menu.draw(window)
    window.blit(title_texture, (10,-50))
