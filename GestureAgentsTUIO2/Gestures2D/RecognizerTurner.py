#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GestureAgentsTUIO2.Tuio2 as Tuio
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
import math


#NECESITO COORDENADAS RELATIVAS DENTRO DEL PAD, INFO DE TAMAÑO, ANGULO, ETC

class RecognizerTurner(Recognizer):
   
    newAgent = Event()
    def __init__(self):
        self.pad = None
        Recognizer.__init__(self)
        self.figureEvents = Tuio.Tuio2FigureEvents
        self.register_event(self.figureEvents.newAgent,RecognizerTurner.EventNewAgent)
        self.origin = None
        self.px = None
        self.py = None
        self.pz = None
        self.fid = None
        self.figure = None
        self.down = False
        self.floor = 1280
        self.margin = 260
        self.fidIDs = (3,4,5,6,7,8)
        self.angle = 0
	self.time = 1
    
    @newHypothesis
    def EventNewAgent(self,Figure):
        self.fid = Figure.figure.fid   
        if self.fid not in self.fidIDs: self.fail("Not a turner")
        print "hay un Turner"
        if Figure.recycled:
            self.fail("Figure is recycled")
        self.agent = self.make_TurnerAgent()      
        self.agent.fid = self.fid
        self.figure = Figure
        self.pz = Figure.figure.z
        self.px = Figure.pos[0]
        self.py = Figure.pos[1]
        self.angle = self.figure.figure.roll
        self.sendPos()
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail("Noone interested")
        else:
            self.unregister_event(self.figureEvents.newAgent)
            self.register_event(Figure.newFigure,RecognizerTurner.EventNewFigure)
        
    def EventNewFigure(self,Figure):
        self.instance = Figure
        self.unregister_event(Figure.newFigure)
        self.register_event(Figure.updateFigure,RecognizerTurner.EventMoveFigure)
        self.register_event(Figure.removeFigure,RecognizerTurner.EventRemoveFigure)
        self.acquire(Figure)
        self.complete()
       

    
    def EventMoveFigure(self,Figure):
        self.px = Figure.pos[0]
        self.py = Figure.pos[1]
        self.pz = Figure.figure.z
        self.angle = self.figure.figure.roll
        self.sendPos()
        self.agent.updateTurner.call(self.agent)
        if self.pz < self.floor + self.margin:
            self.down = True
        else: self.down = False

    
    def EventRemoveFigure(self,Figure):
        self.agent.removeTurner.call(self.agent)
        self.register_event(self.figureEvents.newAgent,RecognizerTurner.EventNewAgent2)
        self.expire_in(self.time)


    def fail(self, cause="Unknown"):
        try:
            self.unregister_all()
        except:
            None
        Recognizer.fail(self,cause)



    @newHypothesis
    def EventNewAgent2(self,Figure):
        self.cancel_expire()
        #esto va aca?????
        if Figure.recycled:
            self.fail("Figure is recycled")
        if Figure.figure.fid == self.fid:
            self.acquire(Figure)
            self.fail_all_others()
        self.figure = Figure
        self.pz = Figure.figure.z
        self.px = Figure.pos[0]
        self.py = Figure.pos[1]
        self.angle = self.figure.figure.roll
        self.sendPos()
        self.unregister_event(self.figureEvents.newAgent)
        self.register_event(Figure.newFigure,RecognizerTurner.EventNewFigure2)
        
    def EventNewFigure2(self,Figure):
        self.instance = Figure
        self.unregister_event(Figure.newFigure)
        self.register_event(Figure.updateFigure,RecognizerTurner.EventMoveFigure)
        self.register_event(Figure.removeFigure,RecognizerTurner.EventRemoveFigure)
        self.acquire(Figure)




            
    def execute(self):
        self.angle = self.figure.figure.roll
        self.sendPos()
        self.agent.fid = self.fid
        self.agent.newTurner.call(self.agent)

                


    def sendPos(self):
        self.agent.roll = self.angle
        self.agent.px = self.px
        self.agent.py = self.py
        self.agent.pz = self.pz

    
    def duplicate(self):
        d = self.get_copy()
        d.origin = self.origin
        d.fid = self.fid
        d.figure = self.figure
        d.angle = self.angle

 
        return d
        
    def make_TurnerAgent(self):
        a = Agent(("newTurner","updateTurner","removeTurner",),self)
        return a

import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerTurner)
