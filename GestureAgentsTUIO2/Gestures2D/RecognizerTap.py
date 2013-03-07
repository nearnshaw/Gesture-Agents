#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GestureAgentsTUIO2.Tuio2 as Tuio
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
from .shadow import shadowCursorOffPad
#from GestureAgentsTUIO2.Gestures2D.shadow import shadow
import math


class RecognizerTap(Recognizer):
    #for debugging porpuses we have a count of instances
    newAgent = Event()
    def __init__(self):
        self.finger = None
        Recognizer.__init__(self)
        #shadow.__init__(self)
        self.cursorEvents = Tuio.Tuio2CursorEvents
        self.register_event(self.cursorEvents.newAgent,RecognizerTap.EventNewAgent)
        self.maxd = 10
        self.time = 0.4
        self.origin = None
        self.shadow = shadowCursorOffPad(self)
    
    @newHypothesis
    def EventNewAgent(self,Cursor):
        # Am I interested on this Agent?
        # We don't want recycled Agents
        if Cursor.recycled:
            self.fail("Cursor is recycled")
        # Let's ask our subscribbers
        self.agent = self.make_TapAgent()
        self.agent.pos = Cursor.pos
        self.agent.sid = Cursor.sid
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail("Noone interested")
        else:
            self.unregister_event(self.cursorEvents.newAgent)
            self.register_event(Cursor.newCursor,RecognizerTap.EventNewCursor)
        
    def EventNewCursor(self,Cursor):
        self.finger = Cursor
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerTap.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerTap.EventRemoveCursor)
        self.expire_in(self.time)
        self.origin = Cursor.pos
        self.acquire(Cursor)

    
    def EventMoveCursor(self,Cursor):
        if self.dist(Cursor.pos,self.origin) > self.maxd:
            self.fail("Cursor moved")
    
    def EventRemoveCursor(self,Cursor):
        self.cancel_expire()
        self.unregister_event(Cursor.updateCursor)
        self.unregister_event(Cursor.removeCursor)
        self.complete()
            
    def execute(self):
        self.agent.pos = self.origin
        self.agent.newTap.call(self.agent)
        self.finish()
    
    @staticmethod
    def dist(a,b):
        dx,dy = (a[0]-b[0],a[1]-b[1])
        return math.sqrt(dx**2 + dy**2)
    
    def duplicate(self):
        d = self.get_copy()
        d.finger = self.finger
        d.origin = self.origin
        d.shadow = shadowCursorOffPad(d)
        return d
        
    def make_TapAgent(self):
        a = Agent(("newTap",),self)
        return a

import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerTap)
