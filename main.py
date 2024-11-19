from django.shortcuts import render
import os
from django.core.management import execute_from_command_line
from dotenv import load_dotenv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "update_albums_in_db.settings")

load_dotenv()
PORT = os.getenv('PORT')
# Create your views here.

def run_server():
    execute_from_command_line(["manage.py", "runserver", PORT, "--noreload"])


if __name__ == "__main__":
    run_server()
