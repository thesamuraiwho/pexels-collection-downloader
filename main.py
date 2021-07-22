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

# Globals
pp = pprint.PrettyPrinter(indent=4)
api_calls = 0

# Constants
THEME = "DarkAmber"
PER_PAGE = 80

# Setup settings.json file
default_settings = {"pexels_api_key": "", "home": ""}
settings_file = "settings.json"

# "Map" from the settings dictionary keys to the window's element keys
SETTINGS_KEYS_TO_ELEMENT_KEYS = {"pexels_api_key": "-PEXELS API KEY-", "home": "-HOME-"}

directories = ["thumbnails", "downloads"]
parent_dir = os.getcwd()

for i in directories:
    try:
        os.mkdir(os.path.join(parent_dir, i))
    except OSError as error:
        print(error)

# Download media
# Based on code from: https://sempioneer.com/python-for-seo/how-to-download-images-in-python/#Method_One_How_To_Download_Multiple_Images_From_A_Python_List

import enum

class Media(enum.Enum):
    photo = 1
    video = 2

def download_media(urls, download_dir, media_type):
    broken_urls = []
    for media in urls:
        # We can split the file based upon / and extract the last split within the python list below:
        if media_type == Media.photo:
            file_name = download_dir + (media.split('/')[-1]).split("?")[0]
        else:
            file_name = download_dir + media.split('/')[-2] + ".mp4"
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

def get_collections(url, total_collections, auth):
    count = 0
    collections = []
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
        collections += req.json()['collections']
        count += 1

    return collections

def get_collection_media(url, total_collections, auth):
    count = 0
    collection_media = []
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
        new_collection_media = req.json()['media']

        photos = [i['id'] for i in new_collection_media if i['type'] == 'Photo']
        print(f"len photos: {len(photos)}")
        videos = [i['id'] for i in new_collection_media if i['type'] == 'Video']
        print(f"len videos: {len(videos)}")

        collection_media += new_collection_media
        count += 1

    return collection_media


