#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import os
import csv
import music21 as m21

def log(log_file):
    """Write the processing data to a log file for debugging purposes"""
    with open(os.path.join(os.getcwd(),"log.txt"), "a+") as fp:
        fp.write(log_file)

def save_to_csv(encoded_song, save_path):
    """Save an encoded song, in a list format, to a csv"""
    with open(save_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(encoded_song)

def save_list_to_csv(list, save_path):
    """Save a list to a csv"""
    with open(save_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(list)
        
def open_csv(open_path):
    """Open an encoded song from a csv and return it as a list.
    """
    path = os.path.join(open_path)
    with open(path, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)

    return data

def load_midi(pathname):
    """Load a midi song and return it as m21 stream"""
    
    mf = m21.midi.MidiFile()
    mf.open(str(pathname))
    mf.read()
    mf.close()
    return m21.midi.translate.midiFileToStream(mf)