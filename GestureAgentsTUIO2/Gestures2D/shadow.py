#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import pygame.locals
import pygame.draw
import random, math


import GestureAgentsPygame.Screen as Screen
from GestureAgents.Recognizer import Recognizer
#import GestureAgentsPygame.Render as Render


class shadowPad:
    def __init__(self,recognizer):
        Screen.ScreenDraw.register(shadowPad.draw,self)
        self.recognizer = recognizer
        
        #Screen.draw_shadows.register(shadow.draw,self)
        #después pasar el screen draw_shadows al screendraw? eso decía carles?

    def draw(self):
        surface = Screen.sharedsurface
        a = self.recognizer.agent
        #print a
        if a:
            pos = (a.px,a.py)
            dimensions = (400,300)
            pygame.draw.rect(surface, (255,)*3 , pos+dimensions , 1)


class shadowCursorOnPad:
    def __init__(self,recognizer):
        Screen.ScreenDraw.register(shadowCursorOnPad.draw,self)
        self.recognizer = recognizer
        
        #Screen.draw_shadows.register(shadow.draw,self)
        #después pasar el screen draw_shadows al screendraw? eso decía carles?

    def draw(self):
        surface = Screen.sharedsurface
        a = self.recognizer.agent
        #print self.recognizer
        if a:
            pos = map(int,a.cPos)
            #dimensions = (400,300)
            pygame.draw.circle(surface, (125,)*3 , pos, 10 , 0)





class shadowCursorOffPad:
    def __init__(self,recognizer):
        Screen.ScreenDraw.register(shadowCursorOffPad.draw,self)
        self.recognizer = recognizer
        
        #Screen.draw_shadows.register(shadow.draw,self)
        #después pasar el screen draw_shadows al screendraw? eso decía carles?

    def draw(self):
        surface = Screen.sharedsurface
        a = self.recognizer.agent
        #print self.recognizer
        if a:
            pos = map(int,a.pos)
            #dimensions = (400,300)
            pygame.draw.circle(surface, (255,)*3 , pos, 10 , 0)












