from .base import *  # noqa


DEBUG = False

# In production, ensure SECRET_KEY and ALLOWED_HOSTS are provided via env
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


