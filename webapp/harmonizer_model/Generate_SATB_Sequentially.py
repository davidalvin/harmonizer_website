#!/usr/bin/env python
# coding: utf-8

# imports
import os
from webapp import app
from webapp.harmonizer_model.GlobalConstants import *
from webapp.harmonizer_model.HelperFunctions import load_midi
from webapp.harmonizer_model.MelodyGenerator import MelodyGenerator, save_score, encode


def generate_harmony_from_melody(song_name=None, temperatures=[1]):
    """Generate a song from a melody
    :song_name: Name of the melody to be harmonized
    :temperature: A list of temperatures for random sampling. 
        Note the number is divided by 10, so 1 will become 0.1.
        Must be entered as a list: e.g. [1, 2, 3]
    """

    # Initialize the song class by loading in the model and mapping files
    new_song = MelodyGenerator(MODEL_PATH, SYMBOL_MAPPING_PATH)

    pathname = os.path.join(app.config["FILE_UPLOAD_PATH"], song_name)
    song = load_midi(pathname)
    encoded_song = encode(song).split()

    #temperatures = [1] # Note this number is divide by 10, so 1 will become 0.1
    temperatures = [float(temp) / 10 for temp in temperatures]

    # Iterate through each instance and generate a different test song
    for temp in temperatures:
        B_melody, A_melody, T_melody = new_song.harmonize_melody_sequentially(
            encoded_song, temperature=temp, key=SONG_KEY, verbose=0)

        # TODO If there are multiple song names this will overwrite them. To be updated...
        save_dir = os.path.join(app.config["OUTPUT_PATH"], song_name)
        # Output the score
        save_score(soprano=encoded_song, bass=B_melody,
                   alto=A_melody, tenor=T_melody, file_name=save_dir)
