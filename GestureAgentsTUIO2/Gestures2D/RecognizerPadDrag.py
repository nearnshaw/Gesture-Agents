# -*- coding: cp1252 -*-
import GestureAgentsTUIO2.Tuio2 as Tuio
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
#from GestureAgentsTUIO2.Gestures2D.RecognizerPad import RecognizerPad
from GestureAgentsTUIO2.Gestures2D.RecognizerTap import RecognizerTap
from GestureAgentsTUIO2.Gestures2D.RecognizerCursorOnPad import RecognizerCursorOnPad
from GestureAgentsTUIO2.Gestures2D.RecognizerTwoFingers import RecognizerTwoFingers
import math

#FALTA CAMBIAR QUE AGARRE DEL TUIO A QUE AGARRE DE CursorOnPad
#FALTA DESCOMENTAR LO DE OnPad

class RecognizerPadDrag(Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.register_event(RecognizerTwoFingers.newAgent,RecognizerPadDrag.EventNewTAgent)
        self.name = "RecognizerPadDrag"
        self.pos = None
        self.started = False
        self.origin = None
        self.mind = 10
	self.fid = None

   

    @newHypothesis
    def EventNewTAgent(self,Cursor):
        if Cursor.recycled:
            self.fail("Cursor is recycled")
        self.agent = self.MakeDragAgent()
        self.cPos = Cursor.cPos
	self.crPos = Cursor.crPos
        self.origin = Cursor.cPos
	self.fid = Cursor.fid
        self.agent.cPos = Cursor.cPos
        self.agent.crPos = Cursor.crPos
        self.agent.sid = Cursor.sid
	self.agent.fid = Cursor.fid
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail("Noone interested")
        #tiene que haber un paso en C# que se fije si está sobre algo
        #if not on_something:
        #   self.fail("not on anything dragable)
        self.unregister_event(RecognizerTwoFingers.newAgent)
        self.register_event(Cursor.newCursor, RecognizerPadDrag.NewCursor)
        
    def NewCursor(self,Cursor):
        
        Cursor.origin = Cursor.cPos
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerPadDrag.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerPadDrag.EventRemoveCursor)
        self.acquire(Cursor)
        self.complete()
        
        
        
        

    def EventMoveCursor(self,Cursor):
        self.cPos = Cursor.cPos
        self.crPos = Cursor.crPos
        self.agent.cPos = Cursor.cPos
        self.agent.crPos = Cursor.crPos
        self.agent.dragMove.call(self.agent)
        
            
            
    def EventRemoveCursor(self,Cursor):
        if self.dist(self.origin, Cursor.cPos)< self.mind:
            self.fail("didnt move")
        self.unregister_event(Cursor.updateCursor)
        self.unregister_event(Cursor.removeCursor)
        self.agent.dragDrop.call(self.agent)
        self.finish()
       
    def dist(self,a,b):
        dx,dy = (a[0]-b[0],a[1]-b[1])
        return math.sqrt(dx**2 + dy**2)




    def MakeDragAgent(self):
        evts = ["newDrag","dragMove","dragDrop"] 
        a = Agent(evts, self)
        return a


            
    def execute(self):
        self.fail_all_others()
        self.agent.newDrag.call(self.agent)
        

    def duplicate(self):
        d = self.get_copy()
        return d

import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerPadDrag)
