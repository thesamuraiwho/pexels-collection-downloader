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
import math

import pprint
pp = pprint.PrettyPrinter(indent=4)
THEME = "DarkAmber"
PER_PAGE = 80

# Setup settings.json file
default_settings = {"pexels_api_key": ""}#, "LAST_SAVE_PATH": ""}
settings_file = "settings.json"


# "Map" from the settings dictionary keys to the window's element keys
SETTINGS_KEYS_TO_ELEMENT_KEYS = {"pexels_api_key": "-PEXELS API KEY-"}#, "LAST_SAVE_PATH": "-LAST SAVE PATH-"}

directories = ["thumbnails", "downloads"]
parent_dir = os.getcwd()

for i in directories:
    try:
        os.mkdir(os.path.join(parent_dir, i))
    except OSError as error:
        print(error)


def get_json(url, total_collections, auth):
    count = 0
    json = {}
    iterations = 0

    print(f"url: {url}")
    print(f"total_collections: {total_collections}")
    print(f"PER_PAGE: {PER_PAGE}")
    print(f"check: {total_collections / PER_PAGE < 1}")
    if total_collections / PER_PAGE < 1:
        iterations = 1
    else:
        iterations = math.ceil(total_collections / PER_PAGE)

    print(f"iterations: {iterations}")

    while count < iterations:
        print(f"{url}?page={count + 1}&per_page={PER_PAGE}")
        req = requests.get(f"{url}?page={count + 1}&per_page={PER_PAGE}", headers=auth)
        json = {**json, **req.json()}
        if 'media' in json.keys():
            pp.pprint([i['id'] for i in json['media']])
            print(f"iteration {count} media count: {len([i['id'] for i in json['media']])}")
        count += 1
    
    if 'media' in json.keys():
        # pp.pprint(json['media'])
        print(f"media count: {len([i['id'] for i in json['media']])}")

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

    json = get_json("https://api.pexels.com/v1/collections/", total_collections, auth)

    print(f"total_collections: {total_collections}")
    print(f"json: {json}")
    collections_json = json["collections"]
    print(f"collections_json: {collections_json}")
    pp.pprint(collections_json)

    image_preview_layout = [[sg.Text('Collection Preview')],
                            [sg.HorizontalSeparator()],
                            [sg.Image(key='-IMAGE-')]]

    layout = [  [sg.Listbox(values=[i['title'] for i in collections_json], size=(30, total_collections), 
                    key='-LIST-', enable_events=True),
                    sg.MLine(size=(20, 10), key='-DESCRIPTION-'),
                    sg.Column(image_preview_layout, size=(20, 10), key="-PREVIEW-")],
                [sg.Text('Select download location'), sg.InputText(), sg.FolderBrowse()],
                [sg.Button('Download'), sg.Button('Exit'), sg.Button('Change Settings')]]

    return sg.Window('Pexels Collection Downloader', layout), collections_json


# Download media
# Based on code from: https://sempioneer.com/python-for-seo/how-to-download-images-in-python/#Method_One_How_To_Download_Multiple_Images_From_A_Python_List

import enum

class Media(enum.Enum):
    photo = 1
    video = 2

def download_media(urls, media_type):
    broken_urls = []
    for media in urls:
        # We can split the file based upon / and extract the last split within the python list below:
        if media_type == Media.photo:
            file_name = media.split('/')[-1]
        else:
            file_name = media.split('/')[-2] + ".mp4"
        print(f"This is the file name: {file_name}")
        # Now let's send a request to the image URL:
        r = requests.get(media, stream=True)
        # We can check that the status code is 200 before doing anything else:
        if r.status_code == 200:
            # This command below will allow us to write the data to a file as binary:
            with open(file_name, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        else:
            # We will write all of the images back to the broken_images list:
            broken_urls.append(media)
    
    return broken_urls

# image_urls = ['https://images.pexels.com/photos/1790393/pexels-photo-1790393.jpeg',
#              'https://images.pexels.com/photos/1629014/pexels-photo-1629014.png']
# video_urls = ['https://www.pexels.com/video/4659817/download',
#                 'https://www.pexels.com/video/4747162/download']
# download_media(image_urls, Media.photo)
# download_media(video_urls, Media.video)


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
        
        print(f"event: {event}")
        print(values)
        
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        if event == '-LIST-':
            print(values['-LIST-'][0])
            selection = [i for i in collections_json if values['-LIST-'][0] == i['title']][0]
            print(f"selection: {selection}")

            window['-DESCRIPTION-'].update(f"Description\n{'-'*20}\n"
                                            f"Title: {selection['title']}\n"
                                            f"ID: {selection['id']}\n"
                                            f"Description: {selection['description']}\n"
                                            f"Total media count: {selection['media_count']}\n"
                                            f"Photos count: {selection['photos_count']}\n"
                                            f"Videos count: {selection['videos_count']}")


            auth = {'Authorization': str(settings["pexels_api_key"])}

            json = get_json(f"https://api.pexels.com/v1/collections/{selection['id']}", selection['media_count'], auth)
            # pp.pprint(json['media'])
            photos = [i['src']['tiny'] for i in json['media'] if i['type'] == 'Photo']
            # pp.pprint(photos)
            print(f"len photos: {len(photos)}")
            videos = [i['image'] for i in json['media'] if i['type'] == 'Video']
            # pp.pprint(videos)
            print(f"len videos: {len(videos)}")
            print(len([i['id'] for i in json['media']]))
            print(f"selection media count: {selection['media_count']}")

            # req = requests.get(f"https://api.pexels.com/v1/collections/{selection['id']}?per_page=15", headers=auth)
            # print(f"\n\nrequest for {selection['id']}")
            # pp.pprint(req.json())
            # pp.pprint([i['src']['tiny'] for i in req.json()['media'] if i['type'] == 'Photo'])
            # pp.pprint([i['image'] for i in req.json()['media'] if i['type'] == 'Video'])
            # pp.pprint([i['src']['tiny'] for i in req.json()['media']])



        if event == 'Change Settings':
            event, values = create_settings_window(settings).read(close=True)
            if event == 'Save':
                window.close()
                window = None
                save_settings(settings_file, settings, values)
    window.close()
main()
