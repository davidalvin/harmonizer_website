from os import path

class Config(object):
    DEBUG = False
    SECRET_KEY = 'b45ad7e975774f7f988c6aacb177d22'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

    # Upload File Quality Checks
    ALLOWED_UPLOAD_FILE_EXTENSIONS = ['MID']
    MAX_CONTENT_LENGTH = 10 * 1024  # 10 kB

    # IO Paths
    FILE_UPLOAD_PATH = path.join('webapp', 'input')
    UPLOADED_FILE_NAME = "user-upload.mid"
    OUTPUT_PATH = path.join("webapp", "output")
    GENERATED_MIDI_FILE_NAME = "generated-song.mid"

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
