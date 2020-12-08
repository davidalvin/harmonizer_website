#!/usr/bin/env python
# coding: utf-8

# imports
import os
from webapp import app
from webapp.harmonizer_model.GlobalConstants import *
from webapp.harmonizer_model.HelperFunctions import *
from webapp.harmonizer_model.MelodyGenerator import MelodyGenerator, save_score, encode


def generate_harmony_from_melody():
    # Initialize the song
    new_song = MelodyGenerator(MODEL_PATH, SYMBOL_MAPPING_PATH)

    pathname = os.path.join(app.config["FILE_UPLOAD_PATH"], app.config["UPLOADED_FILE_NAME"])
    song = load_midi(pathname)
    encoded_song = encode(song).split()

    # Define an array with different temperatures t test
    temperatures = [1]
    temperatures = [float(temp) / 10 for temp in temperatures]

    # Iterate through each instance and generate a different test song
    for temp in temperatures:
        B_melody, A_melody, T_melody = new_song.harmonize_melody_sequentially(
            encoded_song, temperature=temp, key=SONG_KEY, verbose=0)
        save_dir = os.path.join(app.config["OUTPUT_PATH"], app.config["GENERATED_MIDI_FILE_NAME"])
        # Output the score
        save_score(soprano=encoded_song, bass=B_melody,
                   alto=A_melody, tenor=T_melody, file_name=save_dir)
        print(save_dir)
