# Author: Brandon Le

# Includes code from https://pysimplegui.readthedocs.io/en/latest/cookbook/
# Copyright 2020 PySimpleGUI.com
# Licensed under LGPL-3
# Includes code from https://sempioneer.com/python-for-seo/how-to-download-images-in-python/#Method_One_How_To_Download_Multiple_Images_From_A_Python_List
# Includes code from Jason Yang: https://stackoverflow.com/a/66868963

import PySimpleGUI as sg
import os
import requests
import json
from json import (load as jsonload, dump as jsondump)
from os import path
import math
import pprint
import enum
from datetime import datetime
import webbrowser

# Globals
pp = pprint.PrettyPrinter(indent=4)
monthly_req_left = 0
req_quota_reset = 0
api_key_valid = False
home_dir_valid = False
hourly_limit_reached = False

# Classes
class Media(enum.Enum):
    photo_video = 0
    photo = 1
    video = 2

# Constants
THEME = "Black"
PER_PAGE = 80
COLLECTION_API = "https://api.pexels.com/v1/collections/"

# "Map" from the settings dictionary keys to the window's element keys
SETTINGS_KEYS_TO_ELEMENT_KEYS = {"pexels_api_key": "-PEXELS API KEY-", "home": "-HOME-"}

# Create the directories
directories = ["collections_data", "downloads"]
parent_dir = os.getcwd()

for i in directories:
    path = os.path.join(parent_dir, i)
    # If the folder doesn't already exist, create it
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except OSError as error:
            print(error)

# Setup settings.json file
default_settings = {"pexels_api_key": "", "home": f"{parent_dir}"}
settings_file = "settings.json"

# Check API Key
def check_api_key(settings):
    auth = {'Authorization': str(settings["pexels_api_key"])}
    print(f'settings["pexels_api_key"]: {settings["pexels_api_key"]}')
    req = requests.get(COLLECTION_API, headers=auth)

    status = req.status_code
    if status == 200:
        print("OK")
        api_key_valid = True
        return True
    elif status == 401 or status == 403:
        if status == 401:
            print("Unauthorized")
        else:
            print("Forbidden")
        api_key_valid = False
    elif status == 429:
        print("Too many requests")
        hourly_limit_reached = True
    else:
        print(req.status_code)
    
    return False

# Check Home directory
def check_home_dir(settings):
    if os.path.exists(str(settings['home'])):
        return True
    else:
        return False


