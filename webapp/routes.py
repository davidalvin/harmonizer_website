from flask import render_template, url_for, flash, redirect, request, send_file, flash, session, send_from_directory
from webapp import app, limiter
from webapp.validator import FileValidator
from os import path, getcwd, environ
from webapp.harmonizer_model import Generate_SATB_Sequentially
import secrets
import subprocess

def get_song_path(input_file=None, output_path=None, ext=None):
  """
  Returns the path to file with a given extension
  :extension: extension like 'wav', 'mid', 'musicxml'
  """
  
  # Gets the 'tail' of the path which is the filename
  file_name = path.split(input_file)[1]
  root = path.splitext(file_name)[0] 
  out_file_name = root + '.' + ext
  return path.join(output_path,  out_file_name)

def convert_midi(input_file=None, output_path=None, output_ext=None):
  """
  Converts a midi file to a given output using musescore3
  :input_file: /path/to/inputfile
  :output_ext: Extension for output file.
    Allowed Extensions: 'mid', 'wav', 'musicxml', 'svg', 'png'
  """
  allowed_extensions = ['mid', 'wav', 'musicxml', 'svg', 'png']
  if output_ext not in allowed_extensions:
    raise Exception(f'{output_ext} is not an allowed extension')
  
  output_file = get_song_path(
    input_file=input_file, 
    output_path=output_path, 
    ext=output_ext)

  # Uses musescore3. This must first be installed
  # QT_QPA_PLATFORM=offscreen is needed as there is no GUI installed
  environ["QT_QPA_PLATFORM"]='offscreen'
  if output_ext in ['mid', 'wav', 'musicxml']:
    process = subprocess.Popen(['/usr/bin/mscore3', '-o', output_file, input_file],
                  stdout=subprocess.PIPE, 
                  stderr=subprocess.PIPE)
    stdout, stderror = process.communicate()

  
  if output_ext in ['svg', 'png']:
    # -T 0: trims excess whitespaces
    process = subprocess.Popen(['/usr/bin/mscore3', '-T', '0', '-o', output_file, input_file],
                  stdout=subprocess.PIPE, 
                  stderr=subprocess.PIPE)
    stdout, stderror = process.communicate()
    # Musescore appends "-1" to the end of the file name of svg and png images
    output_file = path.splitext(output_file)[0]+'-1' + path.splitext(output_file)[1]
  
  print(stdout)
  print(stderror)
  # Return path/to/outputfile
  return output_file

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
  #wav_name = session.get("SONG_KEY")[:-3]+"wav"
  #wav_path = path.join(app.config["OUTPUT_PATH"],  wav_name) # Path to output wav
  #sf_path = path.join(app.config["SF_PATH"], 'FluidR3_GM.sf2') # Path to Sound Fount

  # # Convert Midi to Wav using fluidsynth, which is installed as a separate dependency
  # process = subprocess.Popen(['/usr/bin/fluidsynth', '-F', wav_path, sf_path, midi_path],
  #                 stdout=subprocess.PIPE, 
  #                 stderr=subprocess.PIPE)
  
  wav_path = convert_midi(input_file = midi_path, output_path=app.config["OUTPUT_PATH"], output_ext="wav")
  svg_path = convert_midi(input_file = midi_path, output_path=app.config["OUTPUT_PATH"], output_ext="svg")
  png_path = convert_midi(input_file = midi_path, output_path=app.config["OUTPUT_PATH"], output_ext="png")
  musicxml_path = convert_midi(input_file = midi_path, output_path=app.config["OUTPUT_PATH"], output_ext="musicxml")
  # TODO: This currently does not display the downloaded file correctly

  # TODO: Should this be in the if statement?
  return render_template('listen.html', wav_path=path.split(wav_path)[1], svg_path=path.split(svg_path)[1], png_path=path.split(png_path)[1], musicxml_path=path.split(musicxml_path)[1])

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

@app.route('/cdn/output/<path:filename>', methods=["GET"])
def get_output(filename):
  return send_from_directory(path.join(app.root_path, "output"), filename=filename)


# Site overloaded
@app.errorhandler(429)
def site_overloaded(e):
    # Set the 429 status explicitly
    return render_template('429.html'), 429

@app.route('/test', methods=["GET","POST"])
def test():
  wav_path = convert_midi(input_file = path.join(app.config["OUTPUT_PATH"], "4ffeb3008222d44a7a16abd6190f29.mid") , output_path=app.config["OUTPUT_PATH"], output_ext="wav")
  print(f'wav path:{wav_path}')
  svg_path = convert_midi(input_file = path.join(app.config["OUTPUT_PATH"], "4ffeb3008222d44a7a16abd6190f29.mid") , output_path=app.config["OUTPUT_PATH"], output_ext="svg")
  print(f'svg path:{svg_path}')

  png_path = convert_midi(input_file = path.join(app.config["OUTPUT_PATH"], "4ffeb3008222d44a7a16abd6190f29.mid") , output_path=app.config["OUTPUT_PATH"], output_ext="png")
  print(f'png path:{png_path}')

  musicxml_path = convert_midi(input_file = path.join(app.config["OUTPUT_PATH"], "4ffeb3008222d44a7a16abd6190f29.mid") , output_path=app.config["OUTPUT_PATH"], output_ext="musicxml")
  print(f'xml path:{musicxml_path}')
  return render_template('listen.html', wav_path=path.split(wav_path)[1], svg_path=path.split(svg_path)[1], png_path=path.split(png_path)[1], musicxml_path=path.split(musicxml_path)[1])