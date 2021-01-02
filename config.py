from os import path

class Config(object):
    DEBUG = False
    SECRET_KEY = 'b45ad7e975774f7f988c6aacb177d22'
    #SERVER_NAME = '0.0.0.0:5000'
    # Upload File Quality Checks
    ALLOWED_UPLOAD_FILE_EXTENSIONS = ['MID']
    MAX_CONTENT_LENGTH = 10 * 1024  # 10 kB

    # IO Paths
    FILE_UPLOAD_PATH = path.join('webapp', 'input')
    DEFAULT_MELODY_DIR = 'default'
    OUTPUT_PATH = path.join("webapp", "output")
    SF_PATH = path.join("webapp", "sf") # Soundfont path

class ProductionConfig(Config):
    #DEBUG = True
    #SERVER_NAME = 'prelude49.com:5000'
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'development'
    #SERVER_NAME = '127.0.0.1:5000'
