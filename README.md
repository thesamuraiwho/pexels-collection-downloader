# Pexels Collection Downloader

The Pexels Collection Downloader is an app to download collections from your Pexels account easily.

## Limitations and Caveats

* There are rate limits on the API. So too many requests too often will cause issues. Currently, as of the time of writing, the rate is maxed at 200 requests/hour and 20k requests/month.
* Changes on the Pexels web interface may not be updated in the app immediately. Waiting a bit may bring these changes to the app but times may vary.
* This app is not officially supported by Pexels.
* There is not a robust error handling setup yet so if you have issues with the app, try backing up and deleting the `settings.json` file.

## Steps

1. Create a [Pexels account](https://www.pexels.com/) and request a [Pexels API key](https://www.pexels.com/api/)
   1. The API request will require a project name, selection of a use, entry of a description, and agreeing to the terms of service.
      1. Enter any project name, select personal or applicable use, description can be anything descriptive (here something like "Using API for use in downloading and accessing resources easily"), and read and agree to the terms of service.
         1. Keep in mind the agreement may change but for most uses the limit per hour is ~200 requests so downloading too much too many times in an hour may cause issues for you when downloading. This can be remediated by waiting until the limit is reset the following hour.
2. Create a folder and download the latest release of the [Pexels Collection Downloader](https://github.com/thesamuraiwho/pexels-collection-downloader/releases) into that folder.
3. Open the application, enter your API key from step 1 and select the directory you want to act as your home folder for the downloads.
4. Select the collection you want and settings you want, then click download.

### Extras

* *View Downloads* button allows you to examine your downloads in the download location.

## Credits

Thank you everyone who has contributed to this project, especially Brian Le for their work on QA, their feedback, and motivation.

This application is built as part of [100DaysOfCode](https://www.100daysofcode.com/) and is built using [PySimpleGui](https://pysimplegui.readthedocs.io/en/latest/)

## Build From Source

1. Download the source code.
2. Create a virtual environment and activate it. 
   1. On windows:
      1. Install virutalenv: `pip isntall virtualenv`
      2. Create virtualenv: `virtualenv -p python env`
      3. Activate env: `source env/Scripts/activate`
3. Install the requirements from the `requirements.txt` file: `pip install -r reqirements.txt`
4. Build with `pyinstaller -wF main.py -n pexels-collection-downloader`
