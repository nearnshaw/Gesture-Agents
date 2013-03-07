# -*- coding: cp1252 -*-
import GestureAgentsTUIO2.Tuio2 as Tuio
from GestureAgents.Recognizer import Recognizer, newHypothesis
from GestureAgents.Events import Event
from GestureAgents.Agent import Agent
from GestureAgentsTUIO2.Gestures2D.RecognizerPad import RecognizerPad
from GestureAgentsTUIO2.Gestures2D.RecognizerTap import RecognizerTap
from math import sqrt, fabs

#DOBLE SISTEMA DE COORDENADAS: ABSOLUTAS Y RELATIVAS AL PAD

class RecognizerCursorOnPad(Recognizer):
    newAgent = Event()
    def __init__(self):
        Recognizer.__init__(self)
        self.register_event(RecognizerPad.newAgent,RecognizerCursorOnPad.EventNewPAgent)
        self.onPad = None
        self.fid = None
        self.cursor = None
        self.cPos = None
        self.cPoscm = None
        self.crPos = None
        self.crPoscm = None
        self.origin = None
        self.has_cur = False
        #self.has_pad = True
        #self.mesa_camZ = 0.0042
        self.mesa_camZ = 1280
        self.ratioX = 38.3
        self.ratioY = 25.5
        self.ratioZ = 26
        #self.ratioZ = 12500  #este se trata inverso a los otros dos
        self.px = None   
        self.py = None    
        self.pz = None
        self.pxcm = None   
        self.pycm = None    
        self.pzcm = None
        self.yaw = None       
        self.pitch = None    
        self.roll = None
        self.maxSpace = 40
        self.time = 1

        
        #self.radius = 240    # esto slo temporal hasta tener como calcular onPad


        
    @newHypothesis
    def EventNewPAgent(self,Figure):
        if Figure.recycled:
            self.fail("Figure is recycled")
        self.unregister_event(RecognizerPad.newAgent)
        self.onPad = Figure
        self.fid = self.onPad.fid
        self.getPadPos()
        self.register_event(Figure.newPad, RecognizerCursorOnPad.newPad)
        self.register_event(Tuio.Tuio2CursorEvents.newAgent,RecognizerCursorOnPad.EventNewTAgent)
        

    def newPad(self,Figure):
        self.unregister_event(Figure.newPad)
        self.register_event(Figure.updatePad, RecognizerCursorOnPad.UpdatePad)
        self.register_event(Figure.removePad, RecognizerCursorOnPad.RemovePad)
        
    def UpdatePad(self, Figure):
        self.getPadPos()
        if self.has_cur == True:
            self.crPos = self.relPos()
            self.sendPos(self.cursor)
            self.agent.updateCursor.call(self.agent)

        
    def RemovePad(self, Figure):
        try:
            self.unregister_event(Figure.updatePad)
            self.unregister_event(Figure.removePad)
            self.unregister_event(Tuio.Tuio2CursorEvents.newAgent)
        except:
            print "error de unregister en remove pad"
        if self.has_cur == True:
            self.EventRemoveCursor(self.cursor)

    @newHypothesis
    def EventNewTAgent(self,Cursor):
        if Cursor.recycled:
            self.fail("Cursor is recycled")
        self.unregister_event(Tuio.Tuio2CursorEvents.newAgent)
        self.cPos = Cursor.pos
        self.origin = Cursor.pos
        self.crPos = self.relPos()
        #si anda proyectar el pad a 2d por ahi mejor hacer collision detection para is_on antes de relpos
        if not self.is_on(self.crPoscm):
            self.fail(cause= "not on pad")
        self.agent = self.MakeCursorOnPadAgent()
        self.sendPos(Cursor)
        self.agent.onPad = self.onPad
        self.agent.fid = self.fid
        self.agent.sid = Cursor.sid
        self.newAgent(self.agent)
        if not self.agent.is_someone_subscribed():
            self.fail("Noone interested")
        self.register_event(Cursor.newCursor, RecognizerCursorOnPad.NewCursor)
        
    def NewCursor(self,Cursor):
        if Cursor.recycled:
            self.fail("Cursor is recycled")
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerCursorOnPad.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerCursorOnPad.EventRemoveCursor)
        self.acquire(Cursor)
        self.cursor = Cursor
        self.has_cur = True
        #self.acquire(self.onPad)
        self.complete()
         
        
    def EventMoveCursor(self,Cursor):
        self.cPos = Cursor.pos
        self.crPos = self.relPos()
        self.sendPos(Cursor)
        self.agent.updateCursor.call(self.agent)
        
            
    def EventRemoveCursor(self, Cursor):
        self.has_cur = False
        self.agent.removeCursor.call(self.agent)
        self.register_event(Tuio.Tuio2CursorEvents.newAgent,RecognizerCursorOnPad.EventNewTAgent2)
        self.has_cur = False
        self.expire_in(self.time)
        
        


    @newHypothesis
    def EventNewTAgent2(self,Cursor):
        self.cancel_expire()
        if Cursor.recycled:
            self.fail("Cursor is recycled")
        self.unregister_event(Tuio.Tuio2CursorEvents.newAgent)
        if not self.is_close(Cursor):    
            self.fail(cause ="new Cursor is far")
        self.cPos = Cursor.pos
        self.origin = Cursor.pos
        self.crPos = self.relPos()
        self.sendPos(Cursor)
        self.agent.onPad = self.onPad
        self.agent.fid = self.fid
        self.agent.sid = Cursor.sid
        self.register_event(Cursor.newCursor, RecognizerCursorOnPad.NewCursor2)
        
    def NewCursor2(self,Cursor):
        self.unregister_event(Cursor.newCursor)
        self.register_event(Cursor.updateCursor,RecognizerCursorOnPad.EventMoveCursor)
        self.register_event(Cursor.removeCursor,RecognizerCursorOnPad.EventRemoveCursor)
        self.acquire(Cursor)
        self.cursor = Cursor
        self.has_cur = True
 

    def is_close(self,Cursor):
        if self.dist(self.cPos,Cursor.Pos) < self.maxSpace:
            return True
            
    def dist(self,a,b):
        dx,dy = (a[0]-b[0],a[1]-b[1])
        return math.sqrt(dx**2 + dy**2)







        
  
            
    def dist(a,b):
        dx,dy = (a[0]-b[0],a[1]-b[1])
        return math.sqrt(dx**2 + dy**2)


    def MakeCursorOnPadAgent(self):
        evts = ["newCursor","updateCursor","removeCursor"]
        a = Agent(evts, self)
        return a



    def is_on(self, crcm):
        if (crcm[0] > -1 and crcm[0] < 12 and crcm[1] > -1 and crcm[1] < 12):
            return True
        #en pixels  if (self.crPos[0] > 100 and self.crPos[0] < 520 and self.crPos[1] > -206 and self.crPos[1] < 74):
        # sin centrar if (crcm[0] > 2.6 and crcm[0] < 13.6 and crcm[1] > -8.1 and crcm[1] < 2.9):
        #dist = sqrt((Cursor.pos[0]-self.onPad.px)**2 + (Cursor.pos[1]-self.onPad.py)**2 )
        #if dist < self.radius:
        #    return True

    def relPos(self):
    self.getPadPos()
        #self.pxcm = self.px/(self.ratioX)   
        #self.pycm = self.py/(self.ratioY)
        #self.pxcm = self.px/self.ratioX   
        #self.pycm = self.py/self.ratioY
        #self.pzcm = (self.pz-self.mesa_camZ)/self.ratioZ
        self.cPoscm = (self.cPos[0]/(self.mesa_camZ*self.ratioX/self.pz), self.cPos[1]/(self.mesa_camZ*self.ratioY/self.pz))
        #self.cPoscm = (self.cPos[0]/self.ratioX, self.cPos[1]/self.ratioY)     
        crPoscm = CRelPos(self.cPoscm[0], self.cPoscm[1], self.pxcm, self.pycm, self.pzcm, self.yaw, self.pitch, self.roll)
        #self.crPoscm = crPoscm
        #self.crPoscm = (crPoscm[0] - 2.6),(crPoscm[1]+8.1)
        self.crPoscm = (-1*crPoscm[0]) - 4,(-1*crPoscm[1])+ 8.1
        result = (self.crPoscm[0]*(self.mesa_camZ*self.ratioX/self.pz),self.crPoscm[1]*(self.mesa_camZ*self.ratioY/self.pz))
        #crPos = (relpos[0]*self.ratioX,relpos[1]*self.ratioY)
        return result


    def sendPos(self, Cur):
        self.agent.cPos = self.cPos
        self.agent.origin = self.origin
        self.agent.crPos = self.crPos
        self.agent.crPoscm = self.crPoscm
        self.agent.cPoscm = self.cPoscm
        self.agent.pxcm = self.pxcm     #solo para debug
        self.agent.pycm = self.pycm     #solo para debug
        self.agent.pzcm = self.pzcm       #solo para debug
        self.agent.cPoscm = self.cPoscm   # solo para debug
        self.agent.yaw = self.onPad.yaw        #solo para debug
        self.agent.pitch = self.onPad.pitch    #solo para debug
        self.agent.roll = self.onPad.roll      #solo para debug


    def getPadPos(self):
        self.pxcm = self.onPad.pxcm 
        self.pycm = self.onPad.pycm
        self.pzcm = self.onPad.pzcm
        self.px = self.onPad.px  
        self.py = self.onPad.py  
        self.pz = self.onPad.pz    
        self.yaw = self.onPad.yaw        
        self.pitch = self.onPad.pitch  
        self.roll = self.onPad.roll         

      
        

    def fail(self, cause="Unknown"):
        try:
            self.unregister_all()
        except:
            None
        Recognizer.fail(self,cause)   
            
    def execute(self):
        self.agent.newCursor.call(self.agent)

    def duplicate(self):
        d = self.get_copy()
        d.onPad = self.onPad
        #d.cPos = self.cPos
        #d.origin = self.origin
        #d.crPos = self.crPos
        d.fid = self.fid
        #d.cPoscm = self.cPoscm
        #d.has_cur = self.has_cur 
        d.pxcm= self.pxcm    
        d.pycm = self.pycm    
        d.pzcm = self.pzcm 
        d.yaw = self.yaw       
        d.pitch = self.pitch    
        d.roll = self.roll
        return d





        
         












import GestureAgents.Gestures as Gestures
Gestures.load_recognizer(RecognizerCursorOnPad)
