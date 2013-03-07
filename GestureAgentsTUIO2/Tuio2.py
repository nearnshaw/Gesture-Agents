#!/usr/bin/env python
# -*- coding: utf-8 -*-

from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
import traceback
import sys

class Tuio2CursorEvents:
    newAgent = Event()
    #newSID = 0

class Tuio2HandEvents:
    newAgent = Event()

class Tuio2FigureEvents:
    newAgent = Event()

class Tuio2AgentGenerator(object):
    def __init__(self,screensize):
        self.curagents = {}
        self.figagents = {}
        self.screensize = screensize
    
    def newCur(self,finger):
        curagent = self.makeCursorAgent()
        self.curagents[finger.SESSION_ID] = curagent
        curagent.sid = int(finger.SESSION_ID)
        self._TransferCurInfo(curagent,finger)
        curagent.newAgent(curagent)
        curagent.newCursor(curagent)
            

    def updateCur(self,finger):
        curagent = self.curagents[finger.SESSION_ID]
        self._TransferCurInfo(curagent,finger)
        curagent.updateCursor(curagent)

    def removeCur(self,finger):
        curagent = self.curagents[finger.SESSION_ID]
        self._TransferCurInfo(curagent,finger)
        curagent.removeCursor(curagent)
        del self.curagents[finger.SESSION_ID]
    
    def newFig(self,figure):
        figagent = self.makeFigureAgent()
        self.figagents[figure.sid] = figagent
        self._TransferFigInfo(figagent,figure)
        figagent.newAgent(figagent)
        figagent.newFigure(figagent)

    def updateFig(self,figure):
        figagent = self.figagents[figure.sid]
        self._TransferFigInfo(figagent,figure)
        figagent.updateFigure(figagent)

    def removeFig(self,figure):
        figagent = self.figagents[figure.sid]
        self._TransferFigInfo(figagent,figure)
        figagent.removeFigure(figagent)
        del self.figagents[figure.sid]

    def debug(self,cosa):
        print cosa
        print dir(cosa)

    def _TransferCurInfo(self,cur,finger):
        cur.finger = finger
        #cur.sid = finger.SID
        cur.pos = (finger.X*self.screensize[0],finger.Y*self.screensize[1])

    def _TransferFigInfo(self,fig,figure):
        fig.figure = figure
        fig.pos = (figure.x*self.screensize[0],figure.y*self.screensize[1])
      
    @staticmethod
    def makeCursorAgent():
        evts = ('newCursor','updateCursor','removeCursor')
        return Agent(evts,Tuio2CursorEvents)
    
    @staticmethod
    def makeFigureAgent():
        evts = ('newFigure','updateFigure','removeFigure')
        return Agent(evts,Tuio2FigureEvents)


from GestureAgentsTUIO.Tuio import TuioCursorEvents, TuioFigureEvents
from GestureAgents.Recognizer import Recognizer, newHypothesis
import GestureAgentsPygame.Screen as Screen

class RecognizerTuio_Tuio2(Recognizer):
    newAgent = Tuio2CursorEvents.newAgent
    def __init__(self):
        Recognizer.__init__(self)
        self.generator = Tuio2AgentGenerator(Screen.size)
        self.register_event(TuioCursorEvents.newAgent, RecognizerTuio_Tuio2.EventnewAgentCur)
        self.register_event(TuioFigureEvents.newAgent, RecognizerTuio_Tuio2.EventnewAgentFig)
        self.finger = None
        
    @newHypothesis
    def EventnewAgentCur(self,TUIOCursor):
        if TUIOCursor.recycled:
            self.fail("Agent Recycled")
        self.unregister_all()
        self.register_event(TUIOCursor.newCursor,RecognizerTuio_Tuio2.EventNewCursor)
        self.register_event(TUIOCursor.updateCursor,RecognizerTuio_Tuio2.EventUpdateCursor)
        self.register_event(TUIOCursor.removeCursor,RecognizerTuio_Tuio2.EventRemoveCursor)
    
    @newHypothesis
    def EventnewAgentFig(self,TuioFig):
        if TuioFig.recycled:
            self.fail("Agent Recycled")
        self.unregister_all()
        self.register_event(TuioFig.newFigure,RecognizerTuio_Tuio2.EventNewFigure)
        self.register_event(TuioFig.updateFigure,RecognizerTuio_Tuio2.EventUpdateFigure)
        self.register_event(TuioFig.removeFigure,RecognizerTuio_Tuio2.EventRemoveFigure)
    
    def EventNewCursor(self,TUIOCursor):
        class Faketuio2Finger:
            pass
        self.finger = Faketuio2Finger()
        self.copy_tcur2t2cur(TUIOCursor, self.finger)
        self.generator.newCur(self.finger)
    
    def EventUpdateCursor(self,TUIOCursor):
        self.copy_tcur2t2cur(TUIOCursor, self.finger)
        self.generator.updateCur(self.finger)
    
    def EventRemoveCursor(self,TUIOCursor):
        self.copy_tcur2t2cur(TUIOCursor, self.finger)
        self.generator.removeCur(self.finger)
        self.unregister_all()
        #and fail?
    
    def EventNewFigure(self,TuioFig):
        class Faketuio2Figure:
            pass
        self.finger = Faketuio2Figure()
        self.copy_tfig2t2fig(TuioFig, self.finger)
        self.generator.newFig(self.finger)
    
    def EventUpdateFigure(self,TuioFig):
        self.copy_tfig2t2fig(TuioFig, self.finger)
        self.generator.updateFig(self.finger)
    
    def EventRemoveFigure(self,TuioFig):
        self.copy_tfig2t2fig(TuioFig, self.finger)
        self.generator.removeFig(self.finger)
        self.unregister_all()
        #and fail?
    
    def duplicate(self):
        d = self.get_copy()
        return d
    
    @staticmethod
    def copy_tcur2t2cur(tcur,t2cur):
        correspondances = {
                           "sessionid":"SESSION_ID",
                           "xpos":"X",
                           "ypos":"Y",
                           "xmot":"",
                           "ymot":"",
                           "mot_accel":"",
                           }
        for m1,m2 in correspondances.iteritems():
            if m2:
                setattr(t2cur,m2,getattr(tcur,m1,0))
                
    @staticmethod
    def copy_tfig2t2fig(tfig,t2fig):
        correspondances = {
                           "sessionid":"sid",
                           "xpos":"x",
                           "ypos":"y",
                           "xmot":"",
                           "ymot":"",
                           "mot_accel":"",
                           "id":"fid",
                           "mot_speed":"",
                           "rot_speed":"",
                           "rot_accel":"",
                           "z":"z",
                           "yaw":"yaw",
                           "pitch":"pitch",
                           "angle":"roll",
                           }
        for m1,m2 in correspondances.iteritems():
            if m2:
                setattr(t2fig,m2,getattr(tfig,m1,0))
    
import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerTuio_Tuio2)