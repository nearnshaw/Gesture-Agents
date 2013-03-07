# -*- coding: cp1252 -*-
import GestureAgentsTUIO2.Tuio2 as Tuio
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
#from GestureAgentsTUIO2.Gestures2D.RecognizerPad import RecognizerPad
#from GestureAgentsTUIO2.Gestures2D.RecognizerTap import RecognizerTap
from GestureAgentsTUIO2.Gestures2D.RecognizerCursorOnPad import RecognizerCursorOnPad
import math


#FALTA DESCOMENTAR LO DE OnPad

class RecognizerPadSwipe(Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.register_event(RecognizerCursorOnPad.newAgent,RecognizerPadSwipe.EventNewAgent)
        self.onPad = None
        self.cursors = []
        self.ammount_cursors = 0
        self.good_cursors = []
        self.name = "RecognizerPadSwipe"
        self.maxSpace = 100
        self.minMoved = 20
        self.time = 4
        self.cPos = None
   

    @newHypothesis
    def EventNewAgent(self,Cursor):
        if Cursor.recycled:
            self.fail("Cursor is recycled")
        self.agent = self.MakePadSwipeAgent()
        self.onPad = Cursor.onPad
        self.agent.onPad = self.onPad
        self.agent.sid = Cursor.sid
        self.agent.cPos = Cursor.cPos
        self.agent.crPos = Cursor.crPos
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail("Noone interested")
        self.unregister_event(RecognizerCursorOnPad.newAgent)
        self.register_event(RecognizerCursorOnPad.newAgent,RecognizerPadSwipe.EventNewAgent2)
        self.register_event(Cursor.newCursor, RecognizerPadSwipe.NewCursor)
        
    def NewCursor(self,Cursor):
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerPadSwipe.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerPadSwipe.EventRemoveCursor)
        self.cursors.append(Cursor)
        self.acquire(Cursor)
        #self.ammount_cursors += 1
        
        
        

    def EventMoveCursor(self,Cursor):
        
        if not Cursor in self.good_cursors:
            if self.dist(Cursor.origin, Cursor.cPos) > self.minMoved:
                if self.is_close(Cursor):
                    self.good_cursors.append(Cursor)
        if len(self.good_cursors) == len(self.cursors) > 2:
            #for a in self._agentsAcquired:
            #   self.confirm(a)
            self.fail_all_others()
            try:
                self.unregister_event(RecognizerCursorOnPad.newAgent)
            except KeyError:
                pass
            self.complete()
            
            
    def EventRemoveCursor(self,Cursor):
        #self.ammount_cursors -=1
        if not Cursor in self.good_cursors:
            self.fail("irrelevant cursor")
        if not self.executed:
            self.fail("cursor removed before gesture")
        else:
            self.unregister_all()
            self.finish()
        #self.cancel_expire()
        self.cursors.remove(Cursor)
        self.good_cursors.remove(Cursor)
        
        
        
    @newHypothesis    
    def EventNewAgent2(self,Cursor):
        if Cursor.recycled:
            self.fail(cause ="Cursor is recycled")
        if not self.is_on_same(Cursor):
            self.fail(cause ="new Cursor is not on same pad")
        if not self.is_close(Cursor):    
            self.fail(cause ="new Cursor is far")
        self.register_event(Cursor.newCursor, RecognizerPadSwipe.NewCursor2)        
                  
    def NewCursor2(self,Cursor):
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerPadSwipe.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerPadSwipe.EventRemoveCursor)
        self.cursors.append(Cursor)
        self.acquire(Cursor)
        #self.ammount_cursors += 1



  
    def is_close(self,Cursor):
        for cur in self.cursors:
            if not cur == Cursor:
                if self.dist(cur.cPos,Cursor.cPos) < self.maxSpace:
                    return True
            
    def dist(self,a,b):
        dx,dy = (a[0]-b[0],a[1]-b[1])
        return math.sqrt(dx**2 + dy**2)


    def MakePadSwipeAgent(self):
        evts = ["newPadSwipe"]
        a = Agent(evts, self)
        return a


    def is_on_same(self, Cursor):
        if Cursor.onPad == self.onPad:
            return True

    def fail(self,cause):
        print "PadSwipe fails: %s" % (cause,)
        self.unregister_all()
        Recognizer.fail(self, cause)

            
    def execute(self):
        self.agent.onPad = self.onPad.fid
        self.fail_all_others()
        self.unregister_all()
        self.agent.newPadSwipe.call(self.agent)
        self.finish()
        

    def duplicate(self):
        d = self.get_copy()
        d.cPos = self.cPos
        d.onPad = self.onPad
        d.cursors = self.cursors[:]
        d.ammount_cursors = self.ammount_cursors
        d.good_cursors = self.good_cursors[:]
        return d

import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerPadSwipe)
