# Author: Brandon Le

# Includes code from https://pysimplegui.readthedocs.io/en/latest/cookbook/
# Copyright 2020 PySimpleGUI.com
# Licensed under LGPL-3


import PySimpleGUI as sg
import os
import requests
import json

from json import (load as jsonload, dump as jsondump)
from os import path

THEME = "DarkAmber"

# # Setup settings.json file
# DEFAULT_SETTINGS = {"PEXELS_API_KEY": "", "LAST_SAVE_PATH": ""}
# SETTINGS_FILE = "settings.json"

# # "Map" from the settings dictionary keys to the window's element keys
# SETTINGS_KEYS_TO_ELEMENT_KEYS = {"PEXELS_API_KEY": "-PEXELS API KEY-", "LAST_SAVE_PATH": "-LAST SAVE PATH-"}

# ##################### Load/Save Settings File #####################
# def load_settings(settings_file, default_settings):
#     try:
#         with open(settings_file, 'r') as f:
#             settings = jsonload(f)
#     except Exception as e:
#         sg.popup_quick_message(f'exception {e}', 'No settings file found... will create one for you', keep_on_top=True, background_color='red', text_color='white')
#         settings = default_settings
#         save_settings(settings_file, settings, None)
#     return settings


# def save_settings(settings_file, settings, values):
#     if values:      # if there are stuff specified by another window, fill in those values
#         for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:  # update window with the values read from settings file
#             try:
#                 settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
#             except Exception as e:
#                 print(f'Problem updating settings from window values. Key = {key}')

#     with open(settings_file, 'w') as f:
#         jsondump(settings, f)

#     sg.popup('Settings saved')

# ##################### Make a settings window #####################
# def create_settings_window(settings):
#     sg.theme(THEME)

#     def TextLabel(text): return sg.Text(text+':', justification='r', size=(15,1))

#     layout = [  [sg.Text('Settings', font='Any 15')],
#                 [TextLabel('Pexels API key'), sg.Input(key='-PEXELS API KEY-')],
#                 [TextLabel('Last save path'),sg.Input(key='-LAST SAVE PATH-'), sg.FolderBrowse(target='-LAST SAVE PATH-')],
#                 [sg.Button('Save'), sg.Button('Exit')]  ]

#     window = sg.Window('Settings', layout, keep_on_top=True, finalize=True)

#     for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:   # update window with the values read from settings file
#         try:
#             window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=settings[key])
#         except Exception as e:
#             print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

#     return window

# ##################### Main Program Window & Event Loop #####################
# def create_main_window(settings):
#     sg.theme(THEME)

#     # Check if Pexels API Key is valid
#     if 

#     layout = [  [sg.Text()],
#                 [sg.Text('Enter collections URL'), sg.InputText()],
#                 [sg.Button('Ok'), sg.Button('Cancel'), sg.Button('Change Settings')]]

#     return sg.Window('Pexels Collection Downloader', layout)


# def main():
#     window, settings = None, load_settings(SETTINGS_FILE, DEFAULT_SETTINGS )

#     while True:             # Event Loop
#         if window is None:
#             window = create_main_window(settings)

#         event, values = window.read()
#         if event in (sg.WIN_CLOSED, 'Exit'):
#             break
#         if event == 'Change Settings':
#             event, values = create_settings_window(settings).read(close=True)
#             if event == 'Save':
#                 window.close()
#                 window = None
#                 save_settings(SETTINGS_FILE, settings, values)
#     window.close()
# main()

def main():
    sg.theme('DarkAmber')   # Add a touch of color
    # All the stuff inside your window.
    layout = [  [sg.Text('Enter Pexels API key'), sg.InputText()],
                [sg.Text('Enter collections URL'), sg.InputText()],
                [sg.Text('Select download location'), sg.InputText(), sg.FolderBrowse()],
                [sg.Button('Ok'), sg.Button('Cancel')] ]

    # Create the Window
    window = sg.Window('Pexels Collection Downloader', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
            break
        print('You entered for the Pexels API key', values[0])
        print('You entered for the collectiosn URL', values[1])
        print('You entered for the download location', values[2])

    window.close()

main()