# Download media
def download_media(urls, download_dir, media_type):
    broken_urls = []
    good_urls = []
    for media in urls:
        # We can split the file based upon / and extract the last split within the python list below:
        if media_type == Media.photo:
            file_name = download_dir + (media.split('/')[-1]).split("?")[0]
        else:
            file_name = download_dir + media.split('/')[-2] + ".mp4"
        # Now let's send a request to the image URL:
        r = requests.get(media, stream=True)
        # We can check that the status code is 200 before doing anything else:
        if r.status_code == 200:
            # This command below will allow us to write the data to a file as binary:
            with open(file_name, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
            good_urls.append(media)
        else:
            # We will write all of the images back to the broken_images list:
            broken_urls.append(media)
    return broken_urls, good_urls

def get_json(url, auth, total_collections, field):
    count = 0
    json = []
    iterations = 0
    if total_collections / PER_PAGE < 1:
        iterations = 1
    else:
        iterations = math.ceil(total_collections / PER_PAGE)
    while count < iterations:
        req = requests.get(f"{url}?page={count + 1}&per_page={PER_PAGE}", headers=auth)
        monthly_req_left = req.headers['X-Ratelimit-Remaining']
        req_quota_reset = int(req.headers['X-Ratelimit-Reset'])

        print(f"{monthly_req_left}\n{req_quota_reset}\n")
        
        json += req.json()[field]
        count += 1
    return json

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
                [sg.Button(key='-SAVE-', button_text='Save'), sg.Button(button_text='Exit', key="-EXIT-"), sg.Text(key='-OUTPUT-', text="", text_color="red", size=(30,1))],
                [sg.Text(key='URL https://www.pexels.com/api/', text='Link to Pexels API', tooltip='https://www.pexels.com/api/', enable_events=True)]]
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
    req = requests.get(COLLECTION_API, headers=auth)
    total_collections = req.json()["total_results"]
    collections = get_json(f"{COLLECTION_API}", auth, total_collections, 'collections')
    monthly_req_left = req.headers['X-Ratelimit-Remaining']
    req_quota_reset = int(req.headers['X-Ratelimit-Reset'])

    left_col = [[sg.Text("Collections")],
                    [sg.HorizontalSeparator()],
                    [sg.Listbox(values=sorted([i['title'] for i in collections], key=str.lower), 
                        size=(20, total_collections), key='-LIST-', enable_events=True)]]

    media_opt_panel = [[sg.Text("Media Selection")],
                            [sg.HorizontalSeparator()],
                            [sg.Radio(key="-MEDIA_ALL-", text="Photos and Videos", default=True, enable_events=True, 
                                group_id=2)],
                            [sg.Radio(key="-MEDIA_PHOTOS-", text="Photos Only", enable_events=True, 
                                group_id=2)],
                            [sg.Radio(key="-MEDIA_VIDEOS-", text="Videos Only", enable_events=True, 
                                group_id=2)]]
    request_panel = [[sg.Text("Hourly request limit: 200")],
                        [sg.HorizontalSeparator()],
                        [sg.Text(text="Monthly requests left:")],
                        [sg.Text(key="-REMAINING_REQ-", text=f"{monthly_req_left}")],
                        [sg.HorizontalSeparator()],
                        [sg.Text(text="Request quota resets:")],
                        [sg.Text(key="-REQ_QUOTA_RESET-", text=f"{datetime.utcfromtimestamp(req_quota_reset).strftime('%Y-%m-%dT%H:%M')}")]]
    mid_col = [[sg.Text("Collection Description")],
                [sg.HorizontalSeparator()],
                [sg.MLine(size=(20, 10), key='-DESCRIPTION-')]] + [[sg.Text()]] + request_panel #+ media_opt_panel
    right_col = media_opt_panel + [[sg.HorizontalSeparator()], [sg.HorizontalSeparator()]] + [[sg.Text('Collection Photo Quality')],
                    [sg.HorizontalSeparator()],
                    [sg.Radio(key="-QUALITY_ORIGINAL-", text="Original", default=True, enable_events=True, 
                        group_id=1)],
                    [sg.Radio(key="-QUALITY_2X-", text="Large 2x", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_LARGE-", text="Large", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_MEDIUM-", text="Medium", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_SMALL-", text="Small", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_PORTRAIT-", text="Portrait", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_LANDSCAPE-", text="Landscape", enable_events=True, group_id=1)],
                    [sg.Radio(key="-QUALITY_TINY-", text="Tiny", enable_events=True, group_id=1)],]
    layout = [[ sg.Column(left_col), sg.VSeparator(), sg.Column(mid_col), sg.VSeparator(), 
                    sg.Column(right_col)],
                [sg.Text('Select download location'), 
                    sg.InputText(key="-DOWNLOAD_LOCATION-", default_text=str(settings['home']) + "/", 
                        readonly=True, disabled_readonly_background_color="#4d4d4d",enable_events=True), 
                    sg.FolderBrowse(key="-DOWNLOAD_BROWSER-", target="-DOWNLOAD_LOCATION-", 
                        initial_folder=str(settings['home']) + "/")],
                [sg.FileBrowse(key="-OUTPUT_VIEWER-", button_text="View Downloads", 
                    file_types=(("ALL Files", "*.*"), ("JPEG Files", "*.jpeg"), ("MP4 Files", "*.mp4"),),
                    initial_folder=str(settings['home']) + "/", enable_events=True)],
                [sg.MLine(key="-OUTPUT-" + sg.WRITE_ONLY_KEY, size=(74, 5), write_only=True)],
                [sg.Button(button_text='Download', key="-DOWNLOAD-"), 
                    sg.Button(button_text='Exit', key="-EXIT-"),
                    sg.Button(button_text='Change Settings', key="-CHANGE_SETTINGS-")],
                [sg.Text(key='URL https://github.com/thesamuraiwho', text='Developed by TheSamuraiWho', tooltip='https://github.com/thesamuraiwho', enable_events=True), 
                    sg.VerticalSeparator(), 
                    sg.Text(key='URL https://www.pexels.com/', text='Photos provided by Pexels', tooltip='https://www.pexels.com/', enable_events=True),
                    sg.VerticalSeparator(),
                    sg.Button(button_text='Credits', key="-CREDITS-")]]

    return sg.Window('Pexels Collection Downloader', layout), collections

def main():
    window, settings = None, load_settings(settings_file, default_settings)

    quality_keys = ["-QUALITY_ORIGINAL-",
        "-QUALITY_2X-",
        "-QUALITY_LARGE-",
        "-QUALITY_MEDIUM-",
        "-QUALITY_SMALL-",
        "-QUALITY_PORTRAIT-",
        "-QUALITY_LANDSCAPE-",
        "-QUALITY_TINY-"]
    quality_values = ["original",
        "large2x",
        "large",
        "medium",
        "small",
        "portrait",
        "landscape",
        "tiny"]
    quality_selection = "original"

    media_keys = ["-MEDIA_ALL-", "-MEDIA_PHOTOS-", "-MEDIA_VIDEOS-"]
    media_values = ["photo_video", "photo", "video"]
    media_selection = "photo_video"

    while True:             # Event Loop
        if window is None:
            # If first time setup, create the settings window
            if settings == default_settings:
                window = create_settings_window(settings)
                api_check = check_api_key(settings)
                home_check = check_home_dir(settings)
                print(f"api_check: {api_check}")
                print(f"home_check: {home_check}")
                while not api_check or not home_check:
                    event, values = window.read()
                    print(f"event: {event}")
                    print(f"values: {values}")
                    settings = {"pexels_api_key": f"{values['-PEXELS API KEY-']}", "home": f"{values['-HOME-']}"}

                    if event == '-SAVE-':
                        api_check = check_api_key(settings)
                        home_check = check_home_dir(settings)
                        print(f"api_check: {api_check}")
                        print(f"home_check: {home_check}")
                        if api_check and home_check:
                            save_settings(settings_file, settings, values)
                            window.close()
                        elif not api_check and home_check:
                            window['-OUTPUT-'].update("Invalid API Key")
                        elif api_check and not home_check:
                            window['-OUTPUT-'].update("Invalid Home directory")
                        else:
                            window['-OUTPUT-'].update("Invalid API Key or Home directory")
                    
                    # TODO: Clean exit
                    if event in (sg.WIN_CLOSED, '-EXIT-'):
                        exit()

                    # Open URLs if they are clicked
                    if event.startswith("URL"):
                        url = event.split(" ")[1]
                        webbrowser.open(url)
            window, collections = create_main_window(settings)

        event, values = window.read()
        print(f"event: {event}")
        print(f"values: {values}")
        
        if event in (sg.WIN_CLOSED, '-EXIT-'):
            break

        # Select a collection from the listbox
        if event == '-LIST-':
            selection = [i for i in collections if values['-LIST-'][0] == i['title']][0]
            window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Selecting: {selection['title']}")
            window['-DESCRIPTION-'].update(f"Title: {selection['title']}\n"
                                            f"ID: {selection['id']}\n"                                            
                                            f"Total media count: {selection['media_count']}\n"
                                            f"Photos count: {selection['photos_count']}\n"
                                            f"Videos count: {selection['videos_count']}\n"
                                            f"\nDescription: {selection['description']}\n\n")

        # Click on download browser button
        if event == '-DOWNLOAD_LOCATION-':
            if values['-DOWNLOAD_LOCATION-'][-1] != "/":
                window['-DOWNLOAD_LOCATION-'].update(values['-DOWNLOAD_LOCATION-'] + "/")

        # Click on download button itself
        if event == '-DOWNLOAD-':
            if values['-LIST-']:
                auth = {'Authorization': str(settings["pexels_api_key"])}
                collection_media = get_json(f"{COLLECTION_API}{selection['id']}", auth, 
                    selection['media_count'], 'media')
                    
                # Create photos and video lists for download, download, and return successful/failed urls
                if media_selection == "photo_video":
                    photos = [i['src'][quality_selection] for i in collection_media if i['type'] == 'Photo']
                    videos = ["https://www.pexels.com/video/" + str(i['id']) + "/download" for i in collection_media if i['type'] == 'Video']
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Total photos in {selection['title']}: {len(photos)}")
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Total videos in {selection['title']}: {len(videos)}")
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Total media count in {selection['title']}: {len(photos) + len(videos)}")
                    broken_photos, good_photos = download_media(photos, values['-DOWNLOAD_LOCATION-'], Media.photo)
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Good photo urls: {good_photos}")
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Broken photo urls: {broken_photos}")
                    broken_videos, good_videos = download_media(videos, values['-DOWNLOAD_LOCATION-'], Media.video)
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Good video urls: {good_videos}")
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Broken video urls: {broken_videos}")
                elif media_selection == "photo":
                    photos = [i['src'][quality_selection] for i in collection_media if i['type'] == 'Photo']
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Total photos in {selection['title']}: {len(photos)}")
                    broken_photos, good_photos = download_media(photos, values['-DOWNLOAD_LOCATION-'], Media.photo)
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Good photo urls: {good_photos}")
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Broken photo urls: {broken_photos}")
                else:
                    videos = ["https://www.pexels.com/video/" + str(i['id']) + "/download" for i in collection_media if i['type'] == 'Video']
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Total videos in {selection['title']}: {len(videos)}")
                    broken_videos, good_videos = download_media(videos, values['-DOWNLOAD_LOCATION-'], Media.video)
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Good video urls: {good_videos}")
                    window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Broken video urls: {broken_videos}")
                
                window['-REMAINING_REQ-'].update(f"{monthly_req_left}")
                window['-REQ_QUOTA_RESET-'].update(f"{datetime.utcfromtimestamp(req_quota_reset).strftime('%Y-%m-%dT%H:%M')}")

        # Show photo quality radio selection
        if event in quality_keys:
            # Check the selected quality
            for i in range(len(quality_keys)):
                if values[quality_keys[i]]:
                    quality_selection = quality_values[i]
            window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Selecting photo quality: {quality_selection}")
        
        # Show media radio selection
        if event in media_keys:
            # Check for selected media option
            for i in range(len(media_keys)):
                if values[media_keys[i]]:
                    media_selection = media_values[i]
            window['-OUTPUT-' + sg.WRITE_ONLY_KEY].print(f"Selecting media option: {media_selection}")
        
        # TODO: Fix change settings button
        # Click on change settings button
        if event == '-CHANGE_SETTINGS-':
            event, values = create_settings_window(settings).read(close=True)
            if event == '-SAVE-':
                window.close()
                window = None
                save_settings(settings_file, settings, values)

            # setting_window = create_settings_window(settings)
            # api_check = False
            # home_check = False
            # print(f"api_check: {api_check}")
            # print(f"home_check: {home_check}")
            # while not api_check or not home_check:
            #     setting_event, setting_values = setting_window.read()
            #     print(f"event: {event}")
            #     print(f"values: {values}")
            #     setting_window = {"pexels_api_key": f"{setting_values['-PEXELS API KEY-']}", "home": f"{setting_values['-HOME-']}"}

            #     if setting_event == '-SAVE-':
            #         api_check = check_api_key(settings)
            #         home_check = check_home_dir(settings)
            #         print(f"api_check: {api_check}")
            #         print(f"home_check: {home_check}")
            #         if api_check and home_check:
            #             save_settings(settings_file, settings, setting_values)
            #             setting_window.close()
            #         elif not api_check and home_check:
            #             setting_window['-OUTPUT-'].update("Invalid API Key")
            #         elif api_check and not home_check:
            #             setting_window['-OUTPUT-'].update("Invalid Home directory")
            #         else:
            #             setting_window['-OUTPUT-'].update("Invalid API Key or Home directory")
                
            #     # TODO: Clean exit
            #     if setting_event in (sg.WIN_CLOSED, '-EXIT-'):
            #         setting_window.close()

            #     # Open URLs if they are clicked
            #     if setting_event.startswith("URL"):
            #         url = setting_event.split(" ")[1]
            #         webbrowser.open(url)
        
        # Open URLs if they are clicked
        if event.startswith("URL"):
            url = event.split(" ")[1]
            webbrowser.open(url)

        # Open a popup of the contributors in the credits
        if event == "-CREDITS-":
            sg.popup_ok('Thank you everyone who has contributed to this project, especially:\n', 
                'Brian Le: QA, feedback, and motivator', title='Credits', keep_on_top=True)

    window.close()
main()
