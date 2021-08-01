# Author: Brandon Le

# Includes code from https://pysimplegui.readthedocs.io/en/latest/cookbook/
# Copyright 2020 PySimpleGUI.com
# Licensed under LGPL-3
# Includes code from https://sempioneer.com/python-for-seo/how-to-download-images-in-python/#Method_One_How_To_Download_Multiple_Images_From_A_Python_List
# Includes code from Jason Yang: https://stackoverflow.com/a/66868963

import PySimpleGUI as sg
import os
import requests
from json import (load as jsonload, dump as jsondump)
from os import path
import math
import enum
from datetime import datetime
import webbrowser

# Globals
# monthly_req_left = 0
# req_quota_reset = 0
api_key_valid = False
home_dir_valid = False

# Classes
class Media(enum.Enum):
    photo_video = 0
    photo = 1
    video = 2

# Constants
THEME = "Black"
PER_PAGE = 80
COLLECTION_API = "https://api.pexels.com/v1/collections/"
QUALITY_KEYS = ["-QUALITY_ORIGINAL-", "-QUALITY_2X-", "-QUALITY_LARGE-", "-QUALITY_MEDIUM-",
    "-QUALITY_SMALL-", "-QUALITY_PORTRAIT-", "-QUALITY_LANDSCAPE-", "-QUALITY_TINY-"]
QUALITY_VALUES = ["original", "large2x", "large", "medium", "small",
    "portrait", "landscape", "tiny"]
MEDIA_KEYS = ["-MEDIA_ALL-", "-MEDIA_PHOTOS-", "-MEDIA_VIDEOS-"]
MEDIA_VALUES = ["photo_video", "photo", "video"]

# "Map" from the settings dictionary keys to the window's element keys
SETTINGS_KEYS_TO_ELEMENT_KEYS = {"pexels_api_key": "-PEXELS API KEY-", "home": "-HOME-"}

# Create the directories
# directories = ["collections_data", "downloads"]
parent_dir = os.getcwd()

# for i in directories:
#     path = os.path.join(parent_dir, i)
#     if not os.path.exists(path): # If the folder doesn't already exist, create it
#         try:
#             os.mkdir(path)
#         except OSError as error:
#             print(error)

# Setup settings.json file
default_settings = {"pexels_api_key": "", "home": f"{parent_dir}"}
settings_file = "settings.json"

def check_api_key(settings): # Check API Key
    auth = {'Authorization': str(settings["pexels_api_key"])}
    # print(f'settings["pexels_api_key"]: {settings["pexels_api_key"]}')
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
    return False

def check_home_dir(settings): # Check Home directory
    return os.path.exists(str(settings['home']))

def download_media(urls, download_dir, media_type):
    """Download media
    urls: list of strings, urls of files to download
    download_dir: string, directory to download media to
    media_type: Media enum, type of media
    """
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
        json += req.json()[field]
        count += 1
    return json

def load_settings(settings_file, default_settings):
    """Load settings from settings.json
    settings_file: string, filename
    default_settings: dict, default settings for the app
    """
    try:
        with open(settings_file, 'r') as f:
            settings = jsonload(f)
    except Exception as e:
        settings = default_settings
    return settings

def save_settings(settings_file, settings, values):
    if values:      # if there are stuff specified by another window, fill in those values
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:  # update window with the values read from settings file
            try:
                settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
            except Exception as e:
                print(f'{e}\tProblem updating settings from window values. Key = {key}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f)

    return settings

##################### Make a settings window #####################
def create_settings_window(settings):
    sg.theme(THEME)

    def TextLabel(text): return sg.Text(text+':', justification='r', size=(15,1))

    layout = [  [TextLabel('Pexels API key'), sg.Input(key='-PEXELS API KEY-')],
                [TextLabel('Home directory'), sg.Input(key='-HOME-'), sg.FolderBrowse(target='-HOME-')],
                [sg.Button(key='-SAVE-', button_text='Save'), sg.Button(button_text='Exit', key="-SETTINGS_EXIT-"), 
                    sg.Text(key='-SETTINGS_OUTPUT-', text="", text_color="red", size=(30,1))],
                [sg.Text(key='URL https://www.pexels.com/api/', text='Link to Pexels API', tooltip='https://www.pexels.com/api/', enable_events=True)]]
    window = sg.Window('Settings', layout, keep_on_top=True, finalize=True, no_titlebar=False)

    for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:   # update window with the values read from settings file
        try:
            window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=settings[key])
        except Exception as e:
            print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

    return window

