# NeuralCounterpoint-Website

> **Interactive deep learning web application for AI-assisted classical music harmonization using TensorFlow/Keras, Flask, and symbolic MIDI generation.**

## Overview

NeuralCounterpoint-Website is the deployed inference layer of the broader **NeuralCounterpoint** project: an end-to-end generative AI system for symbolic classical music composition.

This repository contains a Flask web application that lets users upload or select a MIDI melody, process it through a trained deep learning model, and generate four-part SATB harmony as a downloadable MIDI file.

The system combines:

* Deep learning model inference
* Symbolic MIDI processing
* Sequential SATB voice generation
* Flask-based web deployment
* Interactive AI-assisted composition

This was built as a from-scratch machine learning engineering project before modern LLM coding assistants were widely available. The model architecture, symbolic music encoding, inference logic, web integration, and deployment workflow were implemented manually.

---

## Project Ecosystem

NeuralCounterpoint is split across multiple public repositories that together demonstrate a full machine learning lifecycle: data preparation, model training, checkpointed experimentation, model inference, and web deployment.

| Repository                                                                             | Role                                                                                                       |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [NeuralCounterpoint](https://github.com/davidalvin/NeuralCounterpoint)                 | Core training experiment for SATB-style classical harmony generation using encoded symbolic music data.    |
| [NeuralCounterpoint-Trainer](https://github.com/davidalvin/NeuralCounterpoint-Trainer) | Generalized TensorFlow/Keras training framework for experimenting with polyphonic music generation models. |
| [NeuralCounterpoint-Website](https://github.com/davidalvin/NeuralCounterpoint-Website) | Flask web application that deploys a trained model for interactive MIDI harmonization.                     |

Together, these repositories form an end-to-end AI music generation pipeline:

```text
Classical MIDI dataset
        ↓
Symbolic music encoding
        ↓
Deep learning model training
        ↓
Saved TensorFlow/Keras model checkpoint
        ↓
Flask web application
        ↓
User-uploaded MIDI melody
        ↓
AI-generated SATB harmonization
        ↓
Downloadable MIDI output
```

---

## What This Repository Does

This repository turns the trained NeuralCounterpoint model into a usable web application.

A user can:

1. Open the web interface.
2. Upload a `.mid` melody or select a default melody.
3. Submit the melody for harmonization.
4. Run the melody through a trained TensorFlow/Keras model.
5. Generate bass, alto, and tenor parts around the input soprano melody.
6. Download the resulting four-part harmonized MIDI file.

The application bridges the gap between model training and real-world interaction by exposing the trained neural network through a simple browser interface.

---

## Deep Learning System

At the core of the app is a trained TensorFlow/Keras model designed for symbolic polyphonic music generation.

The model performs sequential SATB harmonization:

1. **Bass generation**
   The model predicts a bass line from the input melody and surrounding musical context.

2. **Alto generation**
   The model predicts alto using the melody and generated bass.

3. **Tenor generation**
   The model predicts tenor using the melody, generated bass, and generated alto.

This mirrors a structured music-theory workflow while using neural network inference to learn harmonic relationships from data.

The inference pipeline uses:

* Saved TensorFlow/Keras `.h5` model loading
* Sub-model extraction for bass, alto, and tenor prediction
* Symbolic MIDI-to-integer encoding
* One-hot encoded musical context windows
* Temperature-based probabilistic sampling
* Sequential autoregressive voice generation
* MIDI score reconstruction with `music21`

---

## Symbolic Music Representation

Unlike audio generation systems that operate on raw waveforms, NeuralCounterpoint works with symbolic music.

The app converts MIDI melodies into tokenized musical sequences where notes, rests, holds, and end-of-song symbols are represented explicitly.

Example symbolic concepts include:

```text
Note       → MIDI pitch value
Rest       → r
Hold       → _
End marker → /
```

This allows the neural network to model musical structure directly, including:

* Melody
* Harmony
* Rhythm
* Voice leading
* Counterpoint
* Multi-part SATB relationships

---

## Web Application Flow

```text
User uploads/selects MIDI
        ↓
Flask validates input
        ↓
MIDI is parsed with music21
        ↓
Melody is encoded into symbolic sequence
        ↓
TensorFlow/Keras model generates harmony
        ↓
SATB voices are reconstructed
        ↓
music21 writes harmonized MIDI output
        ↓
User downloads generated file
```

---

## Features

* Browser-based MIDI harmonization
* Upload support for `.mid` files
* Default melody selection
* Trained TensorFlow/Keras model inference
* Sequential SATB harmony generation
* Symbolic music processing with `music21`
* Downloadable generated MIDI output
* Flask routing and templating
* Upload validation
* Session-based randomized output filenames
* WSGI-ready deployment structure

---

## Tech Stack

* Python
* Flask
* TensorFlow / Keras
* music21
* NumPy
* SQLAlchemy
* Flask-Limiter
* Jinja2
* HTML / CSS
* MIDI file processing

---

## Repository Structure

```text
.
├── config.py
├── run.py
├── wsgi.py
├── requirements.txt
├── requirements-conda.txt
├── restart.sh
├── shutdown.sh
├── cleanup.sh
└── webapp/
    ├── __init__.py
    ├── routes.py
    ├── validator.py
    ├── input/
    ├── output/
    ├── static/
    ├── templates/
    └── harmonizer_model/
        ├── Generate_SATB_Sequentially.py
        ├── GlobalConstants.py
        ├── HelperFunctions.py
        ├── MelodyGenerator.py
        ├── mapping/
        └── models/
```

---

## Model Files

The application expects a trained TensorFlow/Keras model in:

```text
webapp/harmonizer_model/models/
```

The model path is configured in:

```text
webapp/harmonizer_model/GlobalConstants.py
```

The symbolic mappings used for inference are stored in:

```text
webapp/harmonizer_model/mapping/
```

These mappings translate between MIDI symbols and model-readable integer encodings.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/davidalvin/NeuralCounterpoint-Website.git
cd NeuralCounterpoint-Website
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Alternatively, install from the Conda requirements file:

```bash
conda create --name neuralcounterpoint --file requirements-conda.txt
conda activate neuralcounterpoint
```

---

## Running Locally

For local development:

```bash
export FLASK_ENV=development
python run.py
```

On Windows PowerShell:

```powershell
$env:FLASK_ENV="development"
python run.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## Usage

1. Open the web application.
2. Upload a `.mid` melody or choose a default melody.
3. Submit the melody for harmonization.
4. Wait for the model to generate the missing voices.
5. Download the generated SATB MIDI file.

---

## Configuration

Main application settings are defined in:

```text
config.py
```

Important settings include:

```python
ALLOWED_UPLOAD_FILE_EXTENSIONS = ['MID']
MAX_CONTENT_LENGTH = 10 * 1024
FILE_UPLOAD_PATH = 'webapp/input'
OUTPUT_PATH = 'webapp/output'
DEFAULT_MELODY_DIR = 'default'
```

By default, the app accepts `.mid` files.

---

## Deployment

The project includes `wsgi.py` for production deployment with a WSGI server.

Example:

```bash
uwsgi --ini harmonizer.ini
```

The repository also includes helper scripts for server management:

```text
restart.sh
shutdown.sh
cleanup.sh
```

---

## Why This Project Matters

NeuralCounterpoint-Website demonstrates more than a standalone web app. It shows an end-to-end machine learning system that connects:

* A trained neural network
* Custom symbolic data encoding
* Deep learning inference
* Music theory-inspired generation logic
* Backend web development
* File validation and user interaction
* Generated media output

For a machine learning portfolio, this project highlights the full path from model experimentation to an interactive deployed application.

---

## Applications

This project demonstrates techniques relevant to:

* Generative AI
* Deep learning model deployment
* AI-assisted music composition
* Symbolic music generation
* Sequence modeling
* Recurrent neural networks
* Computational musicology
* Flask web development
* End-to-end machine learning systems
* Creative AI applications


---

## Historical Note

This project was originally built before the rise of modern AI coding assistants. The deep learning architecture, symbolic encoding system, SATB generation pipeline, Flask application, and deployment logic were implemented manually.

---

## Author

**David Alvin**

Machine Learning • Deep Learning • Generative AI • Music AI • Full-Stack ML Applications
