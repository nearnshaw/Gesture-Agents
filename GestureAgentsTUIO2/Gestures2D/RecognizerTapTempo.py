#!/usr/bin/env python
# -*- coding: utf-8 -*-

from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgentsTUIO2.Gestures2D.RecognizerTap import RecognizerTap
from GestureAgents.Agent import Agent
import math
import datetime

def to_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10.0**6

class RecognizerTapTempo(Recognizer):
    newAgent = Event()
    rtotal = 0
    def __init__(self):
        Recognizer.__init__(self)
        self.agent = None
        self.firstap = None
        self.secondtap = None
        self.thirdtap = None
        self.fourthtap = None
        self.register_event(RecognizerTap.newAgent,RecognizerTapTempo.EventNewAgent)
        self.time = 1
        self.maxd = 15
        self.name = "RecognizerTapTempo %d" % RecognizerTapTempo.rtotal
        RecognizerTapTempo.rtotal+=1
        self.tapTime = []
        self.tempo = None
        self.interval = None
        self.start = datetime.datetime.now()
        
    @newHypothesis
    def EventNewAgent(self,Tap):
        self.agent = self.make_TapTempoAgent()
        self.agent.pos = Tap.pos
	self.agent.sid = Tap.sid
        self.newAgent.call(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail(cause="Noone Interested")
        else:
            self.unregister_event(RecognizerTap.newAgent)
            self.register_event(Tap.newTap,RecognizerTapTempo.FirstTap)
        
    def FirstTap(self,Tap):
        self.start = datetime.datetime.now()
        self.tapTime.append(0)
        self.firstap = Tap
        self.unregister_event(Tap.newTap)
        self.register_event(RecognizerTap.newAgent,RecognizerTapTempo.EventNewAgent2)
        self.expire_in(self.time)
        self.acquire(Tap)
    
    
    @newHypothesis
    def EventNewAgent2(self,Tap):
        if self.dist(Tap.pos,self.firstap.pos) > self.maxd:
            self.fail(cause="Max distance")
        else:
            self.unregister_event(RecognizerTap.newAgent)
            self.register_event(Tap.newTap,RecognizerTapTempo.SecondTap)
        
    def SecondTap(self,Tap):
        self.interval = to_seconds(datetime.datetime.now() - self.start)
        self.tapTime.append(self.interval)
        self.secondtap = Tap
        self.unregister_event(Tap.newTap)
        self.cancel_expire()
        self.acquire(Tap)
        self.register_event(RecognizerTap.newAgent,RecognizerTapTempo.EventNewAgent3)
        self.expire_in(self.interval*1.7)
        

    @newHypothesis
    def EventNewAgent3(self,Tap):
        self.cancel_expire()
        if self.dist(Tap.pos,self.firstap.pos) > self.maxd:
            self.fail(cause="Max distance")
        else:
            self.unregister_event(RecognizerTap.newAgent)
            self.register_event(Tap.newTap,RecognizerTapTempo.ThirdTap)

    def ThirdTap(self,Tap):
        self.tapTime.append(to_seconds(datetime.datetime.now() - self.start))
        self.thirdtap = Tap
        if (self.tapTime[2] - self.tapTime[1]) < self.interval*0.3:
            self.fail() 
        self.unregister_event(Tap.newTap)
        self.acquire(Tap)
        self.register_event(RecognizerTap.newAgent,RecognizerTapTempo.EventNewAgent4)
        self.expire_in(self.interval*1.7)


    @newHypothesis
    def EventNewAgent4(self,Tap):
        self.cancel_expire()
        if self.dist(Tap.pos,self.firstap.pos) > self.maxd:
            self.fail(cause="Max distance")
        else:
            self.unregister_event(RecognizerTap.newAgent)
            self.register_event(Tap.newTap,RecognizerTapTempo.FourthTap)

    def FourthTap(self,Tap):
        print "llego"
        self.tapTime.append(to_seconds(datetime.datetime.now() - self.start))
        self.fourthtap = Tap
        if (self.tapTime[3] - self.tapTime[2]) < self.interval*0.3:
            self.fail() 
        self.unregister_event(Tap.newTap)
        self.acquire(Tap)
        self.tempo = self.calculateTime()
        self.agent.tempo = self.tempo
        self.fail_all_others()
        self.complete()

    def calculateTime(self):
        interval = ((self.tapTime[1] - self.tapTime[0]) + (self.tapTime[2] - self.tapTime[0]) + (self.tapTime[3] - self.tapTime[0]) )/3 
        return interval
 
    def execute(self):
        #print "I execute",self
        self.agent.interval = str(self.interval)
        #print self.agent.newDoubleTap.registered
        self.agent.newTapTempo(self.agent)
        self.finish()
    
    def duplicate(self):
        d = self.get_copy()
        d.firstap = self.firstap
        d.secondtap = self.secondtap
        d.thirdtap = self.thirdtap
        d.fourthtap = self.fourthtap
        d.tapTime = list(self.tapTime)
        d.tempo = self.tempo
        d.interval = self.interval
        
        return d
    
    def fail(self, cause="Unknown"):
        print "RecognizerTapTempo(",self,") fail, cause="+cause
        #raise Exception("RecognizerDoubleTap fail")
        Recognizer.fail(self,cause)
    
    @staticmethod
    def dist(a,b):
        dx,dy = (a[0]-b[0],a[1]-b[1])
        return math.sqrt(dx**2 + dy**2)
    
    def make_TapTempoAgent(self):
        a =  Agent(("newTapTempo",),self)
        return a
        
    def __repr__(self):
        return self.name
        
import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerTapTempo)

