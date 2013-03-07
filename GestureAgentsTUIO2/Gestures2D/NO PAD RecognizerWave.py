#!/usr/bin/env python
# -*- coding: utf-8 -*-


import GestureAgentsTUIO2.Tuio2 as Tuio
from math import sqrt, fabs
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
#from GestureAgents.RecognizerCursorOnPad import RecognizerCursorOnPad



#FALTA CAMBIAR QUE AGARRE DEL TUIO A QUE AGARRE DE CursorOnPad

#EL 0 ES ABSOLUTO EN EL PAD O RELATIVO A DONDE EMPIEZO?

class RecognizerWave (Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.finger = None
        self.cursorEvents = Tuio.Tuio2CursorEvents
        self.register_event(self.cursorEvents.newAgent,RecognizerWave.EventNewAgent)
        self.positions = []
        self.vertex = [0]
        self.gradients = []
        self.time = 0.4
        self.peaks = 0
        self.fase = "up"
        self.margin = 10
        self.maxdist = 4
        self.num = 0
        self.flats = 0
        self.baseline = 0
        self.ok = None
        self.is_square = 0
        self.straight_down = 0
        self.onPad = None
        self.max = 0
        self.minHeight = 30
        
    @newHypothesis
    def EventNewAgent(self,Cursor):
        if Cursor.recycled:
            self.fail(cause="Agent is recycled")
        self.agent = self.make_WaveAgent()
        self.agent.pos = Cursor.pos
        self.agent.sid = Cursor.sid
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail(cause="Noone interested")
        else:
            self.unregister_all()
            self.register_event(Cursor.newCursor,RecognizerWave.EventNewCursor)
        
    def EventNewCursor(self,Cursor):
        self.finger = Cursor
        self.positions.append(Cursor.pos)
        self.baseline = Cursor.pos[1]
        self.fase = "uppos"
        #self.agent.positions.append(Cursor.pos)
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerWave.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerWave.EventRemoveCursor)
        #self.onPad = Cursor.onPad
        #acquire should be the last thing to do
        self.acquire(Cursor)
        #self.expire_in(self.time)
    
    def EventMoveCursor(self,Cursor):
        self.positions.append(Cursor.pos)
        #self.cancel_expire()
        self.num += 1
        self.new = self.positions[-1]
        self.previous = self.positions[-2]
        if not self.goes_right():
            self.fail(cause="goes left")
        
        if self.fase == "uppos": 
            if self.goes_down():
                self.max = abs(self.positions[self.num-1][1]-self.baseline)
                if self.max < self.minHeight:
                    self.fail(cause="too short")
                self.fase = "downpos"
                self.flats = 0
                self.vertex.append(self.num-1)
            elif not self.goes_up():
                if not self.new[0] == self.previous[0]:
                    self.flats += 1
                    if self.flats > 4:
                        self.max = abs(self.positions[self.num-5][1]-self.baseline)
                        if self.max < self.minHeight:
                            self.fail(cause="too short")
                        self.fase = "flatpos" 
                        self.vertex.append(self.num-5)
                        self.is_square += 1
                        self.flats = 0
        elif self.fase == "flatpos":
            if self.goes_down():
                 self.fase = "downpos"
                 self.vertex.append(self.num-1)                 
        elif self.fase == "downpos":
            if Cursor.pos[1] < self.baseline - self.margin:
                self.fase = "downneg"
        if self.fase == "downneg":
            print "llega a downneg"
            if self.goes_up():
                if self.positions[self.num-1][1]>self.baseline -(self.max*0.3):
                    self.fail(cause="not low enough")
                self.fase = "upneg"
                self.vertex.append(self.num-1)
            elif not self.goes_down():
                if not self.new[0] == self.previous[0]:
                    self.flats += 1
                    if self.flats > 4:
                        self.fase = "flatneg" 
                        self.vertex.append(self.num-5)
                        self.is_square += 1
                        self.flats = 0
        elif self.fase == "flatneg":
            if self.goes_up():
                if self.positions[self.num-5][1]>self.baseline -(self.max*0.3):
                    self.fail(cause="not low enough")
                self.fase = "upneg"
                self.vertex.append(self.num-1)
        if self.fase == "upneg":
            self.ok = True
            if Cursor.pos[1] < self.baseline - self.margin:
                self.fase= "uppos"
            
       
            
   
            
    def EventRemoveCursor(self,Cursor):
        self.unregister_event(Cursor.updateCursor)
        self.unregister_event(Cursor.removeCursor)
        self.first = self.positions[-1]
        self.last = self.positions[0]
        self.vertex.append(self.num)
        if not self.ok:
            self.fail(cause = "no second up phase")
        if self.long_enough():
            self.complete()

    def goes_right(self):
        #if int(self.new[0]) + self.margin >int(self.previous[0]):
        #if self.new[0] >self.previous[0]:
        a = int(self.new[0]) + (self.margin*2)
        b = int(self.previous[0])
        if a > b:
            return True

    def goes_down(self):
        #if int(self.new[1])<int(self.previous[1]) + self.margin:
        #if self.new[1]<self.previous[1]:
        a = int(self.new[1]) + self.margin
        b = int(self.previous[1]) 
        if a < b:        
            return True

    def goes_up(self):
        #if int(self.new[1]) + self.margin>int(self.previous[1]):
        #if self.new[1] > self.previous[1]:
        a = int(self.new[1]) 
        b = int(self.previous[1]) + self.margin
        if a > b:        
            return True


        
    def long_enough(self):
        if (self.first[0] - self.last[0])>300:
            return True

    def is_line(self, v1, v2):
        first = self.positions[v1]
        last = self.positions[v2]
        if first[0] == last[0] or first[1] == last[1]: 
            self.gradients.append(((last[0]-first[0]),(last[1]-first[1])))
            return True
        else:
            dist = sqrt((last[0]-first[0])**2 + (last[1]-first[1])**2 )
            maxdist = dist/20.0
            t = last[0]-first[0], last[1]-first[1]           # Vector ab
            t = t[0]/dist, t[1]/dist               # unit vector of ab
            self.gradients.append(t)
            for p in self.positions[v1:v2]:
                d = self.pdis(self, first,last,p)
                if abs(d) > maxdist:
                    return False
            return True
    
    @staticmethod        
    def pdis(self, a, b, c):
        t = b[0]-a[0], b[1]-a[1]           # Vector ab
        dd = sqrt(t[0]**2+t[1]**2)         # Length of ab
        t = t[0]/dd, t[1]/dd               # unit vector of ab
        n = -t[1], t[0]                    # normal unit vector to ab
        ac = c[0]-a[0], c[1]-a[1]          # vector ac
        return fabs(ac[0]*n[0]+ac[1]*n[1]) # Projection of ac to n (the minimum distance)

    #def get_gradient(self,a,b):
     #   t = b[0]-a[0], b[1]-a[1]           # Vector ab
      #  dd = sqrt(t[0]**2+t[1]**2)         # Length of ab
       # tt = t[0]/dd, t[1]/dd              # unit vector of ab
        #return tt
    
    def duplicate(self):
        d = self.get_copy()
        d.finger = self.finger
        d.positions = self.positions
        d.onPad = self.onPad
        
        return d



        
    def execute(self):
        self.agent.pos1 = self.positions[0]
        self.agent.pos2 = self.positions[-1]
        self.agent.peaks = self.peaks
        self.agent.vertex = self.vertex
        self.agent.gradients= self.gradients
        self.agent.onPad = self.onPad
        lines = 0
        curves = 0
        v = 0
        done = False

          
       
        while v < len(self.vertex)-1:
            if self.is_line(self.vertex[v],self.vertex[v+1]):
                lines += 1
                print "line"
                grad = self.gradients[v]
                print grad
                if grad < (0.2,-0.8):       #int(grad[0]) < 0.2 and int(grad[1]) < -0.8:
                    print "lined"
                    if self.is_square > 1:
                        self.agent.newSquareWave.call(self.agent)
                    else: self.agent.newSawWave.call(self.agent)
                    done = True
                    break
            else:
                curves += 1
                print "curve"
            v += 1
            
        if not done:
            if curves >= lines:
                self.agent.newSineWave.call(self.agent)
            elif lines > curves:
                self.agent.newTriangleWave.call(self.agent)
        self.finish()
    
    def make_WaveAgent(self):
        a = Agent(("newSineWave","newTriangleWave","newSquareWave","newSawWave",),self)
        return a

    def fail(self, cause="Unknown"):
        print "RecognizerWave(",self,") fail, cause="+cause
        Recognizer.fail(self,cause)

    
import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerWave)

