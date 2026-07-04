# Harmonizer Website

A Flask web application that automatically harmonizes a user-provided melody into four-part SATB harmony using a trained TensorFlow/Keras model.

## Overview

Harmonizer Website lets users upload or select a MIDI melody, processes it through a trained sequential harmony model, and generates a harmonized MIDI output with soprano, alto, tenor, and bass parts.

The project includes:

* A Flask web interface
* MIDI upload and validation
* Pretrained TensorFlow/Keras harmony model support
* MIDI parsing and writing with `music21`
* Sequential SATB harmony generation
* Downloadable harmonized MIDI output

## Tech Stack

* Python 3.7
* Flask
* TensorFlow / Keras
* music21
* NumPy
* Flask-Limiter
* SQLAlchemy

## Project Structure

```text
harmonizer_website/
├── config.py
├── run.py
├── wsgi.py
├── requirements.txt
├── requirements-conda.txt
├── webapp/
│   ├── __init__.py
│   ├── routes.py
│   ├── validator.py
│   ├── input/
│   ├── output/
│   ├── static/
│   ├── templates/
│   └── harmonizer_model/
│       ├── Generate_SATB_Sequentially.py
│       ├── GlobalConstants.py
│       ├── HelperFunctions.py
│       ├── MelodyGenerator.py
│       ├── mapping/
│       └── models/
```

## Installation

Clone the repository:

```bash
git clone https://github.com/davidalvin/harmonizer_website.git
cd harmonizer_website
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Alternatively, use the Conda requirements file:

```bash
conda create --name harmonizer --file requirements-conda.txt
conda activate harmonizer
```

## Running the App

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

The repository also includes helper scripts such as `restart.sh`, `shutdown.sh`, and `cleanup.sh`.

## Usage

1. Open the web application.
2. Upload a `.mid` file or choose a default melody.
3. Submit the melody for harmonization.
4. Wait for the model to generate SATB harmony.
5. Download the resulting MIDI file.

## Model

The harmonizer uses a pretrained TensorFlow/Keras model stored in:

```text
webapp/harmonizer_model/models/
```

The model generates harmony sequentially:

1. Bass is predicted first.
2. Alto is predicted using the melody and predicted bass.
3. Tenor is predicted using the melody, bass, and alto.

Mappings for MIDI symbols and keys are stored in:

```text
webapp/harmonizer_model/mapping/
```

## Configuration

Main configuration is handled in `config.py`.

Important settings include:

```python
ALLOWED_UPLOAD_FILE_EXTENSIONS = ['MID']
MAX_CONTENT_LENGTH = 10 * 1024
FILE_UPLOAD_PATH = 'webapp/input'
OUTPUT_PATH = 'webapp/output'
DEFAULT_MELODY_DIR = 'default'
```

Only `.mid` files are accepted by default.

## Deployment

For production deployment, the project includes `wsgi.py` for running the Flask app with a WSGI server.

Example:

```bash
uwsgi --ini harmonizer.ini
```

You may also use the included shell scripts after setting the correct environment variables.

## Notes

* Uploaded MIDI files are saved temporarily in `webapp/input`.
* Generated harmonized MIDI files are written to `webapp/output`.
* The app uses a secret session key to create randomized file names.
* WAV conversion support appears to be planned through FluidSynth, but the conversion code is currently commented out.

## License

No license is currently specified in the repository. Add one before distributing or reusing this project publicly.

## Author

Created by [davidalvin](https://github.com/davidalvin).


	