##################### Main Program Window & Event Loop #####################
def create_main_window(settings):
    sg.theme(THEME)

    def Radio(key, text, group_id, default=False): return sg.Radio(key=key, text=text, group_id=group_id, 
        default=default, enable_events=True)

    def Link(url, text): return sg.Text(key=f'URL {url}', text=text, tooltip=url, enable_events=True)

    auth = {'Authorization': str(settings["pexels_api_key"])}
    req = requests.get(COLLECTION_API, headers=auth)
    if req.status_code == 200:
        total_collections = req.json()["total_results"]
        collections = get_json(f"{COLLECTION_API}", auth, total_collections, 'collections')
        # monthly_req_left = req.headers['X-Ratelimit-Remaining']
        # req_quota_reset = int(req.headers['X-Ratelimit-Reset'])

        left_col = [[sg.Text("Collections")], [sg.HSeparator()],
                        [sg.Listbox(values=sorted([i['title'] for i in collections], key=str.lower), 
                            size=(20, total_collections), key='-LIST-', enable_events=True)]]
        media_opt_panel = [[sg.Text("Media Selection")], [sg.HSeparator()],
                                [Radio("-MEDIA_ALL-", "Photos and Videos", 2, default=True)],
                                [Radio("-MEDIA_PHOTOS-", "Photos Only", 2)],
                                [Radio("-MEDIA_VIDEOS-", "Videos Only", 2)]]
        # request_panel = [[sg.Text("Hourly request limit: 200")], [sg.HSeparator()],
        #                     [sg.Text(text="Monthly requests left:")],
        #                     [sg.Text(key="-REMAINING_REQ-", text=f"{monthly_req_left}")], [sg.HSeparator()],
        #                     [sg.Text(text="Request quota resets:")],
        #                     [sg.Text(key="-REQ_QUOTA_RESET-", text=f"{datetime.utcfromtimestamp(req_quota_reset).strftime('%Y-%m-%dT%H:%M')}")]]
        mid_col = [[sg.Text("Collection Description")], [sg.HSeparator()],
                    [sg.MLine(size=(20, 10), key='-DESCRIPTION-')]] + [[sg.Text()]] #+ request_panel
        right_col = media_opt_panel + [[sg.HSeparator()], [sg.HSeparator()]] + [[sg.Text('Collection Photo Quality')],
                        [sg.HSeparator()],
                        [Radio("-QUALITY_ORIGINAL-", "Original", 1, default=True)],
                        [Radio("-QUALITY_2X-", "Large 2x", 1)],
                        [Radio("-QUALITY_LARGE-", "Large", 1)],
                        [Radio("-QUALITY_MEDIUM-", "Medium", 1)],
                        [Radio("-QUALITY_SMALL-", "Small", 1)],
                        [Radio("-QUALITY_PORTRAIT-", "Portrait", 1)],
                        [Radio("-QUALITY_LANDSCAPE-", "Landscape", 1)],
                        [Radio("-QUALITY_TINY-", "Tiny", 1)]]
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
                    [sg.MLine(key="-OUTPUT-", size=(74, 5), write_only=True)],
                    [sg.Button(button_text='Download', key="-DOWNLOAD-"), 
                        sg.Button(button_text='Exit', key="-EXIT-"),
                        sg.Button(button_text='Change Settings', key="-CHANGE_SETTINGS-")],
                    [Link('https://github.com/thesamuraiwho', 'Developed by TheSamuraiWho'), 
                        sg.VSeparator(), 
                        Link('https://www.pexels.com/', 'Photos provided by Pexels'),
                        sg.VSeparator(),
                        sg.Button(button_text='Credits', key="-CREDITS-")]]
        return sg.Window('Pexels Collection Downloader', layout), collections
    else:
        layout = [[sg.popup("Issue with API. Please try again later.", auto_close=True,
            auto_close_duration=120, any_key_closes=True)]]
        collections = {}
        return layout, collections
   

