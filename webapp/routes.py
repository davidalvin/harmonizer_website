from flask import render_template, url_for, flash, redirect, request, send_file, flash, session
from webapp import app, limiter
from webapp.validator import FileValidator
from os import path, getcwd
from webapp.harmonizer_model import Generate_SATB_Sequentially
import secrets

# Home
@app.route('/')
@app.route('/home')
@limiter.exempt # Limiter exempt
def home():
    # Generate a random key
    session["SONG_KEY"] = secrets.token_hex(15) + ".mid"
    
    return render_template('index.html')

# The route for generating the song
@app.route("/processing", methods=["POST", "GET"])
def processing():
  if (request.method == 'POST') and (session.get("SONG_KEY", None) is not None):
    valid, message = FileValidator.valid_upload(request)
    song_key = session.get("SONG_KEY")
    print("The song_key is: ", song_key)
    if valid:
      f = request.files['file']
      f.save(path.join(app.config["FILE_UPLOAD_PATH"], song_key))
      flash(message, "success")
     
      Generate_SATB_Sequentially.generate_harmony_from_melody(song_name=song_key)
 
      flash("Harmonization complete", "success")
      session["DOWNLOAD_READY"] = 1
    else:
      flash(message, "danger")
      return redirect(url_for("home"))

  return render_template('listen.html')

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
