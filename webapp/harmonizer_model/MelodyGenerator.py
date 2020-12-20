import tensorflow as tf
import os
import json
import numpy as np
import music21 as m21
from webapp.harmonizer_model.GlobalConstants import *

def save_melody(melody="",stream="", step_duration=0.25):
    """Save a part as a music 21 stream.
    :melody: Notes from a part as midi notes
    :stream: The music21 stream.part
    :step_duration: Duration of the smallest note in quarterLength

    returns stream, a music 21 stream
    """
    # create a music21 stream
    # This defaults to a 4/4 bars, C major

    # parse all the symbols in the melody and create note / rest objects
    start_symbol = None
    step_counter = 1 # Units are of step_duration

    for i, symbol in enumerate(melody):

        # Handle an edge case when the first note is a hold symbol "_".
        # If this is the case, convert the symbol to a rest as this a poor prediction
        if i==0 and symbol == "_":
            symbol = "r"

        # handle a note / rest
        if symbol != "_" or i + 1 == len(melody):
            if start_symbol is not None:
                quarter_length_duration = step_duration * step_counter
                # handle rest
                if start_symbol == "r":
                    m21_event = m21.note.Rest(quarterLength=quarter_length_duration)

                # handle note
                else:
                    m21_event = m21.note.Note(int(start_symbol), quarterLength=quarter_length_duration)

                stream.append(m21_event)

                # reset the counter
                step_counter = 1
            start_symbol = symbol

        # handle a prolongation (_)
        else:
            step_counter += 1
    return stream

def save_score(soprano="",alto="", tenor="", bass="", step_duration=0.25, format="midi", file_name="melody.midi"):
    """Save a 4-part score as a file
    :soprano:, :alto:, :tenor:, bass: The four parts of the score, encoded as midi symbols in a list
    :step_duration: Duration of step in quarterLength
    :format: Format of the saved file
    :file_name: File name used when saving
    """
    parts_dict = {"soprano": soprano,
                  "alto": alto,
                  "tenor": tenor,
                  "bass": bass
                 }

    # Create a music21 stream
    # This defaults to a 4/4 bars, C major
    stream = m21.stream.Stream()

    for part_name in parts_dict.keys():
        # Write the soprano part
        if parts_dict[part_name] != "":
            p = m21.stream.Part()
            p.id = part_name
            stream.insert(0,save_melody(melody=parts_dict[part_name], stream=p))

    # write the m21 stream to a midi file
    stream.write(format, file_name)

def encode(song, time_step = 0.25):
    """Encode a song into a time series with the following format:
        Middle C, Quarter Note = 60___
        Rest, 8th note = r_
    """
    encoded_song = []

    # Iterate through each item (note or rest)
    for item in song.flat.notesAndRests:

        # handle notes
        if isinstance(item, m21.note.Note):
            symbol = item.pitch.midi
        elif isinstance(item, m21.note.Rest):
            symbol = 'r'

        # convert the notes and rests into a time series
        steps = int(item.duration.quarterLength / time_step)

        # This ensures that none of the steps are longer than 8 bars
        # (1/time_step = 4 16th notes in a quarter note, *4 quarter notes in a bar * 8 bars)
        # This line could be commented out if long time steps are properly removed
        steps = min(1/time_step*4*8, steps)

        # iterate through each step
        for i in range(steps):
            if i==0:
                encoded_song.append(symbol)
            if i>0:
                encoded_song.append("_")

    # Convert the song to a string
    encoded_song = " ".join(map(str,encoded_song))

    return encoded_song