def main():
    window, settings = None, load_settings(settings_file, default_settings)
    quality_selection = "original"
    media_selection = "photo_video"

    while True: # Event Loop
        if window is None:
            if settings == default_settings: # If first time setup, create the settings window
                window = create_settings_window(settings)
                api_check = check_api_key(settings)
                home_check = check_home_dir(settings)
                # print(f"api_check: {api_check}\nhome_check: {home_check}")
                while not api_check or not home_check:
                    event, values = window.read()
                    # print(f"event: {event}\nvalues: {values}")
                    if values:
                        settings = {"pexels_api_key": f"{values['-PEXELS API KEY-']}", "home": f"{values['-HOME-']}"}

                    if event == '-SAVE-':
                        api_check = check_api_key(settings)
                        home_check = check_home_dir(settings)
                        # print(f"api_check: {api_check}\nhome_check: {home_check}")
                        if api_check and home_check:
                            save_settings(settings_file, settings, values)
                            window.close()
                        elif not api_check and home_check:
                            window['-SETTINGS_OUTPUT-'].update("Invalid API Key")
                        elif api_check and not home_check:
                            window['-SETTINGS_OUTPUT-'].update("Invalid Home directory")
                        else:
                            window['-SETTINGS_OUTPUT-'].update("Invalid API Key or Home directory")
                    
                    if event in (sg.WIN_CLOSED, '-SETTINGS_EXIT-'):
                        exit()

                    if event.startswith("URL"): # Open URLs if they are clicked
                        url = event.split(" ")[1]
                        webbrowser.open(url)
            window, collections = create_main_window(settings)

        if collections != {}:
            event, values = window.read()
            # print(f"event: {event}")
            # print(f"values: {values}")
            
            if event in (sg.WIN_CLOSED, '-EXIT-'):
                break

            if event == '-LIST-': # Select a collection from the listbox
                selection = [i for i in collections if values['-LIST-'][0] == i['title']][0]
                window['-OUTPUT-'].print(f"Selecting: {selection['title']}")
                window['-DESCRIPTION-'].update(f"Title: {selection['title']}\n"
                                                f"ID: {selection['id']}\n"                                            
                                                f"Total media count: {selection['media_count']}\n"
                                                f"Photos count: {selection['photos_count']}\n"
                                                f"Videos count: {selection['videos_count']}\n"
                                                f"\nDescription: {selection['description']}\n\n")

            if event == '-DOWNLOAD_LOCATION-': # Click on download browser button
                if values['-DOWNLOAD_LOCATION-'][-1] != "/":
                    window['-DOWNLOAD_LOCATION-'].update(values['-DOWNLOAD_LOCATION-'] + "/")

            if event == '-DOWNLOAD-': # Click on download button itself
                if values['-LIST-']:
                    window['-OUTPUT-'].print(f"Downloading...")
                    auth = {'Authorization': str(settings["pexels_api_key"])}
                    collection_media = get_json(f"{COLLECTION_API}{selection['id']}", auth, 
                        selection['media_count'], 'media')
                    
                    # Create photos and video lists for download, download, and return successful/failed urls
                    if media_selection == "photo_video":
                        photos = [i['src'][quality_selection] for i in collection_media if i['type'] == 'Photo']
                        videos = ["https://www.pexels.com/video/" + str(i['id']) + "/download" for i in collection_media if i['type'] == 'Video']
                        window['-OUTPUT-'].print(f"Total photos in {selection['title']}: {len(photos)}")
                        window['-OUTPUT-'].print(f"Total videos in {selection['title']}: {len(videos)}")
                        window['-OUTPUT-'].print(f"Total media count in {selection['title']}: {len(photos) + len(videos)}")
                        broken_photos, good_photos = download_media(photos, values['-DOWNLOAD_LOCATION-'], Media.photo)
                        window['-OUTPUT-'].print(f"Good photo urls: {good_photos}")
                        window['-OUTPUT-'].print(f"Broken photo urls: {broken_photos}")
                        broken_videos, good_videos = download_media(videos, values['-DOWNLOAD_LOCATION-'], Media.video)
                        window['-OUTPUT-'].print(f"Good video urls: {good_videos}")
                        window['-OUTPUT-'].print(f"Broken video urls: {broken_videos}")
                    elif media_selection == "photo":
                        photos = [i['src'][quality_selection] for i in collection_media if i['type'] == 'Photo']
                        window['-OUTPUT-'].print(f"Total photos in {selection['title']}: {len(photos)}")
                        broken_photos, good_photos = download_media(photos, values['-DOWNLOAD_LOCATION-'], Media.photo)
                        window['-OUTPUT-'].print(f"Good photo urls: {good_photos}")
                        window['-OUTPUT-'].print(f"Broken photo urls: {broken_photos}")
                    else:
                        videos = ["https://www.pexels.com/video/" + str(i['id']) + "/download" for i in collection_media if i['type'] == 'Video']
                        window['-OUTPUT-'].print(f"Total videos in {selection['title']}: {len(videos)}")
                        broken_videos, good_videos = download_media(videos, values['-DOWNLOAD_LOCATION-'], Media.video)
                        window['-OUTPUT-'].print(f"Good video urls: {good_videos}")
                        window['-OUTPUT-'].print(f"Broken video urls: {broken_videos}")
            
            if event in QUALITY_KEYS: # Show photo quality radio selection
                for i in range(len(QUALITY_KEYS)): # Check the selected quality
                    if values[QUALITY_KEYS[i]]:
                        quality_selection = QUALITY_VALUES[i]
                window['-OUTPUT-'].print(f"Selecting photo quality: {quality_selection}")
            
            if event in MEDIA_KEYS: # Show media radio selection
                for i in range(len(MEDIA_KEYS)): # Check for selected media option
                    if values[MEDIA_KEYS[i]]:
                        media_selection = MEDIA_VALUES[i]
                window['-OUTPUT-'].print(f"Selecting media option: {media_selection}")
            
            if event == '-CHANGE_SETTINGS-': # Click on change settings button            
                settings_window = create_settings_window(settings)
                exit_loop = False

                while not exit_loop:
                    settings_event, settings_values = settings_window.read()
                    if settings_values:
                        settings = {"pexels_api_key": f"{settings_values['-PEXELS API KEY-']}", 
                            "home": f"{settings_values['-HOME-']}"}
                    # print(f"event: {settings_event}\nvalues: {settings_values}")

                    if settings_event == '-SAVE-':
                        api_check = check_api_key(settings)
                        home_check = check_home_dir(settings)
                        # print(f"api_check: {api_check}")
                        # print(f"home_check: {home_check}")
                        if api_check and home_check:
                            save_settings(settings_file, settings, values)
                            exit_loop = True
                            settings_window.close()
                        elif not api_check and home_check:
                            settings_window['-SETTINGS_OUTPUT-'].update("Invalid API Key")
                        elif api_check and not home_check:
                            settings_window['-SETTINGS_OUTPUT-'].update("Invalid Home directory")
                        else:
                            settings_window['-SETTINGS_OUTPUT-'].update("Invalid API Key or Home directory")
                    
                    if settings_event == '-SETTINGS_EXIT-':
                        exit_loop = True
                        settings_window.close()

                    if settings_event == sg.WIN_CLOSED:
                        pass

                    if settings_event.startswith("URL"): # Open URLs if they are clicked
                        url = settings_event.split(" ")[1]
                        webbrowser.open(url)
                window['-DOWNLOAD_LOCATION-'].update(value=str(settings['home']) + "/")
            
            # Open URLs if they are clicked
            if event.startswith("URL"):
                url = event.split(" ")[1]
                webbrowser.open(url)

            # Open a popup of the contributors in the credits
            if event == "-CREDITS-":
                sg.popup_ok('Thank you everyone who has contributed to this project, especially:\n', 
                    'Brian Le: QA, feedback, and motivator', title='Credits', keep_on_top=True)
        else:
            exit()
    window.close()
main()
