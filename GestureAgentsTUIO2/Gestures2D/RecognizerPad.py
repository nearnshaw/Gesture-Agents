#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GestureAgentsTUIO2.Tuio2 as Tuio
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
from  .shadow import shadowPad
import math


#NECESITO COORDENADAS RELATIVAS DENTRO DEL PAD, INFO DE TAMAÑO, ANGULO, ETC

class RecognizerPad(Recognizer):
   
    newAgent = Event()
    #padsUp = None
    #fidIDs = [0, 1, 2, 3]

    def __init__(self):
        Recognizer.__init__(self)
        self.figureEvents = Tuio.Tuio2FigureEvents 
        self.register_event(self.figureEvents.newAgent,RecognizerPad.EventNewAgent)
        self.maxd = 10
        self.time = 1
        self.fid = None
##        self.corner1 = None
##        self.corner2 = None
##        self.corner3 = None
##        self.corner4 = None
##        self.c1 = (-2.6,2.9)
##        self.c2 = (-13.6,2.9)
##        self.c3 = (-13.6,-8.1)
##        self.c4 = (-2.6,-8.1)
        self.fidIDs = (0, 1, 2, 3)
        self.name = "RecognizerPad"
        self.shadow = shadowPad(self)

    
    @newHypothesis
    def EventNewAgent(self,Figure):
        if Figure.recycled:
            self.fail("Figure is recycled")
        elif not self.is_pristine():
            self.safe_fail("already taken")
        self.unregister_event(self.figureEvents.newAgent)
        self.agent = self.make_PadAgent()
        self.fid = Figure.figure.fid   
        self.agent.fid = self.fid
        #if self.fid not in RecognizerPad.fidIDs: self.fail("Not a Pad")
        if self.fid not in self.fidIDs: self.fail("Not a Pad")
        #RecognizerPad.fidIDs.remove(self.fid)
        self.update(Figure)
        self.sendPos(Figure)
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail("Noone interested")
        else:
            self.register_event(Figure.newFigure,RecognizerPad.EventNewFigure)
           
        


    def EventNewFigure(self,Figure):
        self.unregister_event(Figure.newFigure)
        self.register_event(Figure.updateFigure,RecognizerPad.EventMoveFigure)
        self.register_event(Figure.removeFigure,RecognizerPad.EventRemoveFigure)
        self.acquire(Figure)
        self.complete()

    
    def EventMoveFigure(self,Figure):
        self.update(Figure)
        self.sendPos(Figure)
        self.agent.updatePad.call(self.agent) 

    
    def EventRemoveFigure(self,Figure):
        #RecognizerPad.fidIDs.append(self.fid)
        self.unregister_event(Figure.updateFigure)
        self.unregister_event(Figure.removeFigure)
        self.register_event(self.figureEvents.newAgent,RecognizerPad.EventNewAgent2)
        self.expire_in(self.time)
       
        
    def fail(self, cause="Unknown"):
        if self.agent:
            self.agent.removePad.call(self.agent)
        Recognizer.fail(self,cause)
        self.unregister_all()

               
    def EventNewAgent2(self,Figure):
        #esto va aca?????
        #if Figure.recycled:
        #    self.fail("Figure is recycled")
        if not Figure.recycled and Figure.figure.fid == self.fid:
            self.acquire(Figure)
            self.fail_all_others()
            #CARLES: cancel expire solo cuando es el mismo fid
            self.cancel_expire()
            #if self.fid in RecognizerPad.fidIDs:
                #RecognizerPad.fidIDs.remove(self.fid)
        #CARLES: no hace falta, si es fid diferente ignoramos.
        #else:
        #    self.fail("not the same pad")
        try:
            self.unregister_event(self.figureEvents.newAgent)
        except:
            pass
        self.register_event(Figure.newFigure,RecognizerPad.EventNewFigure2)
        
    def EventNewFigure2(self,Figure):
        self.unregister_event(Figure.newFigure)
        self.update(Figure)
        self.sendPos(Figure)
        self.register_event(Figure.updateFigure,RecognizerPad.EventMoveFigure)
        self.register_event(Figure.removeFigure,RecognizerPad.EventRemoveFigure)
    
    

        
                
    def execute(self):
        self.agent.newPad.call(self.agent)
      

     
    def update(self, Pad):
        self.px = Pad.pos[0]    
        self.py = Pad.pos[1]   
        self.roll = Pad.figure.roll      
##        corner1cm = tablePos(self.c1[0], self.c1[1], self.pxcm, self.pycm, self.pzcm, self.yaw, self.pitch, self.roll)
##        corner2cm = tablePos(self.c2[0], self.c2[1], self.pxcm, self.pycm, self.pzcm, self.yaw, self.pitch, self.roll)
##        corner3cm = tablePos(self.c3[0], self.c3[1], self.pxcm, self.pycm, self.pzcm, self.yaw, self.pitch, self.roll)
##        corner4cm = tablePos(self.c4[0], self.c4[1], self.pxcm, self.pycm, self.pzcm, self.yaw, self.pitch, self.roll)
##        self.corner1 = (round((corner1cm[0]*(self.mesa_camZ*self.ratioX/self.pz)),2)), (round((corner1cm[1]*(self.mesa_camZ*self.ratioY/self.pz)),2))
##        self.corner2 = (round((corner2cm[0]*(self.mesa_camZ*self.ratioX/self.pz)),2)), (round((corner2cm[1]*(self.mesa_camZ*self.ratioY/self.pz)),2))
##        self.corner3 = (round((corner3cm[0]*(self.mesa_camZ*self.ratioX/self.pz)),2)), (round((corner3cm[1]*(self.mesa_camZ*self.ratioY/self.pz)),2))
##        self.corner4 = (round((corner4cm[0]*(self.mesa_camZ*self.ratioX/self.pz)),2)), (round((corner4cm[1]*(self.mesa_camZ*self.ratioY/self.pz)),2))
     
    def sendPos(self, Pad):
        self.agent.px = Pad.pos[0]
        self.agent.py = Pad.pos[1]
        self.agent.roll = self.roll


       
    
    def duplicate(self):
        d = self.get_copy()
        d.shadow = shadowPad(d)
        return d
        
    def make_PadAgent(self):
        a = Agent(("newPad","updatePad","removePad",),self)
        return a

import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerPad)
