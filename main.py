# Author: Brandon Le

import PySimpleGUI as sg
import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv
import json

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

if 
