=====================================
Agent-Based Gesture Ecology Framework
=====================================


Author: Carles F. Julià <carles.fernandez@upf.edu>

Testing:
    There are some example Apps in the Apps directory, to test them you just have to execute the python program from inside its folder.


This is an implementation of a framework created by Carles Julia ment to put it to the test.
It was part of my Master thesis @ Cognitive Systems and Interactive Media in Pompeu Fabra University.

What is most interesting about this framework is that it allows for unlimited simultaneous and overlapping gestures to be detected.
Although other frameworks exist that allow for this too, it is inevitable to impose limitations in order to make it possible... the GestureAgents framework reduces those limitations to a minimum.  It simply imposes some rules in the mediation between the framework and the gestures, but the gestures themselves don't suffer any limitations that restrain the developer's creativity in any way.



Gestures in this implementation are built to work within the confines of a "pad".  In order for some of them to be detected, a tangible (or simulated tangible) of code 0 or 1.  A white rectangle will appear next to the tangible, gestures are ment to be drawn within it.

The gestures are meant to adress a music generating application so they include specific things like a drawable ASDR envelope, a drawable equalizer and diverse wave-shapes.
A cheat-sheet .doc file is included in the folder to provide some guidance.

Any swipes that begin near a mid-height of the pad, move to the right and that match any given wave-form will be identified as such.
If a swipe begins and ends close to the low end of the pad and moves to the right will be identified as an envelope filter, regardless of shape... all sensical envelope shapes can fit these constraints.  Thanks to this both gestures can be drawn in the same space and direction but they can be accurately differentiated.
Any swipes that move from right to left will be identified as an equalizer filter.  Since envelope shapes can take all sorts of shapes, some closely resembling those of waveforms or envelopes, segregating these was an important design challenge.  We are culturally predisposed to identify left-to-right movement with the passage of time (probably due to the direction we read in), since in an Envelope and a Wave-form graph the X-axis represents time, drawing these shapes left-to-right would feel odd.  An equalizer filter, on the other hand, is not time based, the X-axis represents pitch rather than time... therefore if any gesture were to be drawn in that direction it should be this one.



-------------------------------------------------------------------------------------------

In order to run this app you must run:

\gesture-agents\Apps\SLsimApp\SLSimApp.py

The following programs are needed:
-Python
-Pygame  (python library)
-Whilst a table with touch capabilities and tangible objects (such as a ReacTable) is the ideal setting for these gestures, it is still possible to run them in a regular computer thanks to the TUIO2 simulator
 



Carles Julia: gesture framework and the application's launcher 
Nicolas Earnshaw: The gestures in use in this implementation
 