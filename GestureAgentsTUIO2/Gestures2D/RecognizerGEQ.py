#!/usr/bin/env python
# -*- coding: utf-8 -*-


import GestureAgentsTUIO2.Tuio2 as Tuio
from math import sqrt, fabs
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgentsTUIO2.Gestures2D.RecognizerCursorOnPad import RecognizerCursorOnPad
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent



class RecognizerGEQ (Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.finger = None
        self.register_event(RecognizerCursorOnPad.newAgent,RecognizerGEQ.EventNewAgent)
        self.positions = []
        self.real_positions = []
        self.time = 1
        self.margin = 5
        self.p =  [0,0,0,0,0]
        self.peaks = []
        self.fase = "flat"
        self.padHeight = 300
        self.onPad = None
        self.maxright = None
        
    @newHypothesis
    def EventNewAgent(self,Cursor):
        if Cursor.recycled:
            self.fail(cause="Agent is recycled")
        self.agent = self.make_GEQAgent()
        self.agent.cPos = Cursor.cPos
        self.agent.sid = Cursor.sid
        #self.onPad = Cursor.onPad
        self.positions.append(Cursor.crPos)
        self.real_positions.append(Cursor.cPos)
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail(cause="Noone interested")
        else:
            self.unregister_event(RecognizerCursorOnPad.newAgent)
            self.register_event(Cursor.newCursor,RecognizerGEQ.EventNewCursor)
        
    def EventNewCursor(self,Cursor):
        #cursor is an Agent
        self.finger = Cursor
        #self.agent.positions.append(Cursor.pos)
        self.maxright = Cursor.crPos[0]
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerGEQ.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerGEQ.EventRemoveCursor)
        #acquire should be the last thing to do
        self.acquire(Cursor)
        #self.expire_in(self.time)
    
    def EventMoveCursor(self,Cursor):
        self.positions.append(Cursor.crPos)
        self.real_positions.append(Cursor.cPos)
        #self.cancel_expire()
        self.new = self.positions[-1]
        self.previous = self.positions[-2]
        if self.goes_right():
            self.fail(cause= "goes right")
       
            
   
            
    def EventRemoveCursor(self,Cursor):
        self.unregister_event(Cursor.updateCursor)
        self.unregister_event(Cursor.removeCursor)
        self.first = self.positions[0]
        self.last = self.positions[-1]
        if self.long_enough():
            self.complete()
        else:
            self.fail("not long enough when removing")

    def goes_right(self):
        #if int(self.new[0]) + self.margin >int(self.previous[0]):
        #if self.new[0] >self.previous[0]:
        if self.new[0] - self.margin > self.maxright:
            self.maxright = self.new[0]
            return True
        
       
    def long_enough(self):
        if (self.first[0] - self.last[0])>100:
            return True
    
    def duplicate(self):
        d = self.get_copy()
        d.finger = self.finger
        d.positions = self.positions[:]
        d.onPad = self.onPad
        return d
    
##    def getMidPoint (self, start, end):
##        startx = start[0]
##        endx = end[0]
##        lookfor = (startx + endx)/2
##        a = self.positions.index(start)
##        while a < self.positions.index(end):
##            if self.positions[a][0] < lookfor:
##                return self.positions[a]
##                break
##            a +=1
##        #si falla encontrar la coordenada x promedio tira el index promedio en positions
##        b = self.positions.index(start)+self.positions.index(end)/2
##        return self.positions[b]
            

        
    def execute(self):
 
        self.agent.onPad = self.onPad            
        self.agent.pos1 = self.positions[0]
        self.agent.pos2 = self.positions[-1]
        self.agent.positions = self.positions[:]
        self.agent.real_positions = self.real_positions[:]
        #self.agent.finalPositions = self.finalPositions
        self.agent.newGEQ.call(self.agent)
        self.finish()
    
    def make_GEQAgent(self):
        a = Agent(("newGEQ",),self)
        return a
    
    def fail(self,cause):
        self.unregister_all()
        print "GEQ fails: %s" % (cause,)
        Recognizer.fail(self, cause)
    
import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerGEQ)

