from webapp import app

class FileValidator:

  def allowed_extension(filename):
    if not "." in filename:
      return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() not in app.config['ALLOWED_UPLOAD_FILE_EXTENSIONS']:
      return False
    else:
      return True

  def valid_upload(request):
    valid = True
    message = "Your file is being uploaded."
    if request.files:
      file = request.files['file']
      if file.filename == "":
        message = "File must have a filename."
        valid = False

      if not FileValidator.allowed_extension(file.filename):
        message = "Only the following file extensions are allowed: " + ", ".join(ext for ext in app.config['ALLOWED_UPLOAD_FILE_EXTENSIONS'])
        valid = False

      return valid, message
