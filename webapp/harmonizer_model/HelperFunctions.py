#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import os
import music21 as m21

def load_midi(pathname):
    """Load a midi song and return it as m21 stream"""
    
    mf = m21.midi.MidiFile()
    mf.open(str(pathname))
    mf.read()
    mf.close()
    return m21.midi.translate.midiFileToStream(mf)