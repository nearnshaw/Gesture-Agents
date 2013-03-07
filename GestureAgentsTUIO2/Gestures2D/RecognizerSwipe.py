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

class RecognizerSwipe(Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.register_event(Tuio.Tuio2CursorEvents.newAgent,RecognizerSwipe.EventNewAgent)
        self.cursors = []
        self.ammount_cursors = 0
        self.good_cursors = []
        self.name = "RecognizerSwipe"
        self.maxSpace = 80
        self.minMoved = 30
        self.pos = None
        self.positions = []
        self.time = 30
        self.conf = False
        self._good_cursors = 0
        
   

    @newHypothesis
    def EventNewAgent(self,Cursor):
        if Cursor.recycled:
            self.fail("Cursor is recycled")
        self.agent = self.MakePadSwipeAgent()
        self.agent.sid = Cursor.sid
        self.agent.pos = Cursor.pos
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail("Noone interested")
        self.unregister_event(Tuio.Tuio2CursorEvents.newAgent)
        self.register_event(Cursor.newCursor, RecognizerSwipe.NewCursor)
        
    def NewCursor(self,Cursor):
        Cursor.origin = Cursor.pos
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerSwipe.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerSwipe.EventRemoveCursor)
        self.register_event(Tuio.Tuio2CursorEvents.newAgent,RecognizerSwipe.EventNewAgent2)
        #self.expire_in(self.time)
        self.cursors.append(Cursor)
        self.acquire(Cursor)
        #self.ammount_cursors += 1
        
        
        

    def EventMoveCursor(self,Cursor):
        self.get_pos()
        if self.conf == False:
            if not Cursor in self.good_cursors:
                if self.dist(Cursor.origin, Cursor.pos) > self.minMoved:
                    if self.is_close(Cursor):
                        self.good_cursors.append(Cursor)
            if len(self.good_cursors) > 2:
                #for a in self._agentsAcquired:
                #   self.confirm(a)
                self.fail_all_others()
                self.unregister_all()
                self.conf = True
                self.complete()
            
        else:
            self.agent.pos = self.positions[-1]
            self.agent.swipePos.call(self.agent)
            
    def EventRemoveCursor(self,Cursor):
        self.cancel_expire()
        #self.ammount_cursors -=1
        if self.conf == False:
            try:
                self.good_cursors.remove(Cursor)
                self.cursors.remove(Cursor)
            except:
                self.fail(cause="irrelevant cursor")
            if len(self.cursors) < 2 or len(self.good_cursors)<2:
                self.fail(cause = "not enough fingers on")
            self.unregister_event(Cursor.updateCursor)
            self.unregister_event(Cursor.removeCursor)
        else:
            try:
                self.good_cursors.remove(Cursor)
                self.cursors.remove(Cursor)
            except:
                None
            self.unregister_all()
            self.finish()

            
    @newHypothesis    
    def EventNewAgent2(self,Cursor):
        if Cursor.recycled:
            self.fail(cause ="Cursor is recycled")
        if not self.is_close(Cursor):    
            self.fail(cause ="new Cursor is far")
        self.register_event(Cursor.newCursor, RecognizerSwipe.NewCursor2)        
                  
    def NewCursor2(self,Cursor):
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerSwipe.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerSwipe.EventRemoveCursor)
        self.cursors.append(Cursor)
        self.acquire(Cursor)
        #self.ammount_cursors += 1



   
    
        




    def get_pos(self):
        av_posx = 0
        av_posy = 0
        for cur in self.cursors:
            av_posx += cur.pos[0]
            av_posy += cur.pos[1]
        self.positions.append((av_posx/len(self.cursors),av_posy/len(self.cursors)))        

    def send_pos(self):
        for pos in self.positions:
            self.agent.pos = pos
            self.agent.swipePos.call(self.agent)
  
    def is_close(self,Cursor):
        for cur in self.cursors:
            if not cur == Cursor:
                if self.dist(cur.pos,Cursor.pos) < self.maxSpace:
                    return True
            
    def dist(self,a,b):
        dx,dy = (a[0]-b[0],a[1]-b[1])
        return math.sqrt(dx**2 + dy**2)


    def MakePadSwipeAgent(self):
        evts = ["newSwipe", "swipePos"]
        a = Agent(evts, self)
        return a

   
    def fail(self, cause="Unknown"):
        try:
            self.unregister_all()
        except:
            None
        Recognizer.fail(self,cause)




            
    def execute(self):
        self.agent.pos = self.positions[0]
        self.agent.newSwipe.call(self.agent)
        self.send_pos()
        
        
        
        

    def duplicate(self):
        d = self.get_copy()
        d.pos = self.pos
        d.cursors = self.cursors
        #d.good_cursors = self.good_cursors
        #d.ammount_cursors = self.ammount_cursors
        return d

import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerSwipe)
