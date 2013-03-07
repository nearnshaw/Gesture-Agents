'''
Created on 21/06/2012

@author: carles
'''

import types
import datetime

class ClassLogged(type):
    #number = 0
    def __new__(cls, name, bases, attrs):
    
        for attr_name, attr_value in attrs.iteritems():
            if isinstance(attr_value, types.FunctionType):
                attrs[attr_name] = cls.deco(attr_value)
        
        attrs["_ClassLogged_name"] = name
        attrs["log"] = lambda self,text: self._file_logger.write("> %s\n" % text)
        
        return super(ClassLogged, cls).__new__(cls, name, bases, attrs)
    
    @classmethod
    def deco(cls, func):
        def wrapper(*args, **kwargs):
            self = args[0]
            klass = self.__class__
            try:
                file_logger = self._file_logger
            except AttributeError:
                num = getattr(klass, "_instance_number_",0)
                fname = "%s-%d.log" % (klass._ClassLogged_name,num)
                self._file_logger = open(fname,'w')
                klass._instance_number_ = num + 1
                file_logger = self._file_logger
            file_logger.write("%s %s(%s)\n" % (str(datetime.datetime.today()), func.func_name, ", ".join([repr(a) for a in args[1:]]+["%s=%s" % (str(k),repr(v)) for k,v in kwargs.iteritems()])))
            file_logger.flush()
            return func(*args, **kwargs)
        return wrapper

if __name__ == "__main__":
    class MyKlass(object):
        __metaclass__ = ClassLogged
    
        def func1(self): 
            pass
        def func2(self,a):
            pass
    
    mk = MyKlass().func1()
    mk.func2(42)
    MyKlass().func2(3)
    MyKlass().func2(a=44)
