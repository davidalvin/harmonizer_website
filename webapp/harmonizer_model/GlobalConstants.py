#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import os

cwd = os.getcwd()
#------SONGS--------
# ENCODED_SONG_PATH = ".\\encoded_songs" # Path where encoded songs are saved
# COMBINED_SONGS_PATH = ".\\encoded_songs_singlefile" # Path where encoded songs are saved

#------TRAINING-----
TRAINING_PATH = os.path.join(cwd,"midi_training","original")
TRAINING_ENCODED_PATH = os.path.join(cwd,"encoded_train_midis")
TRAINING_COMBINED_SONGS_PATH = os.path.join(cwd,"encoded_train_singlefile")

# MAPPING_PATH = ".\\mapping"
# INT_SONGS_PATH = ".\\encoded_songs_singlefile"
# TRAIN_PATH = ".\\train_sequences"
# SAVE_MODEL_PATH = ".\\models"

model_name = "LSTMx128x128-Densex512x128-Densex512x128-SYMBOL-SCALE-64-Dropout-0.2-C-Maj-25E-20201016.h5"
MODEL_PATH = os.path.join("webapp", "harmonizer_model", "models", model_name)
SYMBOL_MAPPING_PATH = os.path.join("webapp", "harmonizer_model", "mapping", "mappings_symbol.jsn")
KEY_MAPPING_PATH = os.path.join("webapp", "harmonizer_model", "mapping", "mappings_key.jsn")

TIME_STEPS = 0.125 # Smallest time steps in quarter_length
TRAIN_SEQUENCE_LENGTH = 64 # Length of the training sequence
SONG_KEY = "C major"



#------SMYBOLS------
EOF_ = "/"
REST_ = 'r'
HOLD_ = "_"

MODE = "MAJ"
TRANSPOSE_DICT = {-5:"G",
                  -4:"G#",
                  -3:"A",
                  -2:"A#",
                  -1:"B",
                  0:"C",
                  1:"C#",
                  2:"D",
                  3:"D#",
                  4:"E",
                  5:"F",
                  6:"F#"}

DILATIONS = {0.25:"16th",
                  0.5:"8th",
                  1:"quarter",
                  2:"Half",
                  4:"whole"
                 }

# Define the list of features
FEATURES_TO_INT = {"symbol": 0,
                   "symbol_conv": 1,
                   "note_name": 2,
                   "octave": 3,
                   "degree": 4,
                   "strike": 5,
                   "key": 6}

USE_MAPPING = {"symbol": 1,
               "symbol_conv": 0,
               "note_name": 1,
               "octave": 1,
               "degree": 1,
               "strike": 1,
               "key": 1}

FEATURE_NAMES = list(FEATURES_TO_INT.keys())
NUM_FEATURES = len(FEATURES_TO_INT)

# Used by the STRIKE feature
NOTE_ON_ = 2
NOTE_HOLD_ = 1
NOTE_OFF_ = 0

# Define the hold symbols across each feature.
# None indicates that instead of a hold symbol, just use the current note encoded as a feature.
HOLD_SYMBOL = {"symbol": HOLD_,  # _
               "symbol_conv": None,
               "note_name": HOLD_,
               "octave": None,
               "degree": None,
               "strike": NOTE_HOLD_,
               "key": None}

# Define the rest symbols across each feature
REST_SYMBOL = {"symbol": REST_,  # r
               "symbol_conv": NOTE_OFF_,
               "note_name": REST_,
               "octave": NOTE_OFF_,
               "degree": NOTE_OFF_,
               "strike": NOTE_ON_,
               "key": None}

# Define the rest symbols across each feature
EOF_SYMBOL = {"symbol": EOF_,  # _
               "symbol_conv": NOTE_OFF_, # 0. Needs to be a number for convolutions
               "note_name": EOF_,
               "octave": EOF_,
               "degree": EOF_,
               "strike": NOTE_OFF_,
               "key": EOF_} # THought it would be worth keeping as 0 as that already represents note off

# Define a dictionary of voices
VOICES_TO_INT = {"S": 0,
                 "A": 1,
                 "T": 2,
                 "B": 3,
                 }
NUM_VOICES = len(VOICES_TO_INT)

MIN_MIDI_INT = 20 #The note before A0 which is 21. When scaled, 20 -> 0
MAX_MIDI_INT = 108 #C8, when scaled 108 -> 1

