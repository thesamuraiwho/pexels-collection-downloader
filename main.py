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

import pprint
pp = pprint.PrettyPrinter(indent=4)
THEME = "DarkAmber"
PER_PAGE = 80

# Setup settings.json file
default_settings = {"pexels_api_key": ""}#, "LAST_SAVE_PATH": ""}
settings_file = "settings.json"


# "Map" from the settings dictionary keys to the window's element keys
SETTINGS_KEYS_TO_ELEMENT_KEYS = {"pexels_api_key": "-PEXELS API KEY-"}#, "LAST_SAVE_PATH": "-LAST SAVE PATH-"}


def get_json(url, total_collections, auth):
    count = 0
    json = {}

    iterations = 0

    if total_collections / PER_PAGE < 1:
        iterations = 1
    else:
        iterations = int(total_collections / PER_PAGE)

    while count < iterations:
        req = requests.get(f"{url}?page={count}&per_page={PER_PAGE}", headers=auth)
        json = {**json, **req.json()}
        count += 1
    
    return json

##################### Load/Save Settings File #####################
def load_settings(settings_file, default_settings):
    try:
        with open(settings_file, 'r') as f:
            settings = jsonload(f)
    except Exception as e:
        # sg.popup_quick_message(f'exception {e}', 'No settings file found... will create one for you', keep_on_top=True, background_color='red', text_color='white')
        settings = default_settings
        # save_settings(settings_file, settings, None)
    return settings


def save_settings(settings_file, settings, values):
    if values:      # if there are stuff specified by another window, fill in those values
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:  # update window with the values read from settings file
            try:
                settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
            except Exception as e:
                print(f'Problem updating settings from window values. Key = {key}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f)

    # sg.popup('Settings saved')

##################### Make a settings window #####################
def create_settings_window(settings):
    sg.theme(THEME)

    def TextLabel(text): return sg.Text(text+':', justification='r', size=(15,1))

    layout = [  #[sg.Text('Settings', font='Any 15')],
                [TextLabel('Pexels API key'), sg.Input(key='-PEXELS API KEY-')],
                # [TextLabel('Last save path'), sg.Input(key='-LAST SAVE PATH-'), sg.FolderBrowse(target='-LAST SAVE PATH-')],
                [sg.Button('Save'), sg.Button('Exit')]  ]

    window = sg.Window('Settings', layout, keep_on_top=True, finalize=True)

    for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:   # update window with the values read from settings file
        try:
            window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=settings[key])
        except Exception as e:
            print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

    return window


##################### Main Program Window & Event Loop #####################
def create_main_window(settings):
    sg.theme(THEME)

    # TODO: Check if Pexels API Key is valid
    auth = {'Authorization': str(settings["pexels_api_key"])}
    req = requests.get("https://api.pexels.com/v1/collections", headers=auth)
    total_collections = req.json()["total_results"]
    print(f"https://api.pexels.com/v1/collections/?per-page={total_collections}")

    # TODO: Ensure all collections are retrieved
    

    # req = requests.get(f"https://api.pexels.com/v1/collections/?per_page={total_collections}", headers=auth)
    # print(f"total_collections: {total_collections}")
    # collections_json = req.json()["collections"]

    json = get_json("https://api.pexels.com/v1/collections/", total_collections, auth)
    # count = 0
    # json = {}

    # iterations = 0

    # if total_collections / PER_PAGE < 1:
    #     iterations = 1
    # else:
    #     iterations = int(total_collections / PER_PAGE)

    # while count < iterations:
    #     req = requests.get(f"https://api.pexels.com/v1/collections/?page={count}&per_page={PER_PAGE}", headers=auth)
    #     json = {**json, **req.json()}
    #     count += 1

    print(f"total_collections: {total_collections}")
    print(json)
    collections_json = json["collections"]
    print(collections_json)
    pp.pprint(collections_json)

    layout = [  [sg.Listbox(values=[i['title'] for i in collections_json], size=(30, total_collections), 
                    key='-LIST-', enable_events=True), 
                    # sg.Text(f"Description\n{'-'*20}\nTitle: ...\nID: ...\nDescription: ...\nMedia count: 5\nPhotos count: 4\nVideos count: 1", 
                    #     size=(20, 10), key="-DESCRIPTION-"), 
                    sg.MLine(size=(20, 10), key='-DESCRIPTION-'),
                    sg.Text("Collection preview:", size=(20, 10), key="-PREVIEW-")],
                [sg.Text('Select download location'), sg.InputText(), sg.FolderBrowse()],
                [sg.Button('Download'), sg.Button('Exit'), sg.Button('Change Settings')]]

    return sg.Window('Pexels Collection Downloader', layout), collections_json


def main():
    window, settings = None, load_settings(settings_file, default_settings)

    while True:             # Event Loop
        if window is None:
            if settings == default_settings:
                event, values, collections_json = create_settings_window(settings).read(close=True)
                if event == 'Save':
                    save_settings(settings_file, settings, values)
            window, collections_json = create_main_window(settings)

        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        
        # print(f"\n\n\n{values}")
        # print(collections_json)
        # print(f"{collections_json[0]}")
        # print(f"{[i for i in collections_json if values['-LIST-'][0] == i['title']]}")
        print(values['-LIST-'][0])

        window['-DESCRIPTION-'].update(f"Description\n{'-'*20}\nTitle: {[i['title'] for i in collections_json if values['-LIST-'][0] == i['title']][0]}\nID: {[i['id'] for i in collections_json if values['-LIST-'][0] == i['title']][0]}\nDescription: {[i['description'] for i in collections_json if values['-LIST-'][0] == i['title']][0]}\nTotal media count: {[i['media_count'] for i in collections_json if values['-LIST-'][0] == i['title']][0]}\nPhotos count: {[i['photos_count'] for i in collections_json if values['-LIST-'][0] == i['title']][0]}\nVideos count: {[i['videos_count'] for i in collections_json if values['-LIST-'][0] == i['title']][0]}")
        if event == 'Change Settings':
            event, values, collections_json = create_settings_window(settings, collections_json).read(close=True)
            if event == 'Save':
                window.close()
                window = None
                save_settings(settings_file, settings, values)
    window.close()
main()



# def main():
#     sg.theme('DarkAmber')   # Add a touch of color
#     # All the stuff inside your window.
#     layout = [  [sg.Text('Enter Pexels API key'), sg.InputText()],
#                 # [sg.Text('Enter collections URL'), sg.InputText()],
#                 [sg.Listbox(values=sg.theme_list(), size=(20, 12), key='-LIST-', enable_events=True)],
#                 [sg.Text('Select download location'), sg.InputText(), sg.FolderBrowse()],
#                 [sg.Button('Download'), sg.Button('Exit')] ]

#     # Create the Window
#     window = sg.Window('Pexels Collection Downloader', layout)
#     # Event Loop to process "events" and get the "values" of the inputs
#     while True:
#         event, values = window.read()
#         if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
#             break
#         auth = {'Authorization': str(values[0])}
#         print('You entered for the Pexels API key', values[0])
#         print('You entered for the collections URL', values[1])
#         print('You entered for the download location', values[2])
#         print((values[1].split('/')[-2]).split('-'))

#         req = requests.get("https://api.pexels.com/v1/collections", headers=auth)
#         pp.pprint(req.json())

#         # req = requests.get(f"https://api.pexels.com/v1/collections/{}", headers=auth, stream=True)


#     window.close()
# main()