# wsgi.py
import sys
import os

# Añade el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application

# Esto es necesario para que AlwaysData ejecute tu app
if __name__ == "__main__":
    application.run()