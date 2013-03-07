#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GestureAgents.Reactor as Reactor
from GestureAgents.Events import Event
from GestureAgents.Policy import PolicyRuleset

class Agent(object):
    """This class represents something that generates Events.
    
    When receiving an event with an Agent associated,
    call acquire to show your interest. If you are an 
    application, you may call complete directly.
    
    If you are a recognizer call complete when you have
    fully recognized a gesture. For symbolic gestures 
    this means at the end of the recognition. For continuous
    gestures, you may call complete directly instead of
    acquire, as you know that anything is ypur gesture.
    
    Whenever you feel that you don't need this agent
    anymore, call discard AS EARLY AS POSSIBLE.
    
    Recognizers must call these through their own helpers
    in the class Recognizer.
    """
    #Policy on whenever a confirmed recognizer can be failed by a new recognizer confirming
    completion_policy = PolicyRuleset()
    #Policy on whenever one gesture can be confirmed while another can be aquired (for instance when a continuous gesture can
    #finish another gesture to complete.
    compatibility_policy = PolicyRuleset()
    
    def __init__(self,eventnames,creator):
        """eventnames is a list of names that will become member events.
        creator is a class or instance with newAgent event to be called when recycling this agent."""
        self._recognizers_acquired = []
        self._recognizer_complete = None
        self.events = {}
        self.owners = [creator]
        self.name = str(creator)+" Agent"
        self.newAgent = creator.newAgent
        #is this agent having a confirmed recognizer?
        self.completed = False
        #is this agent recycled?
        self.recycled = False
        self.finished = False
        for ename in list(eventnames)+["finishAgent"]:
            self.events[ename]=Event()
            setattr(self,ename,self.events[ename])
        
    def acquire(self,Recognizer):
        "The recognizer is interested on this agent"
        #can we acquire even if there is someone confirmed?
        if Recognizer in self._recognizers_acquired:
            return True
        if self.completed and self.compatibility_policy.result(self._recognizer_complete,Recognizer) != True:
            return False
        else:
            self._recognizers_acquired.append(Recognizer)
            return True
    
    def finish(self):
        "The owner of the event will not generate events anymore"
        self.finished = True
        self.finishAgent(self)
            
    def discard(self,Recognizer):
        """The recognizer is no longer interested in this agent.
        This should occur after acquiring the agent. If it happens
        after confirming, the agent will be recycled."""
        if Recognizer == self._recognizer_complete:
            #import traceback
            #traceback.print_stack()
            self._recognizer_complete = None
            if self.completed and not self.finished:
                self.completed = False
                self.recycled = True
                #we have to fail all remaining subscribed recognizers
                for r in self._get_recognizers_subscribed()+self._recognizers_acquired:
                    r.safe_fail(cause="registered to an Agent being recycled")
                self.newAgent(self)
                
        elif Recognizer in self._recognizers_acquired:
            self._recognizers_acquired.remove(Recognizer)
            if self._can_confirm():
                self._recognizer_complete.confirm(self)
                self.completed = True
        
    
    def _can_confirm(self):
        "[internal] Decides if self._recognizer_complete can be confirmed"
        if not self._recognizer_complete: return False  #if there is no recognizer completed it can't be confirmed
        if self.completed: return False                 #if it's already confirmed it can't be confirmed
        if not self._recognizers_acquired: return True  #if there are no competitors acquired it can be confirmed
        for r in self._recognizers_acquired:            #if there is an incompatibility with any of the acquired competitors it can't be confirmed
            if self.compatibility_policy.result(self._recognizer_complete,r) != True \
            and self.compatibility_policy.result(r, self._recognizer_complete) != True:
                return False
        return True
        
    def _complete(self,Recognizer):
        "[internal] "
        if Recognizer is self._recognizer_complete:
            return
        # According to the policy we choose the best Recognizer
        #print "CCC", self, type(Recognizer), type(self._recognizer_complete)
        if self.completion_policy.result(self._recognizer_complete,Recognizer) == False:
            #Policy doesn't accept change
            Recognizer.safe_fail("Policy doesn't accept change on complete")
            return
        elif self._recognizer_complete:
            self._recognizer_complete.safe_fail("Displaced by another recognizer: "+str(Recognizer))
            self._recognizer_complete = None
            self.completed = False
        
        self._recognizer_complete = Recognizer
        if Recognizer in self._recognizers_acquired:
            self._recognizers_acquired.remove(Recognizer)
        #According to the policy we remove acquisitions
        if self._can_confirm():
            self._recognizer_complete.confirm(self)
            self.completed = True
            
    def complete(self,Recognizer):
        if Recognizer not in self._recognizers_acquired:
            self._recognizers_acquired.append(Recognizer)
        Reactor.run_after(lambda Recognizer=Recognizer, self=self: self._complete(Recognizer) )
    
    def is_someone_subscribed(self):
        for event in self.events.itervalues():
            if event.registered:
                return True
        return False
    
    def fail(self):
        "The Recognizer owner of this agent fails before really existing, so All the recognizers based on it must fail"
        if self.finished: return
        for r in self._get_recognizers_subscribed():
            r.safe_fail("Agent failed: "+repr(self))
    
    def _get_recognizers_subscribed(self):
        from GestureAgents.Recognizer import Recognizer
        return [r for r in set([rr[1] for event in self.events.itervalues() for rr in event.registered]) if isinstance(r,Recognizer)]
    
    def fail_all_others(self,winner):
        Reactor.run_after(lambda winner=winner,self=self: self._fail_all_others(winner))
                
    def _fail_all_others(self,winner):
        #assert(self._recognizer_complete is winner) we are all consenting adults here
        target = type(winner)
        #print "fail_all_others :",winner,"wants to fail",target
        for r in list(self._recognizers_acquired):
            if type(r) == target and r is not winner:
                #print "fail_all_others by",winner,":", r, "is target"
                r.safe_fail(cause="Fail all others by %s"%str(winner))
            else:
                #print "fail_all_others :", r, "is not target"
                pass
                
    def __repr__(self):
        return self.name

#default policies

@Agent.completion_policy.rule(-100)
def _accept_if_none(recognizer1,recognizer2):
    "Accept First"
    if recognizer1 == None:
        return True

@Agent.completion_policy.rule(-99)
def _accept_if_compatible(recognizer1,recognizer2):
    "Use compatibility_policy to accept completion one over another"
    if Agent.compatibility_policy.result(recognizer1,recognizer2) == True:
        return True
    
@Agent.compatibility_policy.rule(100)
def _never_accept(recognizer_confirmed,recognizer_acquiring):
    "Never accept acquire when confirmed"
    return False
