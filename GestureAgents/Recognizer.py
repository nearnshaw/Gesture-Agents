#!/usr/bin/env python
# -*- coding: utf-8 -*-

from GestureAgents.Events import Event, EventClient
import GestureAgents.Reactor as Reactor

try:
    from classlogger import ClassLogged
except ImportError:
    ClassLogged = type

class RecognizerFailedException(Exception):
    pass

class Recognizer(EventClient):
    """Class to be derived to make a Gesture Recognizer
    
    Most of the methods of Recognizer are meant to be called
    from a derived class on itself. There are, however some
    methods that can be called from outside.
    
    Methods:
        
        General info:
            is_pristine
            is_someone_interested
            
        Reserved to be called by Agent:
            safe_fail
            confirm 
    
        Reserved to be called by a subclass:
            finish
            unregister_all
            fail
            acquire
            complete
            copy_to
            fail_all_others
            expire_in
            cancel_expire
    
    Attributes:
        agent: To be filled with the agent representing the gesture
        
    """
    
    __metaclass__ = ClassLogged
    
    def __init__(self):
        EventClient.__init__(self)
        self._agentsAcquired = []
        self._agentsConfirmed = []
        #TODO: replace self.failed with self.died and self.failed to indicate different things?
        self.failed = False
        self.agent = None
        self.executed = False
        #self.parent = False
    
    def finish(self):
        assert(not self.failed)
        self.failed=True
        self.unregister_all()
        #we die but not fail
        #assert(not self._agentsAcquired) #TODO: arreglar això
        for a in self._agentsConfirmed:
            a.discard(self)
        self.agent.owners.remove(self) #removing a complex reference cycle preventing gc
        self.agent.finish()
        self.agent = None
        
    def unregister_all(self):
        EventClient.unregister_all(self)
        Reactor.cancel_schedule(self)
        
    def fail(self,cause="Unknown"):
        #TODO: relacionat amb el finish vs confirm race
        #assert(not self.failed)
        if self.failed:
            return
        self.failed=True
        for a in self._agentsAcquired+self._agentsConfirmed:
            a.discard(self)
        self._agentsAcquired = []
        self._agentsConfirmed = []
        self.unregister_all()
        # we have to fail only if we are the solely owner of self.agent.
        if self.agent:
            self.agent.owners.remove(self)
            if not self.agent.owners:
                self.agent.fail()
            self.agent = None
        raise RecognizerFailedException()
    
    def acquire(self,agent):
        #TODO: define a way to release agents also
        if self.failed: return 
        if agent.acquire(self):
            self._agentsAcquired.append(agent)
        else:
            self.fail("Acquire failed")
            
    def complete(self):
        if self.failed: return
        for a in self._agentsAcquired:
            a.complete(self)
            
    def confirm(self,agent):
        if self.failed: return
        self._agentsAcquired.remove(agent)
        self._agentsConfirmed.append(agent)
        if not self._agentsAcquired:
            self.execute()
            self.executed = True
        
    def get_copy(self,*iargs,**ikwargs):
        if self.failed: print "WARNING: copying a failed Recognizer!"
        if self._agentsConfirmed and not self.executed: print "WARNING: copying a Recognizer in confirmation!"
        d = self.__class__(*iargs,**ikwargs)
        d.unregister_all()
        for a in self._agentsAcquired:
            d.acquire(a)
        EventClient.copy_to(self,d)
        Reactor.duplicate_instance(self,d)
        #we duplicate agents
        if self.agent:
            d.agent = self.agent
            self.agent.owners.append(d)
        d.executed = self.executed
        #d.parent = self.parent
        return d
    
    def is_pristine(self):
        return ( len(self._agentsAcquired) + len(self._agentsConfirmed) ) == 0
    
    def is_someone_interested(self):
        for f,i in self.newAgent.registered:
            if not isinstance(i,Recognizer):
                return True
            elif i.is_someone_interested():
                return True
        return False
    
    def fail_all_others(self):
        for a in self._agentsAcquired+self._agentsConfirmed:
            a.fail_all_others(self)
    
    def safe_fail(self,cause="Unknown"):
        try:
            self.fail(cause=cause)
        except RecognizerFailedException:
            pass
    
    def expire_in(self,s):
        l = lambda self: self.safe_fail(cause="Timeout")
        Reactor.schedule_after(s,self,l)
    
    def cancel_expire(self):
        Reactor.cancel_schedule(self)
        
def newHypothesis(f):
    "Decorator to create a new hypothesis every time that is called"
    def newHipothesisAndRun(self,*args,**kwargs):
        if self.is_someone_interested():
            d = self.duplicate()
            try:
                self.log("Duplicating to %s-%d" % (d._ClassLogged_name,d._instance_number_))
                d.log("Duplicated from %s-%d" % (self._ClassLogged_name,self._instance_number_))
            except AttributeError:
                pass
            f(self,*args,**kwargs)
        elif not self.is_pristine():
            self.safe_fail("Noone interested")
    newHipothesisAndRun.__name__ = "[new hypothesis] %s" % (f.__name__,)
    return newHipothesisAndRun
    
    
from GestureAgents.Agent import Agent
#policies for comparison between Recognizers

@Agent.completion_policy.rule(100)
def last_to_enter_wins(recognizer1,recognizer2):
    "Last to enter wins"
    return True

@Agent.completion_policy.rule(-50)
def completed_win(recognizer1,recognizer2):
    "Completed win"
    if recognizer1.executed and not recognizer2.executed:
        return False
    if not recognizer1.executed and recognizer2.executed:
        return True

@Agent.completion_policy.rule(-49)
def more_agents_win(recognizer1,recognizer2):
    "Wins the recognizer with more agents"
    la1 = len(recognizer1._agentsAcquired)
    lr1 = len(recognizer1._agentsConfirmed)
    la2 = len(recognizer2._agentsAcquired)
    lr2 = len(recognizer2._agentsConfirmed)
    if la1+lr1 > la2+lr2:
        return False
    elif la1+lr1 < la2+lr2:
        return True

