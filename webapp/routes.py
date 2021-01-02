from flask import render_template, url_for, flash, redirect, request, send_file, flash, session, send_from_directory
from webapp import app, limiter
from webapp.validator import FileValidator
from os import path, getcwd
from webapp.harmonizer_model import Generate_SATB_Sequentially
import secrets
import subprocess

# Home
@app.route('/')
@app.route('/home')
@limiter.exempt # Limiter exempt
def home():
    # Generate a random key
    session["SONG_KEY"] = secrets.token_hex(15) + ".mid"
    print(f"The root path is {app.root_path}")
    
    return render_template('index.html')

# The route for generating the song
@app.route("/processing", methods=["POST", "GET"])
def processing():
  if (request.method != 'POST') or (session.get("SONG_KEY", None) is None):
    return redirect(url_for("home"))

  song_key=session.get("SONG_KEY")
  output_file = song_key

  # If a default melody is selected, grab the melody
  if request.form["default-melody"]:
    input_file = path.join(app.config["DEFAULT_MELODY_DIR"], request.form["default-melody"])
  # Else, save the file
  else:
    # Check validity / security of the file
    valid, message = FileValidator.valid_upload(request)
    if not valid:
      flash(message, "danger")
      return redirect(url_for("home"))
    
    input_file = song_key # input file is given a random name, equivalent to the song key
    f = request.files['file']
    f.save(path.join(app.config["FILE_UPLOAD_PATH"], input_file))

  print(f'input: {input_file}, ouput: {output_file}')      
  Generate_SATB_Sequentially.generate_harmony_from_melody(input_file=input_file, output_file=output_file)

  flash("Harmonization complete", "success")
  session["DOWNLOAD_READY"] = 1
  midi_path = path.join(app.config["OUTPUT_PATH"], session.get("SONG_KEY"))
  wav_name = session.get("SONG_KEY")[:-3]+"wav"
  wav_path = path.join(app.config["OUTPUT_PATH"],  wav_name) # Path to output wav
  sf_path = path.join(app.config["SF_PATH"], 'FluidR3_GM.sf2') # Path to Sound Fount

  # Convert Midi to Wav using fluidsynth, which is installed as a separate dependency
  # process = subprocess.Popen(['fluidsynth', '-F', wav_path, sf_path, midi_path],
  #                 stdout=subprocess.PIPE, 
  #                 stderr=subprocess.PIPE)

  # TODO: This currently does not display the downloaded file correctly

  # TODO: Should this be in the if statement?
  return render_template('listen.html', wav_name=wav_name)

# Page that is displayed after the song is generated
@app.route("/listen")
def listen():
  if session.get("DOWNLOAD_READY", None) == 1:
    return render_template('listen.html')
  else:
    return render_template('index.html')

# Download the song
@app.route("/download")
def download():
  if (session.get("DOWNLOAD_READY", None) == 1) and (session.get("SONG_KEY", None) is not None):
    path_to_file = path.join("output", session.get("SONG_KEY"))
    return send_file(path_to_file, as_attachment=True)
  else:
    return render_template('index.html')

@app.route('/cdn/wav/<path:filename>', methods=["GET"])
def get_wav(filename):
  return send_from_directory(path.join(app.root_path, "output"), filename=filename)

# Site overloaded
@app.errorhandler(429)
def site_overloaded(e):
    # Set the 429 status explicitly
    return render_template('429.html'), 429

@app.route('/test', methods=["POST"])
def test():
  pass