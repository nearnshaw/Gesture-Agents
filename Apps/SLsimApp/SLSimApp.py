'''
Created on 05/07/2012

@author: carles
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-


#import pygame
import pygame.locals
import pygame.draw
from pygame.time import Clock
import sys
sys.path.append('../..')
from Prova import NetGestures

import time

import GestureAgentsPygame.Screen as Screen
#from GestureAgentsTUIO.Gestures2D.RecognizerStick import RecognizerStick
#from GestureAgentsTUIO.Gestures2D.RecognizerDoubleTap import RecognizerDoubleTap
#from GestureAgentsTUIO.Gestures2D.RecognizerTap import RecognizerTap
from GestureAgents.AppRecognizer import AppRecognizer
import GestureAgentsPygame.Render as Render
#from GestureAgentsTUIO.Tuio import TuioCursorEvents
from GestureAgentsTUIO2.Tuio2 import Tuio2CursorEvents
from GestureAgentsTUIO2.Tuio2 import Tuio2FigureEvents

import os, os.path

def getnextfilename(pattern):
    for n in xrange(5000):
        fname = pattern % n
        if not os.path.exists(fname):
            return fname



netgestures = NetGestures()



def DynFunc(f):return f


class PaintingApp:
    def __init__(self):
        #self.surface = pygame.Surface(Screen.size,flags=pygame.locals.SRCALPHA)
        #AppRecognizer(Tuio2CursorEvents).newAgent.register(PaintingApp.newAgentPaint,self)
        #AppRecognizer(Tuio2FigureEvents).newAgent.register(PaintingApp.newAgentFigure,self)
        self.active = False
        self.button = (400,400)
        self.buttoncolor = (0,100,255)
        self.surface = pygame.Surface(Screen.size,flags=pygame.locals.SRCALPHA)
        Screen.sharedsurface = self.surface
        self.full_gesture_list = ["tap", "doubleTap", "tapTempo", "envelope", "equalizer", "sine wave", "triangle wave", "saw wave"]
        self.gesture_count = len(self.full_gesture_list)
        self.gesture_list = self.full_gesture_list[:]
        self.score = 0
        #time = timer(self.surface)

        netgestures.RegisterHelperAppRecognizer("GestureAgentsTUIO2.Gestures2D.RecognizerTap", DynFunc(self.newAgentTap))
        netgestures.RegisterHelperAppRecognizer("GestureAgentsTUIO2.Gestures2D.RecognizerDoubleTap", DynFunc(self.newAgentDoubleTap))
        
        netgestures.RegisterHelperAppRecognizer("GestureAgentsTUIO2.Gestures2D.RecognizerEnvelope", DynFunc(self.newAgentEnvelope))
        #netgestures.RegisterHelperAppRecognizer("GestureAgentsTUIO2.Gestures2D.RecognizerPadTap", DynFunc(self.newAgentPadTap))
        netgestures.RegisterHelperAppRecognizer("GestureAgentsTUIO2.Gestures2D.RecognizerWave", DynFunc(self.newAgentWave))
        #netgestures.RegisterHelperAppRecognizer("GestureAgentsTUIO2.Gestures2D.RecognizerPadSwipe", DynFunc(self.newAgentPadSwipe))
        netgestures.RegisterHelperAppRecognizer("GestureAgentsTUIO2.Gestures2D.RecognizerGEQ", DynFunc(self.newAgentGEQ))
        netgestures.RegisterHelperAppRecognizer("GestureAgentsTUIO2.Gestures2D.RecognizerTapTempo", DynFunc(self.newAgentTapTempo))

        #drag 2 fingers vx multiselect 1??
        self.startingtime= time.time()
        self.totaltime = 2*60
        self.falta = 0
        self.update_list("begin")
        #self.lognum = 0
        self.logfile = None
        self.inittimegesture = {}
        Screen.ScreenDraw.register(PaintingApp.draw,self)
        


    def bogus (self, Cur):
        print "bogus"

    def newAgentPad( self, Pad):
        print "new Pad" 
        netgestures.RegisterHelper(Pad.newPad, DynFunc(self.bogus))


    def newAgentTap(self,Tap):
        if not self.active: return
        #pygame.draw.circle(self.surface, (0,100,200) , map(int,Tap.pos), 10, 0)
        #We accept Taps
        netgestures.RegisterHelper(Tap.newTap, DynFunc(self.newTap))
        self.inittimegesture[Tap]=time.time()
        print "Possible Tap in " , Tap.pos

    
    def newTap(self,Tap):
        self.update_list("tap")
        duracion = time.time() - self.inittimegesture[Tap]
        print >> self.logfile, "%f Detected Tap (%f->%f) duration %f" % (time.time(),self.inittimegesture[Tap],time.time(),duracion) 
        print "TAP! ------- " , Tap.pos
        
    
    def newAgentDoubleTap(self,Tap):
        netgestures.RegisterHelper(Tap.newDoubleTap, DynFunc(self.newDoubleTap))
        self.inittimegesture[Tap]=time.time()
        print "Possible Double Tap in " , Tap.pos
        
    
    def newDoubleTap(self,Tap):
        if self.active:
            print "DOUBLE TAP! ------- " , Tap.pos
            self.update_list("doubleTap")
            duracion = time.time() - self.inittimegesture[Tap]
            print >> self.logfile, "%f Detected Double Tap (%f->%f) duration %f" % (time.time(),self.inittimegesture[Tap],time.time(),duracion) 
        else:
            newdir = getnextfilename("logs_%d")
            os.mkdir(newdir)
            for d in os.listdir(os.getcwd()):
                if d.endswith('.log'):
                    os.rename(d,newdir+"/"+d)
            self.startingtime= time.time()
            self.gesture_list= self.full_gesture_list[:]
            self.logfile = open(getnextfilename("Subjects/%d.log"),'w')
            #self.lognum +=1
            self.active = True
            print >> self.logfile, "%d Init session" % time.time()

    def newAgentPadTap(self,Tap):
        if not self.active: return
        netgestures.RegisterHelper(Tap.newPadTap, DynFunc(self.newPadTap))
        self.inittimegesture[Tap]=time.time()
        print "Possible Pad Tap in " , Tap.cPos

    
    def newPadTap(self,Tap):
        self.update_list("tap on pad")
        duracion = time.time() - self.inittimegesture[Tap]
        print >> self.logfile, "%f Detected Tap on Pad (%f->%f) duration %f" % (time.time(),self.inittimegesture[Tap],time.time(),duracion) 
        print "TAP on Pad! ------- " , Tap.cPos
        


    def newAgentEnvelope(self,Env):
        if not self.active: return
        print "Possible Envelope " #, Env.pos
        self.inittimegesture[Env]=time.time()
        #We accept Taps
        netgestures.RegisterHelper(Env.newEnvelope, DynFunc(self.newEnvelope))

    def newEnvelope(self,Env):
        print "Envelope! ------- " , Env.positions, Env.finalPositions
        for p in Env.real_positions:
            pygame.draw.circle(self.surface, (255,100,100) , map(int,p), 10, 0)  
        self.update_list("envelope")
        duracion = time.time() - self.inittimegesture[Env]
        print >> self.logfile, "%f Detected Envelope (%f->%f) duration %f" % (time.time(),self.inittimegesture[Env],time.time(),duracion) 
        
#swipe O PAD swipe?????
        
    def newAgentPadSwipe(self,Swipe):
        if not self.active: return
        print "Possible Pad Swipe in " ,  "falta activar OnPad"
        self.inittimegesture[Swipe]=time.time()
        #We accept Taps
        netgestures.RegisterHelper(Swipe.newPadSwipe, DynFunc(self.newPadSwipe))

    def newPadSwipe(self,Swipe):
        print "SWIPE! ------- " , "falta activar OnPad"
        self.update_list("three finger swipe")
        duracion = time.time() - self.inittimegesture[Swipe]
        print >> self.logfile, "%f Detected Pad Swipe (%f->%f) duration %f" % (time.time(),self.inittimegesture[Swipe],time.time(),duracion) 

    def newAgentGEQ(self,GEQ):
        if not self.active: return
        self.inittimegesture[GEQ]=time.time()
        print "Possible GEQ in "
        #We accept Taps
        netgestures.RegisterHelper(GEQ.newGEQ, DynFunc(self.newGEQ))

    def newGEQ(self,GEQ):
        print "GEQ! ------- " #, GEQ.peaks, GEQ.finalPositions
        for p in GEQ.real_positions:
            pygame.draw.circle(self.surface, (255,100,100) , map(int,p), 10, 0)  
        self.update_list("equalizer")
        duracion = time.time() - self.inittimegesture[GEQ]
        print >> self.logfile, "%f Detected GEQ (%f->%f) duration %f" % (time.time(),self.inittimegesture[GEQ],time.time(),duracion) 




    def newAgentWave(self,Wave):
        if not self.active: return
        self.inittimegesture[Wave]=time.time()
        print "Possible Wave"#, Wave.pos;
        netgestures.RegisterHelper(Wave.newSineWave, DynFunc(self.newSineWave))
        netgestures.RegisterHelper(Wave.newTriangleWave, DynFunc(self.newTriangleWave))
        netgestures.RegisterHelper(Wave.newSawWave, DynFunc(self.newSawWave))
        netgestures.RegisterHelper(Wave.newSquareWave, DynFunc(self.newSquareWave))
        

    def newSineWave(self, Wave):
        print "SINE WAVE! -------  peaks" 
        for p in Wave.real_positions:
            pygame.draw.circle(self.surface, (255,100,100) , map(int,p), 10, 0)  
        self.update_list("sine wave")
        duracion = time.time() - self.inittimegesture[Wave]
        print >> self.logfile, "%f Detected Sine Wave (%f->%f) duration %f" % (time.time(),self.inittimegesture[Wave],time.time(),duracion) 

        
    def newTriangleWave(self, Wave):
        print "TRIANGLE WAVE! -------  peaks"
        for p in Wave.real_positions:
            pygame.draw.circle(self.surface, (255,100,100) , map(int,p), 10, 0)
        self.update_list("triangle wave")
        duracion = time.time() - self.inittimegesture[Wave]
        print >> self.logfile, "%f Detected Triangle Wave (%f->%f) duration %f" % (time.time(),self.inittimegesture[Wave],time.time(),duracion) 

    def newSawWave(self, Wave):
        print "SAW WAVE! -------  peaks" 
        for p in Wave.real_positions:
            pygame.draw.circle(self.surface, (255,100,100) , map(int,p), 10, 0)
        self.update_list("saw wave")
        duracion = time.time() - self.inittimegesture[Wave]
        print >> self.logfile, "%f Detected Saw Wave (%f->%f) duration %f" % (time.time(),self.inittimegesture[Wave],time.time(),duracion) 

    def newSquareWave(self, Wave):
        print "SQUARE WAVE! -------  peaks" 
        for p in Wave.real_positions:
            pygame.draw.circle(self.surface, (255,100,100) , map(int,p), 10, 0)
        self.update_list("square wave")
        duracion = time.time() - self.inittimegesture[Wave]
        print >> self.logfile, "%f Detected Square Wave (%f->%f) duration %f" % (time.time(),self.inittimegesture[Wave],time.time(),duracion) 

    def newAgentTapTempo(self, TapT):
        if not self.active: return
        self.inittimegesture[TapT]=time.time()
        print "Possible Tap Tempo in ", TapT.pos
        netgestures.RegisterHelper(TapT.newTapTempo, DynFunc(self.newTapTempo))
        

    def newTapTempo(self, TapT):
        print "TAP TEMPO! ------- ", TapT.tempo
        self.update_list("tapTempo")
        duracion = time.time() - self.inittimegesture[TapT]
        print >> self.logfile, "%f Detected TapTempo (%f->%f) duration %f" % (time.time(),self.inittimegesture[TapT],time.time(),duracion) 




    def update_list(self, gesture):
        
        pygame.font.init()
        if gesture in self.gesture_list:
            i = self.gesture_list.index(gesture)
            self.gesture_list[i] = "----------------"
            self.gesture_count -= 1
            self.score += 1
            print self.gesture_list
            print self.gesture_count

        
        if self.gesture_count == 0:
            self.gesture_list = self.full_gesture_list[:]
            self.gesture_count = len(self.full_gesture_list)
            self.surface.fill(0)
            
    
            
        
        self.font = pygame.font.Font(None, 25)
        self.show_text("SCORE     %d" % int(self.score), 500,250, self.font)
        self.show_text("TIME       %d" % int(self.falta), 500,290, self.font)
        posx = 250
        posy = 200
        for g in self.gesture_list:
            gtext = str(g)
            self.show_text(gtext, posx,posy,self.font)
            posy += 20
        

        
    def show_text(self,dtext, x, y,font):
        text = font.render(str(dtext), True, (255,255,255))
        #textpos = text.get_rect()
        #textpos.centerx = background.get_rect().centerx
        pos = x,y
        self.surface.blit(text, pos)
        
        #text = font.render("%s%s%s" % (dtext), 1, (0, 255, 255, 0))
  



    
    
    def draw(self):
        #pygame.draw.circle(self.surface, self.buttoncolor , self.button , 50, 3)
        if self.active:
            self.falta = self.totaltime -  (time.time()-self.startingtime)
            if self.falta < 0:
                #cerramos .. 
                self.active = False
            self.update_list(None)
            Render.drawT(self.surface)
            self.surface.fill(0)
        else:
            self.surface.fill(0)
            Render.drawT(self.surface)
            self.surface.fill(0)
        
    

    

#        
#    @staticmethod
#    def dist(a,b):
#        dx,dy = (a[0]-b[0],a[1]-b[1])
#        return math.sqrt(dx**2 + dy**2)



#POLICY RULES:

    from GestureAgents.Agent import Agent
    


    @Agent.completion_policy.rule(50)
    def always_tap_tempo(r1,r2):
        "Tap Tempo always wins"
        from GestureAgentsTUIO2.Gestures2D.RecognizerTapTempo import RecognizerTapTempo
        if type(r2) == RecognizerTapTempo:
            return True

#    @Agent.completion_policy.rule(40)
#    def tap_on_pad_complete(r1,r2):
#        "Tap on pad always wins"
#        from GestureAgentsTUIO2.Gestures2D.RecognizerTap import RecognizerTap
#        from GestureAgentsTUIO2.Gestures2D.RecognizerPadTap import RecognizerPadTap
#        if type(r2) == RecognizerPadTap and type(r1) == RecognizerTap:
#            return True
#    
#    @Agent.compatibility_policy.rule(40)
#    def tap_on_pad_compat(r1,r2):
#        "Tap on pad always wins"
#        from GestureAgentsTUIO2.Gestures2D.RecognizerTap import RecognizerTap
#        from GestureAgentsTUIO2.Gestures2D.RecognizerPadTap import RecognizerPadTap
#        if type(r2) == RecognizerPadTap and type(r1) == RecognizerTap:
#            return True

    

    @Agent.completion_policy.rule(90)
    def always_pad_swipe(r1,r2):
        "pad swipe ALWAYS wins"
        from GestureAgentsTUIO2.Gestures2D.RecognizerPadSwipe import RecognizerPadSwipe
        from GestureAgentsTUIO2.Gestures2D.RecognizerWave import RecognizerWave
        from GestureAgentsTUIO2.Gestures2D.RecognizerGEQ import RecognizerGEQ
        from GestureAgentsTUIO2.Gestures2D.RecognizerEnvelope import RecognizerEnvelope
        from GestureAgentsTUIO2.Gestures2D.RecognizerPadTap import RecognizerPadTap
        
        if type(r2) == RecognizerPadSwipe:
            if type(r1) == RecognizerWave or type(r1) == RecognizerGEQ or type(r1) == RecognizerEnvelope or type(r1) == RecognizerPadTap:
                return True 

    @Agent.compatibility_policy.rule(90)
    def never_change_pad_swipe(r1,r2):
        "never change pad swipe ALWAYS"
        from GestureAgentsTUIO2.Gestures2D.RecognizerPadSwipe import RecognizerPadSwipe
        from GestureAgentsTUIO2.Gestures2D.RecognizerWave import RecognizerWave
        from GestureAgentsTUIO2.Gestures2D.RecognizerGEQ import RecognizerGEQ
        from GestureAgentsTUIO2.Gestures2D.RecognizerEnvelope import RecognizerEnvelope
        from GestureAgentsTUIO2.Gestures2D.RecognizerPadTap import RecognizerPadTap
        
        if type(r2) == RecognizerPadSwipe:
            if type(r1) == RecognizerWave or type(r1) == RecognizerGEQ or type(r1) == RecognizerEnvelope or type(r1) == RecognizerPadTap:
                return True 


        
if __name__ == "__main__":
    import GestureAgentsPygame
    app = PaintingApp()
    GestureAgentsPygame.run_apps()
