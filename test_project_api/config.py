# import os
#
#
# class Config:
#     DEBUG = False
#     TESTING = False
#     CSRF_ENABLED = True
#     SECRET_KEY = os.environ.get("SECRET_KEY")
#
#
# class ProductionConfig(Config):
#     DEBUG = False
#
#
# class StagingConfig(Config):
#     DEVELOPMENT = True
#     DEBUG = True
#
#
# class DevelopmentConfig(Config):
#     DEVELOPMENT = True
#     DEBUG = True
#
#
# class TestingConfig(Config):
#     TESTING = True