##################### Load/Save Settings File #####################
def load_settings(settings_file, default_settings):
    # TODO: Check if Pexels API Key is valid
    # TODO: Check if home path is still valid, ie exists

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

    layout = [  [TextLabel('Pexels API key'), sg.Input(key='-PEXELS API KEY-')],
                [TextLabel('Home directory'), sg.Input(key='-HOME-'), sg.FolderBrowse(target='-HOME-')],
                [sg.Button(key='-SAVE-', button_text='Save'), sg.Button(button_text='Exit', key="-EXIT-")]  ]

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
    auth = {'Authorization': str(settings["pexels_api_key"])}
    print(f"home: {str(settings['home'])}")
    req = requests.get("https://api.pexels.com/v1/collections", headers=auth)
    total_collections = req.json()["total_results"]
    print(f"https://api.pexels.com/v1/collections/?per-page={total_collections}")
    collections = get_collections("https://api.pexels.com/v1/collections/", total_collections, auth)

    print(f"total_collections: {total_collections}")
    print(f"collections:")
    pp.pprint(collections)

    left_col = [[sg.Text("Collections")],
                    [sg.HorizontalSeparator()],
                    [sg.Listbox(values=[i['title'] for i in collections], size=(30, total_collections), 
                        key='-LIST-', enable_events=True)]]
    mid_col = [[sg.Text("Collection Description")],
                [sg.HorizontalSeparator()],
                [sg.MLine(size=(20, 10), key='-DESCRIPTION-')]]
    right_col = [[sg.Text('Collection Quality')],
                    [sg.HorizontalSeparator()],
                    [sg.Radio(key="-QUALITY_ORIGINAL-", text="Original", default=True, enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_2X-", text="Large 2x", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_LARGE-", text="Large", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_MEDIUM-", text="Medium", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_SMALL-", text="Small", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_PORTRAIT-", text="Portrait", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_LANDSCAPE-", text="Landscape", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_TINY-", text="Tiny", enable_events=True, group_id=1)]]

    layout = [[ sg.Column(left_col), sg.VSeparator(), sg.Column(mid_col), sg.VSeparator(), sg.Column(right_col)],
                [sg.Text('Select download location'), 
                    sg.InputText(key="-DOWNLOAD_LOCATION-", default_text=str(settings['home']) + '/', readonly=True, enable_events=True), 
                    sg.FolderBrowse(key="-DOWNLOAD_BROWSER-", target="-DOWNLOAD_LOCATION-", initial_folder=str(settings['home']) + "/")],
                [sg.Button(button_text='Download', key="-DOWNLOAD-"), sg.Button(button_text='Exit', key="-EXIT-"),
                    sg.Button(button_text='Change Settings', key="-CHANGE_SETTINGS-")]]

    return sg.Window('Pexels Collection Downloader', layout), collections

def main():
    window, settings = None, load_settings(settings_file, default_settings)

    while True:             # Event Loop
        if window is None:
            if settings == default_settings:
                # event, values, collections = create_settings_window(settings).read(close=True)
                event, values = create_settings_window(settings).read(close=True)
                if event == '-SAVE-':
                    save_settings(settings_file, settings, values)
            window, collections = create_main_window(settings)

        event, values = window.read()
        
        print(f"event: {event}")
        print(values)
        
        if event in (sg.WIN_CLOSED, '-EXIT-'):
            break

        # Select a collection from the listbox
        if event == '-LIST-':
            print(values['-LIST-'][0])
            selection = [i for i in collections if values['-LIST-'][0] == i['title']][0]
            print(f"selection: {selection}")

            window['-DESCRIPTION-'].update(f"Title: {selection['title']}\n"
                                            f"ID: {selection['id']}\n"
                                            f"Description: {selection['description']}\n"
                                            f"Total media count: {selection['media_count']}\n"
                                            f"Photos count: {selection['photos_count']}\n"
                                            f"Videos count: {selection['videos_count']}")

        # Click on download browser button
        if event == '-DOWNLOAD_LOCATION-':
            print(event)
            print(values)
            window['-DOWNLOAD_LOCATION-'].update(values['-DOWNLOAD_LOCATION-'] + "/")

        # Click on download button itself
        if event == '-DOWNLOAD-':
            if values['-LIST-']:
                auth = {'Authorization': str(settings["pexels_api_key"])}
                collection_media = get_collection_media(f"https://api.pexels.com/v1/collections/{selection['id']}", selection['media_count'], auth)
                # photos = [i['src']['original'] for i in collection_media if i['type'] == 'Photo']
                
                # Check the selected quality
                radio_keys = ["-QUALITY_ORIGINAL-",
                    "-QUALITY_2X-",
                    "-QUALITY_LARGE-",
                    "-QUALITY_MEDIUM-",
                    "-QUALITY_SMALL-",
                    "-QUALITY_PORTRAIT-",
                    "-QUALITY_LANDSCAPE-",
                    "-QUALITY_TINY-"]

                radio_values = ["original",
                    "large2x",
                    "large",
                    "medium",
                    "small",
                    "portrait",
                    "landscape",
                    "tiny", ]
                
                radio_quality = "original"

                for i in range(len(radio_keys)):
                    if values[radio_keys[i]]:
                        radio_quality = radio_values[i]
                
                print(f"radio_quality: {radio_quality}")

                photos = [i['src'][radio_quality] for i in collection_media if i['type'] == 'Photo']
                print(f"total photos in {selection['title']}: {len(photos)}")
                videos = ["https://www.pexels.com/video/" + str(i['id']) + "/download" for i in collection_media if i['type'] == 'Video']
                print(f"total videos in {selection['title']}: {len(videos)}")
                print(f"selection media count: {len(photos) + len(videos)}")
                # pp.pprint(photos)
                # pp.pprint(videos)
                download_media(photos, values['-DOWNLOAD_LOCATION-'], Media.photo)
                download_media(videos, values['-DOWNLOAD_LOCATION-'], Media.video)

        # Click on change settings button
        if event == '-CHANGE_SETTINGS-':
            event, values = create_settings_window(settings).read(close=True)
            if event == '-SAVE-':
                window.close()
                window = None
                save_settings(settings_file, settings, values)

    window.close()
main()
