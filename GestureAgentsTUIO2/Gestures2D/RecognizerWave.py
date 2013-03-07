#!/usr/bin/env python
# -*- coding: utf-8 -*-


import GestureAgentsTUIO2.Tuio2 as Tuio
from math import sqrt, fabs
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
from GestureAgentsTUIO2.Gestures2D.RecognizerCursorOnPad import RecognizerCursorOnPad





class RecognizerWave (Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.finger = None
        self.register_event(RecognizerCursorOnPad.newAgent,RecognizerWave.EventNewAgent)
        self.real_positions = []
        self.positions = []
        self.vertex = []
        self.gradients = []
        self.time = 0.4
        self.peaks = 0
        self.fase = "up"
        self.margin = 5
        self.minHeight = 30
        self.num = 0
        self.flats = 0
        self.baseline = 0
        self.ok = None
        self.is_square = 0
        self.straight_down = 0
        self.onPad = None
        self.max = None
        self.maxleft = None
        self.min = None
        self.tooLow = 100

        
    @newHypothesis
    def EventNewAgent(self,Cursor):
        if Cursor.recycled:
            self.fail(cause="Agent is recycled")
        self.agent = self.make_WaveAgent()
        self.agent.cPos = Cursor.cPos
        self.agent.crPos = Cursor.crPos
        self.agent.sid = Cursor.sid
        self.agent.fid = Cursor.fid
        self.real_positions.append(Cursor.cPos)
        self.newAgent(self.agent)
        if Cursor.cPos < self.tooLow:
            self.fail("too low")
        if not self.agent.is_someone_subscribed():
            self.fail(cause="Noone interested")
        else:
            self.unregister_event(RecognizerCursorOnPad.newAgent)
            self.register_event(Cursor.newCursor,RecognizerWave.EventNewCursor)
        
    def EventNewCursor(self,Cursor):
        self.finger = Cursor
        self.vertex.append(0)
        self.positions.append(Cursor.crPos)
        self.baseline = Cursor.crPos[1]
        self.fase = "uppos"
        self.max = -1*(self.minHeight)
        self.min = self.minHeight
        self.maxleft = Cursor.crPos[0]
        self.saw0 = self.positions[0][0]
        #self.agent.positions.append(Cursor.pos)
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerWave.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerWave.EventRemoveCursor)
        #self.onPad = Cursor.onPad
        #acquire should be the last thing to do
        self.acquire(Cursor)
        #self.expire_in(self.time)
    
    def EventMoveCursor(self,Cursor):
        self.positions.append(Cursor.crPos)
        self.real_positions.append(Cursor.cPos)
        
        self.agent.cPos = Cursor.cPos
        self.agent.crPos = Cursor.crPos
        #self.cancel_expire()
        self.num += 1
        self.new = self.positions[-1]
        self.previous = self.positions[-2]
        if self.goes_left():
            self.fail(cause="goes left")
        
        
        if self.fase == "uppos": 
            if self.positions[self.num-1][1] < self.baseline - self.margin:
                self.fail("starts down")
            if self.positions[self.num-1][1] > self.minHeight:
                self.fase = "upposhi"
                self.max = self.minHeight*-1
                return
        elif self.fase == "upposhi":
            if self.goes_down():
                self.fase = "downpos"
                self.vertex.append(self.num-1)
                self.saw1 = self.positions[self.num-1][0]
                return
        elif self.fase == "downpos":
            if self.positions[self.num-1][1] < (self.baseline - self.minHeight):
                self.fase = "downneglo"
                self.min = self.minHeight
                return
        elif self.fase == "downneglo":
            if self.goes_up():
                self.fase = "upneg"
                self.vertex.append(self.num-1)
                self.saw2 = self.positions[self.num-1][0]
                return
        elif self.fase == "upneg":
            self.ok = True
            if Cursor.crPos[1] > self.baseline + self.margin:
                self.fase= "uppos"
                self.vertex.append(self.num-1)
                return
            
        print self.fase
       
            
   
            
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
        else:
            self.fail(cause = "not long enough")

    def goes_left(self):
        #if int(self.new[0]) + self.margin >int(self.previous[0]):
        #if self.new[0] >self.previous[0]:
        if self.new[0]+ self.margin < self.maxleft:
            self.maxleft = self.new[0]
            return True


#    def goes_down(self):
#        #if int(self.new[1])<int(self.previous[1]) + self.margin:
#        #if self.new[1]<self.previous[1]:
#        if self.new[1] + self.margin < self.min:
#            self.min = self.new[1]
#            return True
    
    
    def goes_down(self):
        #if int(self.new[1])<int(self.previous[1]) + self.margin:
        #if self.new[1]<self.previous[1]:
        a = int(self.new[1]) + self.margin/2
        b = int(self.previous[1]) 
        if a < b:        
            return True
      
      
      
#
#    def goes_up(self):
#        #if int(self.new[1]) + self.margin>int(self.previous[1]):
#        #if self.new[1] > self.previous[1]:
#        if self.new[1]-self.margin > self.max:
#            self.max = self.new[1]
#            return True

    def goes_up(self):
        #if int(self.new[1]) + self.margin>int(self.previous[1]):
        #if self.new[1] > self.previous[1]:
        a = int(self.new[1]) 
        b = int(self.previous[1]) + self.margin/2
        if a > b:        
            return True



        
    def long_enough(self):
        if (self.first[0] - self.last[0])>100:
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
        d.positions = self.positions[:]
        d.real_positions = self.real_positions[:]
        d.onPad = self.onPad
        
        return d



        
    def execute(self):
        self.agent.pos1 = self.positions[0]
        self.agent.pos2 = self.positions[-1]
        self.agent.peaks = self.peaks
        self.agent.vertex = self.vertex[:]
        self.agent.gradients= self.gradients[:]
        self.agent.onPad = self.onPad
        self.agent.real_positions = self.real_positions[:]
        lines = 0
        curves = 0
        v = 0
        done = False

          
       
        while v < len(self.vertex)-1:
            if self.is_line(self.vertex[v],self.vertex[v+1]):
                lines += 1
                print "line"
#                grad = self.gradients[v]
#                print grad
#                if grad < (0.2,-0.8):       #int(grad[0]) < 0.2 and int(grad[1]) < -0.8:
#                    print "lined"
#                    if self.is_square > 1:
#                        self.agent.newSquareWave.call(self.agent)
#                    else: self.agent.newSawWave.call(self.agent)
#                    done = True
#                    break
            else:
                curves += 1
                print "curve"
            v += 1
            
        if not done:
            if curves >= lines:
                self.agent.newSineWave.call(self.agent)
            elif lines > curves:
#                up1 = self.positions[0][0]
#                pos = self.vertex[1]
#                up2 = self.positions[pos][0]
                
                if (self.saw2-self.saw1)*2 < self.saw1 - self.saw0: 
                    self.agent.newSawWave.call(self.agent)
                else:
                    self.agent.newTriangleWave.call(self.agent)
                    
        self.finish()
    
    def make_WaveAgent(self):
        a = Agent(("newSineWave","newTriangleWave","newSquareWave","newSawWave",),self)
        return a

    def fail(self, cause="Unknown"):
        print "RecognizerWave(",self,") fail, cause="+cause
        self.unregister_all()
        Recognizer.fail(self,cause)

    
import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerWave)

