#!/usr/bin/env python
# -*- coding: utf-8 -*-


import GestureAgentsTUIO2.Tuio2 as Tuio
from math import sqrt, fabs
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgentsTUIO2.Gestures2D.RecognizerCursorOnPad import RecognizerCursorOnPad
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent



class RecognizerEnvelope (Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.finger = None
        self.register_event(RecognizerCursorOnPad.newAgent,RecognizerEnvelope.EventNewAgent)
        self.real_positions = []
        self.positions = []
        self.finalPositions = []
        self.time = 0.5
        self.baseline = 0
        self.max = 0
        self.min = 0
        self.margin = 5
        self.tooHigh = 100
        self.minLength = 200
        #self.margin = 0.25
        #self.tooHigh = 5
        #self.minLength = 4
        self.onPad = None
        self.name = "RecognizerEnvelope"
    
        
        
    @newHypothesis
    def EventNewAgent(self,Cursor):
        if Cursor.recycled:
            self.fail(cause="Agent is recycled")
        self.agent = self.make_EnvelopeAgent()
        self.agent.crPos = Cursor.crPos
        self.agent.crPos = Cursor.crPos
        self.agent.sid = Cursor.sid
        self.onPad = Cursor.onPad
        self.real_positions.append(Cursor.cPos)
        self.positions.append(Cursor.crPos)
        self.newAgent(self.agent)
        if Cursor.crPos[1] > self.tooHigh:
            self.fail(cause= "start too far from bottom of pad ( %f > %f )" % (Cursor.crPos[1] , self.tooHigh) )
        if not self.agent.is_someone_subscribed():
            self.fail(cause="Noone interested")
        else:
            self.unregister_event(RecognizerCursorOnPad.newAgent)
            self.register_event(Cursor.newCursor,RecognizerEnvelope.EventNewCursor)
        
    def EventNewCursor(self,Cursor):
        self.finger = Cursor
        self.baseline = Cursor.crPos[1]
        self.min = Cursor.crPos[1]
        self.maxleft = Cursor.crPos[0]
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerEnvelope.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerEnvelope.EventRemoveCursor)
        #acquire should be the last thing to do
        self.acquire(Cursor)
        #self.expire_in(self.time)
    
    def EventMoveCursor(self,Cursor):
        self.real_positions.append(Cursor.cPos)
        self.positions.append(Cursor.crPos)
        #self.cancel_expire()
        self.new = self.positions[-1]
        self.previous = self.positions[-2]
        if self.new[1] > self.max:
            self.max = self.new[1]
        if self.new[1] < self.min:
            self.min = self.new[1]
        if self.goes_left():
            self.fail(cause="Goes Left")
        if Cursor.crPos[1] < (self.baseline - self.margin - ((self.max-self.baseline)/3)):
            self.fail(cause="Below Baseline")
            
       
            
   
            
    def EventRemoveCursor(self,Cursor):
        if Cursor.crPos[1] > self.tooHigh:
            self.fail(cause= "end too far from bottom of pad")
        self.unregister_event(Cursor.updateCursor)
        self.unregister_event(Cursor.removeCursor)
        self.first = self.positions[-1]
        self.last = self.positions[0]
        if self.long_enough():
            self.complete()
        else:
            self.fail("not long enough")



    def goes_left(self):
        #if int(self.new[0]) + self.margin >int(self.previous[0]):
        #if self.new[0] >self.previous[0]:
        if self.new[0]+ self.margin < self.maxleft:
            self.maxleft = self.new[0]
            return True


        
    def long_enough(self):
        if abs(self.first[0] - self.last[0])> self.minLength:
            return True
    
    def duplicate(self):
        d = self.get_copy()
        d.finger = self.finger
        d.positions = self.positions[:]
        d.real_positions = self.real_positions[:]
        d.finalPositions = self.finalPositions[:]
        d.onPad = self.onPad
        return d
        
    def execute(self):
        self.agent.pos1 = self.positions[0]
        self.agent.pos2 = self.positions[-1]
        self.agent.positions = self.positions[:]
        self.agent.real_positions = self.real_positions[:]
        self.agent.onPad = self.onPad

        i = 1
        miny = self.min
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

    def fail(self,cause):
        print "Envelope fails: %s" % (cause,)
        Recognizer.fail(self, cause)
    
import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerEnvelope)

