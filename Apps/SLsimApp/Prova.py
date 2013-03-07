import sys

try:
    import user
    sys.path.append('gesture-agents/')
    sys.path.append('gesture-agents-SL/')
except ImportError:
    sys.path.append('../../../cpython_modules/')
    sys.path.append('../../../gesture-agents/')
    sys.path.append('../../../gesture-agents-SL/')


from GestureAgents.AppRecognizer import AppRecognizer
import GestureAgents.Reactor as Reactor
import GestureAgentsTUIO2.Tuio2 as Tuio2

def my_import(name):
        __import__(name)
        return sys.modules[name]

class NetGestures(object):
    def __init__(self):
        self.running = True
        self.tuio2agentgenerator = Tuio2.Tuio2AgentGenerator((1024,768))
        self.sensors = (self.tuio2agentgenerator,)
    def main_loop(self):
        try:
            for s in self.sensors:
                if hasattr(s,'updte'):    s.update()
            Reactor.run_all_now()
        except Exception as ex:
            import traceback
            import sys
            traceback.print_exc(file=sys.stdout)
            raise ex
    
    @staticmethod
    def RegisterHelper(event,delegate):
        class T(object):
            def f(self,*args):
                delegate(*args)
        event.register(T.f,T())
    
    def RegisterHelperAppRecognizer(self,fullname, delegate):
        module = my_import(fullname)
        recognizer = fullname.split('.')[-1]
        recognizerKlass = getattr(module,recognizer)
        self.RegisterHelper(AppRecognizer(recognizerKlass).newAgent,delegate)

    @staticmethod
    def injectFunctionRelPos(funct):
        import GestureAgentsTUIO2.Gestures2D.RecognizerCursorOnPad
        GestureAgentsTUIO2.Gestures2D.RecognizerCursorOnPad.CRelPos = funct

    @staticmethod
    def injectFunctionInvRelPos(funct):
        import GestureAgentsTUIO2.Gestures2D.RecognizerPad
        GestureAgentsTUIO2.Gestures2D.RecognizerPad.tablePos = funct
