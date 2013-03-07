# -*- coding: cp1252 -*-
import GestureAgentsTUIO2.Tuio2 as Tuio
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
#from GestureAgentsTUIO2.Gestures2D.RecognizerPad import RecognizerPad
from GestureAgentsTUIO2.Gestures2D.RecognizerTap import RecognizerTap
from GestureAgentsTUIO2.Gestures2D.RecognizerCursorOnPad import RecognizerCursorOnPad
import math

#FALTA CAMBIAR QUE AGARRE DEL TUIO A QUE AGARRE DE CursorOnPad
#FALTA DESCOMENTAR LO DE OnPad

class RecognizerTwoFingers(Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.register_event(RecognizerCursorOnPad.newAgent,RecognizerTwoFingers.EventNewTAgent)
        self.onPad = None
        self.cur1 = None
        self.cur2 = None
        self.crPos1 = None
        self.crPos2 = None        
        self.name = "RecognizerTwoFingers"
        self.maxSpace = 60
        #self.time = 0.25
        self.oneOff = False
        self.avPos = None
        self.cPos1 = None
        self.cPos2 = None
        self.onPad = None

    @newHypothesis
    def EventNewTAgent(self,Cursor):
        if Cursor.recycled:
            self.fail("Cursor is recycled")
        self.agent = self.MakeTwoFingersAgent()
        self.crPos1 = Cursor.crPos
        self.crPos2 = self.crPos1
        self.cPos1 = Cursor.cPos
        self.cPos2 = Cursor.cPos
        self.agent.cPos = self.cPos1
        self.agent.crPos = self.crPos1
        self.fid = Cursor.fid
        self.onPad = Cursor.onPad
        self.agent.fid = Cursor.fid
        self.agent.sid = Cursor.sid
        #a este punto hago posc2 igual A posc1 pq si era null me tira un error
        self.newAgent(self.agent)
        #tiene que haber un paso en C# que se fije si está sobre algo
        if not self.agent.is_someone_subscribed():
            self.fail("Noone interested")
        self.unregister_event(RecognizerCursorOnPad.newAgent)
        self.register_event(Cursor.newCursor, RecognizerTwoFingers.NewCursor)
        
    def NewCursor(self,Cursor):
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerTwoFingers.EventMoveCursor1)
        self.register_event(Cursor.removeCursor,RecognizerTwoFingers.EventRemoveCursor)
        self.register_event(RecognizerCursorOnPad.newAgent,RecognizerTwoFingers.EventNewCAgent2)
        self.cur1 = Cursor
        self.acquire(Cursor)
        #self.onPad = Cursor.onPad
        #self.expire_in(self.time)
        
        
        
        

    def EventMoveCursor1(self,Cursor):
        self.crPos1 = Cursor.crPos
        self.cPos1 = Cursor.cPos
        if self.cur2 == True and self.oneOff == False:
            if self.dist(Cursor, self.cur2) > self.maxspace:
                self.fail(cause= "cursors separated")
            else:
                self.agent.crPos = self.averagePos(self.crPos1, self.crPos2)
                self.agent.cPos = self.averagePos(self.cPos1, self.cPos2)
                self.agent.updateCursor.call(self.agent)
        else:
            self.agent.crPos = Cursor.crPos
            self.agent.cPos = Cursor.cPos
            self.agent.updateCursor.call(self.agent)

    def EventMoveCursor2(self,Cursor):
        self.crPos2 = Cursor.crPos
        self.cPos2 = Cursor.cPos
        if self.oneOff == False:
            if self.dist(Cursor, self.cur1) > self.maxspace:
                self.fail(cause= "cursors separated")
            else:
                self.agent.crPos = self.averagePos(self.crPos1, self.crPos2)
                self.agent.cPos = self.averagePos(self.cPos1, self.cPos2)
                self.agent.updateCursor.call(self.agent)
        else:
            self.agent.crPos = Cursor.crPos
            self.agent.cPos = Cursor.cPos
            self.agent.updateCursor.call(self.agent)

            
    def EventRemoveCursor(self,Cursor):
        #que estén los dos out!
        if not self.cur2:
            self.fail( cause = "no second cursor")
            self.unregister_event(Cursor.newCursor)
        if self.oneOff:
            self.agent.removeCursor.call(self.agent)
            self.unregister_event(Cursor.updateCursor)
            self.unregister_event(Cursor.removeCursor)
            self.unregister_all()
            self.finish()
        else:
            self.oneOff = True
            self.unregister_event(Cursor.updateCursor)
            self.unregister_event(Cursor.removeCursor)


    @newHypothesis    
    def EventNewCAgent2(self,Cursor):
        #self.cancel_expire()
        self.unregister_event(RecognizerCursorOnPad.newAgent)
        if Cursor.recycled:
            self.fail(cause ="Cursor is recycled")
        self.cPos2 = Cursor.cPos
        self.crPos2 = Cursor.crPos
        if not self.is_close():
            #if self.is_on_same(Cursor):
            self.fail(cause ="new Cursor is far")
        self.register_event(Cursor.newCursor, RecognizerTwoFingers.NewCursor2)        
                  
    def NewCursor2(self,Cursor):
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerTwoFingers.EventMoveCursor2)
        self.register_event(Cursor.removeCursor,RecognizerTwoFingers.EventRemoveCursor)
        self.cur2 = Cursor
        self.acquire(self.cur2)
        self.complete()
        

       

    def averagePos (p1, p2):
        avPos = (p1[0] + p2[0] /2),(p1[1] + p2[1] /2)
        return avPos
  
   
    def dist(self,a,b):
        dx,dy = (a[0]-b[0],a[1]-b[1])
        return math.sqrt(dx**2 + dy**2)


    def MakeTwoFingersAgent(self):
        evts = ["newCursor","updateCursor","removeCursor"]  
        a = Agent(evts, self)
        return a


    def is_on_same(self, Cursor):
        if Cursor.onPad == self.onPad:
            return True
    

    def is_close(self):
        if self.dist(self.cPos1,self.cPos2) < self.maxSpace:
            return True

    def fail(self, cause="Unknown"):
        try:
            self.unregister_all()
        except:
            None
        Recognizer.fail(self,cause)   


            
    def execute(self):
        self.agent.crPos1 = self.cur1.crPos1
        self.agent.crPos2 = self.cur2.crPos
        self.avPos = self.averagePos()
        self.agent.crPos = self.avPos
        self.agent.onPad = self.onPad
        self.agent.newCursor.call(self.agent)
        
        

    def duplicate(self):
        d = self.get_copy()
        d.onPad = self.onPad
        d.cur1 = self.cur1
        d.crPos1 = self.crPos1
        d.avPos = self.avPos
        d.cPos1 = self.cPos1
        return d

import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerTwoFingers)
