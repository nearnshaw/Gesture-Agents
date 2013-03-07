# -*- coding: cp1252 -*-
import GestureAgentsTUIO2.Tuio2 as Tuio
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
#from GestureAgentsTUIO2.Gestures2D.RecognizerPad import RecognizerPad
from GestureAgentsTUIO2.Gestures2D.RecognizerCursorOnPad import RecognizerCursorOnPad
import math

#ASUMO QUE SE CREO UNA CLASE RECOGNIZERPAD   que tome el figure y lo reconozca como second display


class RecognizerPadTap(Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.register_event(RecognizerCursorOnPad.newAgent,RecognizerPadTap.EventNewAgent)
        self.crPos = None
        self.onPad = None
        self.fid = None
        self.origin = None
        self.time = 0.5
        self.maxd = 20
        self.cPos = None
	self.name = "RecognizerPadTap"
        

    @newHypothesis
    def EventNewAgent(self,Cursor):
        if Cursor.recycled:
            self.fail("Cursor is recycled")
        self.agent = self.MakePadTapAgent()
        self.cPos = Cursor.cPos
        self.crPos = Cursor.crPos
        self.agent.cPos = self.cPos
        self.agent.crPos = self.crPos
        self.agent.onPad = Cursor.onPad
        self.agent.fid = Cursor.fid
        self.agent.sid = Cursor.sid
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail("Noone interested")
        self.register_event(Cursor.newCursor, RecognizerPadTap.NewTap)
        self.unregister_event(RecognizerCursorOnPad.newAgent)
        
    def NewTap(self,Cursor):
        self.finger = Cursor
        self.crPos = Cursor.crPos
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerPadTap.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerPadTap.EventRemoveCursor)
        self.expire_in(self.time)
        self.origin = Cursor.crPos
        self.acquire(Cursor)


    def EventMoveCursor(self,Cursor):
        if self.dist(Cursor.crPos,self.origin) > self.maxd:
            self.fail("Cursor moved")
    
    def EventRemoveCursor(self,Cursor):
        self.cancel_expire()
        self.unregister_event(Cursor.updateCursor)
        self.unregister_event(Cursor.removeCursor)
        self.complete()
             
    def dist(self, a,b):
        dx,dy = (a[0]-b[0],a[1]-b[1])
        return math.sqrt(dx**2 + dy**2)        



    def MakePadTapAgent(self):
        evts = ["newPadTap"]
        a = Agent(evts, self)
        return a


    def execute(self):
        self.agent.newPadTap.call(self.agent)
        self.finish()

    def duplicate(self):
        d = self.get_copy()
        d.crPos = self.crPos
        d.origin = self.origin
        return d


import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerPadTap)
