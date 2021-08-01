# Pexels Collection Downloader

The Pexels Collection Downloader is an app to download collections from your Pexels account easily.

## Steps

1. Create a [Pexels account](https://www.pexels.com/) and request a [Pexels API key](https://www.pexels.com/api/)
2. Download the latest release of the [Pexels Collection Downloader](https://github.com/thesamuraiwho/pexels-collection-downloader/releases)
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
3. Install the requirements from the `requirements.txt` file.
4. Build with `pyinstaller -wF main.py -n pexels-collection-downloader`
