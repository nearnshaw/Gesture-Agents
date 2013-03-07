#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GestureAgentsTUIO2.Tuio2 as Tuio
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
import math


#NECESITO COORDENADAS RELATIVAS DENTRO DEL PAD, INFO DE TAMAÑO, ANGULO, ETC

class RecognizerInstrument(Recognizer):
   
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.figureEvents = Tuio.Tuio2FigureEvents
        self.register_event(self.figureEvents.newAgent,RecognizerInstrument.EventNewAgent)
        self.origin = None
        self.px = None
        self.py = None
        self.pz = None
        self.fid = None
        self.fidIDs = (11,12,13,14)
        self.angle = 0
        self.figure = None
	self.name = "RecognizerInstrument"
    
    @newHypothesis
    def EventNewAgent(self,Figure):
        if Figure.recycled:
            self.fail("Figure is recycled")
        self.fid = Figure.figure.fid
        if self.fid not in self.fidIDs: self.fail("Not an instrument")
        print "hay un instrument"
        self.agent = self.make_InstrumentAgent()
        self.agent.fid = self.fid
        self.figure = Figure
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail("Noone interested")
        else:
            self.unregister_event(self.figureEvents.newAgent)
            self.register_event(Figure.newFigure,RecognizerInstrument.EventNewFigure)
        
    def EventNewFigure(self,Figure):
        self.instrument = Figure
        self.unregister_event(Figure.newFigure)
        self.register_event(Figure.updateFigure,RecognizerInstrument.EventMoveFigure)
        self.register_event(Figure.removeFigure,RecognizerInstrument.EventRemoveFigure)
        self.px = Figure.pos[0]
        self.py = Figure.pos[1]
        self.pz = Figure.figure.z
        self.angle = Figure.roll
        self.acquire(Figure)
        self.sendPos(Figure)
        self.complete()

    
    def EventMoveFigure(self,Figure):
        self.px = Figure.pos[0]
        self.py = Figure.pos[1]
        self.pz = Figure.figure.z
        self.angle = self.figure.figure.roll
        self.sendPos(Figure)
        self.agent.moveInstrument.call(self.agent)
        

    
    def EventRemoveFigure(self,Figure):
        self.unregister_event(Figure.updateFigure)
        self.unregister_event(Figure.removeFigure)
        self.agent.removeInstrument.call(self.agent)
        self.finish()
            
    def execute(self):
        self.angle = self.figure.figure.roll
        self.sendPos()
        #self.agent.fid = self.fid
        self.agent.newInstrument.call(self.agent)


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
        
    def make_InstrumentAgent(self):
        a = Agent(("newInstrument","updateInstrument","removeInsrument",),self)
        return a

import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerInstrument)
