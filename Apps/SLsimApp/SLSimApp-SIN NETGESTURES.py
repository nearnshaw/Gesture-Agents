'''
Created on 05/07/2012

@author: carles
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import pygame
import pygame.locals
import pygame.draw
import random, math
from pygame.time import Clock
import sys
sys.path.append('../..')




import GestureAgentsPygame.Screen as Screen
#from GestureAgentsTUIO.Gestures2D.RecognizerStick import RecognizerStick
#from GestureAgentsTUIO.Gestures2D.RecognizerDoubleTap import RecognizerDoubleTap
#from GestureAgentsTUIO.Gestures2D.RecognizerTap import RecognizerTap
from GestureAgents.AppRecognizer import AppRecognizer
import GestureAgentsPygame.Render as Render
#from GestureAgentsTUIO.Tuio import TuioCursorEvents
from GestureAgentsTUIO2.Tuio2 import Tuio2CursorEvents
from GestureAgentsTUIO2.Tuio2 import Tuio2FigureEvents

#from GestureAgentsTUIO2.Gestures2D.RecognizerStick import RecognizerStick
from GestureAgentsTUIO2.Gestures2D.RecognizerDoubleTap import RecognizerDoubleTap
from GestureAgentsTUIO2.Gestures2D.RecognizerTap import RecognizerTap
from GestureAgentsTUIO2.Gestures2D.RecognizerEnvelope import RecognizerEnvelope
from GestureAgentsTUIO2.Gestures2D.RecognizerCursorOnPad import RecognizerCursorOnPad
from GestureAgentsTUIO2.Gestures2D.RecognizerWave import RecognizerWave
from GestureAgentsTUIO2.Gestures2D.RecognizerSwipe import RecognizerSwipe
from GestureAgentsTUIO2.Gestures2D.RecognizerGEQ import RecognizerGEQ
from GestureAgentsTUIO2.Gestures2D.RecognizerTapTempo import RecognizerTapTempo
from GestureAgentsTUIO2.Gestures2D.RecognizerDrag import RecognizerDrag

from GestureAgents.AppRecognizer import AppRecognizer



class PaintingApp:
    def __init__(self):
        Screen.ScreenDraw.register(PaintingApp.draw,self)
        self.surface = pygame.Surface(Screen.size,flags=pygame.locals.SRCALPHA)
        AppRecognizer(Tuio2CursorEvents).newAgent.register(PaintingApp.newAgentPaint,self)
        AppRecognizer(Tuio2FigureEvents).newAgent.register(PaintingApp.newAgentFigure,self)
        self.button = (400,400)
        self.buttoncolor = (0,100,255)
        self.surface = pygame.Surface(Screen.size,flags=pygame.locals.SRCALPHA)
        self.full_gesture_list = ["tap", "doubleTap", "tapTempo", "envelope", "swipe", "wave"]
        self.gesture_list = self.full_gesture_list
        self.score = 0

        #AppRecognizer(RecognizerCursorOnPad).newAgent.register(PaintingApp.newAgentCursorOnPad,self)
        #AppRecognizer(RecognizerPad).newAgent.register(PaintingApp.newAgentPad,self)
        AppRecognizer(RecognizerTap).newAgent.register(PaintingApp.newAgentTap,self)
        #AppRecognizer(RecognizerDoubleTap).newAgent.register(PaintingApp.newAgentDoubleTap,self)
        #AppRecognizer(RecognizerStick).newAgent.register(PaintingApp.newAgentStick,self)
        AppRecognizer(RecognizerEnvelope).newAgent.register(PaintingApp.newAgentEnvelope,self)
        AppRecognizer(RecognizerWave).newAgent.register(PaintingApp.newAgentWave,self)
        #AppRecognizer(RecognizerSwipe).newAgent.register(PaintingApp.newAgentSwipe,self)
        AppRecognizer(RecognizerGEQ).newAgent.register(PaintingApp.newAgentGEQ,self)
        AppRecognizer(RecognizerTapTempo).newAgent.register(PaintingApp.newAgentTapTempo,self)
        ##FALTAAppRecognizer(RecognizerDrag).newAgent.register(PaintingApp.newAgentDrag,self)
        #drag 2 fingers vx multiselect 1??
        self.update_list("begin")




    def newAgentCursorOnPad (self, Cur):
        print "new CursorOnPad" , Cur.pos
        Cur.newCursorOnPad.register(self.bogus,self)


    def bogus (self, Cur):
        print "bogus"

    def newAgentPad( self, Pad):
        print "new Pad" 
        Pad.newPad.register(self.bogus,self)


    def newAgentTap(self,Tap):
        print "Possible Tap in " , Tap.pos
        pygame.draw.circle(self.surface, (0,100,200) , map(int,Tap.pos), 10, 0)
        #We accept Taps
        Tap.newTap.register(PaintingApp.newTap,self)
    
    def newTap(self,Tap):
        print "TAP! ------- " , Tap.pos
        self.update_list("tap")
    
    def newAgentDoubleTap(self,Tap):
        print "Possible Double Tap in " , Tap.pos
        
        Tap.newDoubleTap.register(self.newDoubleTap,self)
    
    def newDoubleTap(self,Tap):
        print "DOUBLE TAP! ------- " , Tap.pos
        self.update_list("doubleTap")






    def newAgentStick(self,S):
        print "Possible Stick in " , S.pos
        #We accept Taps
        S.newStick.register(self.newStick,self)

    def newStick(self,Stick):
        print "Stick! ------- " , Stick.pos1 , " --> " , Stick.pos2
        self.update_list("stick")

    def newAgentEnvelope(self,Env):
        print "Possible Envelope in " , Env.pos
        #We accept Taps
        Env.newEnvelope.register(self.newEnvelope,self)

    def newEnvelope(self,Env):
        print "Envelope! ------- " , Env.positions, Env.finalPositions
        self.update_list("envelope")

    def newAgentSwipe(self,Swipe):
        print "Possible Pad Swipe in " ,  "falta activar OnPad"
        #We accept Taps
        Swipe.newSwipe.register(self.newSwipe,self)

    def newSwipe(self,Swipe):
        print "SWIPE! ------- " , "falta activar OnPad"
        self.update_list("swipe")

    def newAgentGEQ(self,GEQ):
        print "Possible GEQ in "
        #We accept Taps
        GEQ.newGEQ.register(self.newGEQ,self)

    def newGEQ(self,GEQ):
        print "GEQ! ------- " , GEQ.peaks, GEQ.finalPositions
        self.update_list("GEQ")




    def newAgentWave(self,Wave):
        print "Possible Wave", Wave.pos;
        Wave.newSineWave.register(self.newSineWave,self)
        Wave.newTriangleWave.register(self.newTriangleWave,self)
        Wave.newSawWave.register(self.newSawWave,self)
        Wave.newSquareWave.register(self.newSquareWave,self)
        

    def newSineWave(self, Wave):
        print "SINE WAVE! -------  peaks" , " vertexes in " , str(Wave.vertex) , " gradients:", Wave.gradients  , Wave.pos1 , " --> " , Wave.pos2
        self.update_list("sineWave")

    def newTriangleWave(self, Wave):
        print "TRIANGLE WAVE! -------  peaks" , " vertexes in " , str(Wave.vertex) , " gradients:", Wave.gradients  , Wave.pos1 , " --> " , Wave.pos2
        self.update_list("triagnleWave")

    def newSawWave(self, Wave):
        print "SAW WAVE! -------  peaks" , " vertexes in " , str(Wave.vertex) , " gradients:", Wave.gradients  , Wave.pos1 , " --> " , Wave.pos2
        self.update_list("sawWave")

    def newSquareWave(self, Wave):
        print "SQUARE WAVE! -------  peaks" , " vertexes in " , str(Wave.vertex) , " gradients:", Wave.gradients  , Wave.pos1 , " --> " , Wave.pos2
        self.update_list("squareWave")

    def newAgentTapTempo(self, TapT):
        print "Possible Tap Tempo in ", TapT.pos
        TapT.newTapTempo.register(self.newTapTempo,self)
        

    def newTapTempo(self, TapT):
        print "TAP TEMPO! ------- ", TapT.tempo
        self.update_list("tapTempo")




    def update_list(self, gesture):
        
        if gesture in self.gesture_list:
            self.gesture_list.remove(gesture)
            print self.gesture_list

        
        if len(self.gesture_list) == 0:
            self.gesture_list = self.full_gesture_list
            self.score += self.score
            
        pygame.font.init()
        self.font = pygame.font.Font(None, 25)
        self.show_text(self.score, 100,100, self.font)
        posx = 100
        posy = 100
        for g in self.gesture_list:
            gtext = str(g)
            self.show_text(gtext, posx,posy,self.font)
            posy += 20
        

        
    def show_text(self,dtext, x, y,font):
        text = font.render(dtext, True, (255,255,255))
        #textpos = text.get_rect()
        #textpos.centerx = background.get_rect().centerx
        pos = x,y
        self.surface.blit(text, pos)
        
        #text = font.render("%s%s%s" % (dtext), 1, (0, 255, 255, 0))
  














        
    def newAgentPaint(self,agent):
        #context here
        agent.updateCursor.register(PaintingApp.event_painting,self)

    def newAgentFigure(self,agent):
        #context here
        agent.updateFigure.register(PaintingApp.event_painting_f,self)
    
    
    def draw(self):
        pygame.draw.circle(self.surface, self.buttoncolor , self.button , 50, 3)
        Render.drawT(self.surface)
        
    
    def event_painting(self,Point):
        #print Point.pos
        pygame.draw.circle(self.surface, (255,100,100) , map(int,Point.pos), 10, 0)
    
    def event_painting_f(self,Point):
        #print Point
        pygame.draw.circle(self.surface, (min(255,Point.figure.roll),100,100) , map(int,Point.pos), 10, 0)
    
    #def event_new_dtap(self,Tap):
     #   #pygame.draw.circle(self.surface, (0,255,100) , map(int,Tap.pos), 10, 0)
      #  self.buttoncolor = [random.randint(0,255) for _ in self.buttoncolor]
       # self.surface.fill(0)
    
   # def event_new_tap(self,Tap):
    #    pygame.draw.circle(self.surface, (0,100,200) , map(int,Tap.pos), 10, 0)
        
    @staticmethod
    def dist(a,b):
        dx,dy = (a[0]-b[0],a[1]-b[1])
        return math.sqrt(dx**2 + dy**2)
        
if __name__ == "__main__":
    import GestureAgentsPygame
    app = PaintingApp()
    GestureAgentsPygame.run_apps()
