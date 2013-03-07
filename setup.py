# -*- coding: utf-8 -*-
'''
Created on 02/07/2012

@author: carles
'''

from setuptools import setup

setup(
    name='AgentGestures',
    version='0.1dev',
    author='Carles F. Julià',
    author_email='carles.fernandez@upf.edu',
    packages=[
              'GestureAgents',
              'GestureAgentsTUIO',
              'GestureAgentsTUIO.tuio',
              'GestureAgentsTUIO.Gestures2D',
              'GestureAgentsPygame',
              ],
    #url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='Agent-Exclusivity-based Gesture Ecology Framework',
    long_description=open('README.txt').read(),
    install_requires=[
        "pygame",
        "pyOpenGL",
    ],
)
