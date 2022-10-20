import os
import requests
from youtube_dl import YoutubeDL


def search(arg, metadata):
        YDL_OPTIONS = {'format': 'm4a', 'noplaylist': 'True',
                       'outtmpl': os.path.join(os.getcwd(), f"temp/{metadata['id']}")}
        with YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                requests.get(arg)
            except:
                video = ydl.extract_info(f"ytsearch:{arg}", download=True)['entries'][0]
            else:
                video = ydl.extract_info(arg, download=True)

        return video
