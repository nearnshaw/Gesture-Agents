#!/usr/bin/env python
# -*- coding: utf-8 -*-


import GestureAgentsTUIO2.Tuio2 as Tuio
from math import sqrt, fabs
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent



class RecognizerEnvelope (Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.finger = None
        self.cursorEvents = Tuio.Tuio2CursorEvents
        self.register_event(self.cursorEvents.newAgent,RecognizerEnvelope.EventNewAgent)
        self.positions = []
        self.finalPositions = []
        self.time = 0.5
        self.baseline = 0
        self.margin = 10
        self.tooHigh = 100
        self.max = 0
        self.minLength = 200
        self.onPad = None
    
        
        
    @newHypothesis
    def EventNewAgent(self,Cursor):
        if Cursor.recycled:
            self.fail(cause="Agent is recycled")
        self.agent = self.make_EnvelopeAgent()
        self.agent.pos = Cursor.pos
	self.agent.sid = Cursor.sid
         #self.onPad = Cursor.onPad
        self.positions.append(Cursor.pos)
        self.newAgent(self.agent)
        if Cursor.pos[1] > self.tooHigh:
            self.fail(cause= "start too far from bottom of pad")
        if not self.agent.is_someone_subscribed():
            self.fail(cause="Noone interested")
        else:
            self.unregister_all()
            self.register_event(Cursor.newCursor,RecognizerEnvelope.EventNewCursor)
        
    def EventNewCursor(self,Cursor):
        self.finger = Cursor
        
        self.baseline = Cursor.pos[1]
        self.positions.append(Cursor.pos)
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerEnvelope.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerEnvelope.EventRemoveCursor)
        #acquire should be the last thing to do
        self.acquire(Cursor)
        #self.expire_in(self.time)
    
    def EventMoveCursor(self,Cursor):
        self.positions.append(Cursor.pos)
        #self.cancel_expire()
        self.new = self.positions[-1]
        self.previous = self.positions[-2]
        if self.new[1] > self.max:
            self.max = self.new[1]
        if not self.goes_right():
            self.fail(cause="Goes Left")
        if Cursor.pos[1] < (self.baseline - self.margin - self.max/3):
            self.fail(cause="Below Baseline")
            
       
            
   
            
    def EventRemoveCursor(self,Cursor):
        if Cursor.pos[1] > self.tooHigh:
            self.fail(cause= "end too far from bottom of pad")
        self.unregister_event(Cursor.updateCursor)
        self.unregister_event(Cursor.removeCursor)
        self.first = self.positions[-1]
        self.last = self.positions[0]
        if self.long_enough():
            self.complete()

    def goes_right(self):
        #if int(self.new[0]) + self.margin >int(self.previous[0]):
        #if self.new[0] >self.previous[0]:
        a = int(self.new[0]) 
        b = int(self.previous[0]) - self.margin
        if a > b:
            return True

        
    def long_enough(self):
        if abs(self.first[0] - self.last[0])> self.minLength:
            return True
    
    def duplicate(self):
        d = self.get_copy()
        d.finger = self.finger
        d.positions = self.positions
        d.onPad = self.onPad
        return d
        
    def execute(self):
        self.agent.pos1 = self.positions[0]
        self.agent.pos2 = self.positions[-1]
        self.agent.positions = self.positions
        self.agent.onPad = self.onPad

        i = 1
        miny = self.positions[0][1]
        maxy = self.max - miny
        minx = self.positions[0][0]
        maxx = self.positions[-1][0]-minx
        while i < (len(self.positions)-1):
            self.finalPositions.append(((self.positions[i][0]-minx)/maxx,(self.positions[i][1]-miny)/maxy))
            i += 1
        self.agent.finalPositions = self.finalPositions
        self.agent.newEnvelope.call(self.agent)
        self.finish()
        #está mandando todo el array,  si es mucho para mandar por ahí puedo resumir
        #no queda 0,0 exactamente, habría q redondear da tipo 0.0002

    
    def make_EnvelopeAgent(self):
        a = Agent(("newEnvelope",),self)
        return a
    
import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerEnvelope)

