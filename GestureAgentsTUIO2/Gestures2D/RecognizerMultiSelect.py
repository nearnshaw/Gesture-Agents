# -*- coding: cp1252 -*-
import GestureAgentsTUIO2.Tuio2 as Tuio
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
#from GestureAgentsTUIO2.Gestures2D.RecognizerPad import RecognizerPad
from GestureAgentsTUIO2.Gestures2D.RecognizerTap import RecognizerTap
#from GestureAgentsTUIO2.Gestures2DRecognizerCursorOnPad import RecognizerCursorOnPad
import math

#FALTA CAMBIAR QUE AGARRE DEL TUIO A QUE AGARRE DE CursorOnPad
#FALTA DESCOMENTAR LO DE OnPad

class RecognizerMultiSelect(Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.register_event(Tuio.Tuio2CursorEvents.newAgent,RecognizerMultiSelect.EventNewTAgent)
        self.name = "RecognizerMultiSelect"
        self.origin = None
        self.pos = None
        self.mind = 10


   

    @newHypothesis
    def EventNewTAgent(self,Cursor):
        if Cursor.recycled:
            self.fail("Cursor is recycled")
        self.agent = self.MakeMultiSelectAgent()
        self.origin = Cursor.pos
        self.pos = Cursor.pos
        self.agent.pos = Cursor.pos
        self.agent.origin = Cursor.pos
	self.agent.sid = Cursor.sid
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail("Noone interested")
        #tiene que haber un paso en C# que se fije si está sobre algo
        #if not on_something:
        #   self.fail("not on a matrix dot)
        self.unregister_event(Tuio.Tuio2CursorEvents.newAgent)
        self.register_event(Cursor.newCursor, RecognizerMultiSelect.NewCursor)
        
    def NewCursor(self,Cursor):
        self.acquire(Cursor)
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerMultiSelect.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerMultiSelect.EventRemoveCursor)
        self.complete()
        
        
        
        

    def EventMoveCursor(self,Cursor):
        self.pos = Cursor.pos
        self.agent.pos = Cursor.pos
        self.agent.moveMSelect.call(self.agent)
        
            
            
    def EventRemoveCursor(self,Cursor):
        if self.dist(self.origin, Cursor.pos)< self.mind:
            self.fail("didnt move")
        self.agent.endMSelect.call(self.agent)
        self.finish()

       

    def dist(self,a,b):
        dx,dy = (a[0]-b[0],a[1]-b[1])
        return math.sqrt(dx**2 + dy**2)       



    def MakeMultiSelectAgent(self):
        evts = ["newMSelect","moveMSelect","endMSelect"] 
        a = Agent(evts, self)
        return a


            
    def execute(self):
        self.agent.newMSelect.call(self.agent)
        

    def duplicate(self):
        d = self.get_copy()
        d.origin = self.origin
        d.pos = self.pos
        return d

import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerMultiSelect)
