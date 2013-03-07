#!/usr/bin/env python
# -*- coding: utf-8 -*-

recognizers = []
recognizers_loaded = []

def load_recognizer(r):
    if r not in recognizers_loaded:
        recognizers_loaded.append(r)
        r()
    #return recognizers_loaded[r]