class MelodyGenerator:
    """Defines a Melody Generator class for a model built of a B, A, S and T sub-model"""
    def __init__(self, model_path = MODEL_PATH, mapping_path = SYMBOL_MAPPING_PATH, key_mapping_path = KEY_MAPPING_PATH):
        self.model_path = model_path
        self.model = tf.keras.models.load_model(model_path)

        # The model is built of sub-models named B_model, A_model and T_model
        self.model_B = self.model.get_layer("B_model")
        self.model_A = self.model.get_layer("A_model")
        self.model_T = self.model.get_layer("T_model")

        # Load the mapping (Midi Symbol-> Int)
        with open(mapping_path, "r") as fp:
            self.mappings = json.load(fp)

        # Create a reverse mapping (Int -> Midi Symbol)
        self.reverse_mappings = {}
        for k,v in self.mappings.items():
            self.reverse_mappings[v] = k

        # Load the key mapping
        with open(key_mapping_path, "r") as fp:
            self.key_mappings = json.load(fp)

    def sample_with_temperature(self, probabilities, temperature):
        """Sample an index with a probabilities distribution defined by
        the temperature and return the index.
        temperture = infinity -> leads to a soft, random distribution
        temperature = 0 -> leads to a deterministic distribution
        temperature = 1 -> raw distribution from the predictions
        """

        predictions = np.log(probabilities) / temperature

        # normalize the probabilities using a softmax
        probabilities = np.exp(predictions) / np.sum(np.exp(predictions))

        choices = range(len(probabilities)) # [0, 1, 2, ...]

        # select an index according to the probability distriution
        index = np.random.choice(choices, p=probabilities)

        return index

    def get_top_indices(self, probabilities, num_rankings=5):
            top_idx = np.argsort(probabilities)[-num_rankings:]
            top_notes = [self.reverse_mappings[i] for i in top_idx]
            for i,note in enumerate(top_notes):
                print("{}:\t{}".format(note, probabilities[top_idx[i]]*100))

    def harmonize_melody_sequentially(self, voice_S, key='C major', temperature=1, verbose=0):

        """Generate a melody from a seed sequentially.
        First the B note is predicted, then A, then T, as opposed to all in parallel.
        :temperature: Indicates how random the melody should be from 0 -> infinity, with 0 being more deterministic
            and infinity being more random
        :verbose: If verbose = 1, then details of the generation will be printed to the terminal. Used for debugging.
        """

        print("Generating the melody sequentially...")

        num_steps = len(voice_S)
        num_classes = len(self.mappings)
        num_keys = len(self.key_mappings)

        # Initialize the appropriate start and end symbols
        voice_B = ["/"] * TRAIN_SEQUENCE_LENGTH
        voice_A = ["/"] * TRAIN_SEQUENCE_LENGTH
        voice_T = ["/"] * TRAIN_SEQUENCE_LENGTH
        voice_S = ["/"] * TRAIN_SEQUENCE_LENGTH + voice_S + ["/"] * TRAIN_SEQUENCE_LENGTH

        # Map the melody to intgeter
        voice_B_int = [self.mappings[symbol] for symbol in voice_B]
        voice_A_int = [self.mappings[symbol] for symbol in voice_A]
        voice_T_int = [self.mappings[symbol] for symbol in voice_T]
        voice_S_int = [self.mappings[symbol] for symbol in voice_S]

        if verbose==1:
            print("---Voices as integers----")
            print("voice_B_int, ", voice_B_int)
            print("voice_A_int, ",voice_A_int)
            print("voice_T_int, ",voice_T_int)
            print("voice_S_int, ",voice_S_int)

        # Iterate through each note in the template melody
        for i in range(num_steps):

            # Print an update on the progress
            if i%16==0:
                print("Percent Complete: {}%".format(int(i/num_steps*100)))

            # Break up the template melody into past, current and future
            voice_S_past = voice_S_int[i:i+TRAIN_SEQUENCE_LENGTH]
            voice_S_current = voice_S_int[i+TRAIN_SEQUENCE_LENGTH]
            voice_S_future = voice_S_int[i+1+TRAIN_SEQUENCE_LENGTH:i+1+2*TRAIN_SEQUENCE_LENGTH]
            ########
            voice_S_future = np.flip(voice_S_future)
            #######
            # Get the past target melody
            voice_B_past = voice_B_int[i:i+TRAIN_SEQUENCE_LENGTH]
            voice_A_past = voice_A_int[i:i+TRAIN_SEQUENCE_LENGTH]
            voice_T_past = voice_T_int[i:i+TRAIN_SEQUENCE_LENGTH]

            # Print to the terminal if verbose is on
            if verbose==1:
                print(i, ":----Inputs prior to OH Encoding------")
                print("voice_B_past, ", voice_B_past, [self.reverse_mappings[symbol] for symbol in voice_B_past])
                print("voice_A_past, ", voice_A_past, [self.reverse_mappings[symbol] for symbol in voice_A_past])
                print("voice_T_past, ", voice_T_past, [self.reverse_mappings[symbol] for symbol in voice_T_past])
                print("voice_S_past, ", voice_S_past, [self.reverse_mappings[symbol] for symbol in voice_S_past])
                print("voice_S_current, ", voice_S_current, self.reverse_mappings[voice_S_current])
                print("voice_S_future, ", voice_S_future, [self.reverse_mappings[symbol] for symbol in voice_S_future])

            # One hot encode each of the above
            voice_S_past = tf.keras.utils.to_categorical(voice_S_past, num_classes)
            voice_S_current = tf.keras.utils.to_categorical(voice_S_current, num_classes)
            voice_S_future = tf.keras.utils.to_categorical(voice_S_future, num_classes)
            voice_B_past = tf.keras.utils.to_categorical(voice_B_past, num_classes)
            voice_A_past = tf.keras.utils.to_categorical(voice_A_past, num_classes)
            voice_T_past = tf.keras.utils.to_categorical(voice_T_past, num_classes)
            voice_S_key = tf.keras.utils.to_categorical(self.key_mappings[key], num_keys)

            if verbose==1:
                print("---Model B inputs---")
                print("voice_B_past:", voice_B_past)
                print("voice_A_past:", voice_A_past)
                print("voice_T_past:", voice_T_past)
                print("voice_S_past:", voice_S_past)
                print("voice_S_current:", voice_S_current)
                print("voice_S_future:", voice_S_future)
                print("voice_S_key:", voice_S_key)

            # Make a prediction for B
            model_B_inputs = ([voice_B_past],
                            [voice_A_past],
                            [voice_T_past],
                            [voice_S_past],
                            [voice_S_current],
                            [voice_S_future],
                            [voice_S_key],
                            )
            predictions = self.model_B.predict(model_B_inputs, steps=1)
            B_pred = predictions[0]
            
            # Sample the prediction B with temperature
            output_B_int = self.sample_with_temperature(B_pred, temperature)
            #output_B_int = np.argmax(B_pred)
            output_B_int_oh = tf.keras.utils.to_categorical(output_B_int, num_classes=num_classes)

            if verbose==1:
                print("---Model A inputs---")
                print("voice_B_past:", voice_B_past)
                print("voice_A_past:", voice_A_past)
                print("voice_T_past:", voice_T_past)
                print("voice_S_past:", voice_S_past)
                print("voice_S_current:", voice_S_current)
                print("voice_S_future:", voice_S_future)
                print("voice_S_key:", voice_S_key)
                print("output_B_int_oh:", output_B_int_oh)

            # Make a prediction for A
            model_A_inputs = ([voice_B_past],
                            [voice_A_past],
                            [voice_T_past],
                            [voice_S_past],
                            [voice_S_current],
                            [voice_S_future],
                            [voice_S_key],
                            [output_B_int_oh]
                            )

            predictions = self.model_A.predict(model_A_inputs, steps=1)
            A_pred = predictions[0]

            # Sample the prediction A with temperature
            output_A_int = self.sample_with_temperature(A_pred, temperature)
            #output_A_int = np.argmax(A_pred)
            output_A_int_oh = tf.keras.utils.to_categorical(output_A_int, num_classes=num_classes)

            if verbose==1:
                print("---Model A inputs---")
                print("voice_B_past:", voice_B_past)
                print("voice_A_past:", voice_A_past)
                print("voice_T_past:", voice_T_past)
                print("voice_S_past:", voice_S_past)
                print("voice_S_current:", voice_S_current)
                print("voice_S_future:", voice_S_future)
                print("voice_S_key:", voice_S_key)
                print("output_B_int_oh:", output_B_int_oh)
                print("output_A_int_oh:", output_A_int_oh)

            # Make a prediction for A
            model_T_inputs = ([voice_B_past],
                            [voice_A_past],
                            [voice_T_past],
                            [voice_S_past],
                            [voice_S_current],
                            [voice_S_future],
                            [voice_S_key],
                            [output_B_int_oh],
                            [output_A_int_oh]
                            )

            predictions = self.model_T.predict(model_T_inputs, steps=1)
            T_pred = predictions[0]

            if verbose==1:
                print("---Predictions---")
                print("B Predictions:", B_pred)
                print("B Top:", self.get_top_indices(B_pred))
                print("A Predictions:", A_pred)
                print("A Top:", self.get_top_indices(A_pred))
                print("T Predictions:", T_pred)
                print("T Top:", self.get_top_indices(T_pred))

            # Sample the prediction T with temperature
            output_T_int = self.sample_with_temperature(T_pred, temperature)
            #output_T_int = np.argmax(T_pred)

            # Update the template melody by appending it to the end
            voice_B_int.append(output_B_int)
            voice_A_int.append(output_A_int)
            voice_T_int.append(output_T_int)
            # Map it to a midi symbol
            output_B_symbol = self.reverse_mappings[output_B_int]
            output_A_symbol = self.reverse_mappings[output_A_int]
            output_T_symbol = self.reverse_mappings[output_T_int]

            # Print to the terminal if verbose is on
            if verbose==1:
                print("---Selected---")
                print("B:", output_B_symbol)
                print("A:", output_A_symbol)
                print("T:", output_T_symbol)

            # Check whether we are at the end of the melody
            if output_B_symbol == "/":
                print("Reached the end of the song at {} steps.".format(i))
                break

            # Update the target melody with the prediction
            voice_B.append(output_B_symbol)
            voice_A.append(output_A_symbol)
            voice_T.append(output_T_symbol)

        # return the target melody (excluding the padding at the beginning)
        return voice_B[TRAIN_SEQUENCE_LENGTH:], voice_A[TRAIN_SEQUENCE_LENGTH:], voice_T[TRAIN_SEQUENCE_LENGTH:]
