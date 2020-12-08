from flask import render_template, url_for, flash, redirect, request, send_file, flash
from webapp import app
from webapp.validator import FileValidator
from os import path, getcwd
from webapp.harmonizer_model import Generate_SATB_Sequentially

@app.route('/')
@app.route('/home')
def home():
    status_msg = ""
    status = "upload"
    return render_template('index.html')

@app.route("/processing", methods=["POST", "GET"])
def processing():
  if request.method == 'POST':
    valid, message = FileValidator.valid_upload(request)
    if valid:
      f = request.files['file']
      f.save(path.join(app.config["FILE_UPLOAD_PATH"], app.config["UPLOADED_FILE_NAME"]))
      flash(message, "success")
      Generate_SATB_Sequentially.generate_harmony_from_melody()
      flash("The harmony has been generated successfully.", "success")
    else:
      flash(message, "danger")
      return redirect(url_for("home"))

  return render_template('listen.html')

@app.route("/listen")
def listen():
  return render_template('listen.html')

@app.route("/download")
def download():
  path_to_file = path.join("output", app.config["GENERATED_MIDI_FILE_NAME"])
  return send_file(path_to_file, as_attachment=True)
