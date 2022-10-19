import json
import ffmpeg
import os
import requests
from urllib.parse import urlparse
from mutagen.easyid3 import EasyID3
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


def download(url, path):
    url = str(url)
    if not path:
        path = os.getcwd()
    else:
        path = os.path.join(path)
    g = requests.get(url, allow_redirects=True)
    url = urlparse(url)
    os.makedirs(path, exist_ok=True)
    path = os.path.join(path, os.path.basename(url.path))
    open(path, 'wb').write(g.content)


# Query

r = r"""{
    "operationName": "TrackFull",
    "variables": {
        "trackId": "",
        "relatedAlbumsFirst": 0
    },
	"query": "query TrackFull($trackId: String!, $relatedAlbumsFirst: Int) {\r\n  track(trackId: $trackId) {\r\n    ...TrackMasthead\r\n    ...TrackLyrics\r\n    ...TrackRelatedAlbums\r\n    __typename\r\n  }\r\n}\r\n\r\nfragment TrackMasthead on Track {\r\n  ...TrackBase\r\n  duration\r\n  isExplicit\r\n  __typename\r\n}\r\n\r\nfragment TrackBase on Track {\r\n  id\r\n  title\r\n  ...TrackContributors\r\n  album {\r\n    id\r\n    displayTitle\r\n    cover {\r\n      small: urls(pictureRequest: {width: 100, height: 100})\r\n      medium: urls(pictureRequest: {width: 264, height: 264})\r\n      large: urls(pictureRequest: {width: 500, height: 500})\r\n      explicitStatus\r\n      __typename\r\n    }\r\n    __typename\r\n  }\r\n  __typename\r\n}\r\n\r\nfragment TrackContributors on Track {\r\n  contributors {\r\n    edges {\r\n      cursor\r\n      roles\r\n      node {\r\n        ... on Artist {\r\n          id\r\n          name\r\n          picture {\r\n            small: urls(pictureRequest: {width: 100, height: 100})\r\n            medium: urls(pictureRequest: {width: 264, height: 264})\r\n            large: urls(pictureRequest: {width: 500, height: 500})\r\n            copyright\r\n            explicitStatus\r\n            __typename\r\n          }\r\n          __typename\r\n        }\r\n        __typename\r\n      }\r\n      __typename\r\n}\r\n    __typename\r\n  }\r\n  __typename\r\n}\r\n\r\nfragment TrackLyrics on Track {\r\n  id\r\n  lyrics {\r\n    id\r\n    copyright\r\n    synchronizedLines {\r\n      line\r\n      __typename\r\n    }\r\n    text\r\n    writers\r\n    __typename\r\n  }\r\n  __typename\r\n}\r\n\r\nfragment TrackRelatedAlbums on Track {\r\n  relatedTracks(first: $relatedAlbumsFirst) {\r\n    edges {\r\n      node {\r\n        ...TrackBase\r\n        __typename\r\n      }\r\n      __typename\r\n    }\r\n    __typename\r\n  }\r\n  __typename\r\n}"
    
}"""

rq = json.loads(r)

TId = input("Track Link: ")
TId = urlparse(TId)
rq["variables"]["trackId"] = os.path.basename(TId.path)

# Login

auth_endpoint = requests.get('https://auth.deezer.com/login/anonymous?jo=p')
auth = auth_endpoint.json()["jwt"]

headers = {'Content-type': 'application/json', 'Authorization': f"Bearer {auth}"}
# print(rq)

z = requests.post('https://pipe.deezer.com/api', data=json.dumps(rq), headers=headers)
metadata = z.json()
metadata = metadata["data"]["track"];

# Metadata

_meta = {
    "id": metadata["id"],  # Debug
    "artwork": "BUFFER",  # Artwork
    "duration": "INT",  # Info
    #######################
    "artist": "STRING",  # Track Artist
    "album": "STRING",  # Album Name
    "title": "STRING",  # Song Title
    "tracknumber": "0",  # Track #
    "comment": "YT_URL",  # YouTube URL
    "year": "0",  # Year of Composition
    # "genre": "255",  # Genre (12 - Other)
    "composer": "STRING"
    #######################
}

# Cleanup

# ARTWORK
# Album Cover
artwork = metadata["album"]["cover"]["large"][0]
print("Artwork: " + artwork)
_meta["artwork"] = artwork

# TRACK / ALBUM NAME
print("Track Title: " + metadata["title"])
print("Album Name: " + metadata["album"]["displayTitle"])
_meta["title"] = metadata["title"]
_meta["album"] = metadata["album"]["displayTitle"]

# ARTISTS

artists = ""

for artist in metadata["contributors"]["edges"]:
    if artists == "":
        artists = artist["node"]["name"]
        _meta["composer"] = artist["node"]["name"]
    else:
        artists = artists + " and " + artist["node"]["name"]

print("Artist(s): " + artists)
_meta["artist"] = artists
# DURATION (I don't know who needs this)
# Round to 3 decimal places

print("Length: " + str(round(int(metadata["duration"]) / 60, 3)) + " minutes")
_meta["duration"] = metadata["duration"]

# After we're done, we do a full rewrite
metadata = _meta
# print(metadata)

# Download artwork
download(metadata["artwork"], os.path.join(os.getcwd(), "temp"))

# Sift through YouTube for the track and download m4a format
search(f"{metadata['artist']} - {metadata['title']}", metadata)
stream = ffmpeg.input(os.path.join(os.getcwd(), f"temp/{metadata['id']}"))
stream = ffmpeg.output(stream, os.path.join(os.getcwd(), f"temp/{metadata['id']}.mp3"))
ffmpeg.run(stream)

# Tagging starts

mp3 = EasyID3(os.path.join(os.getcwd(), f"temp/{metadata['id']}.mp3"))

del metadata["id"]
del metadata["artwork"]
del metadata["duration"]
EasyID3.RegisterTextKey('comment', 'COMM')
for prop in metadata:
    # print(prop)
    try:
        mp3[prop] = metadata[prop]
    except Exception as e:
        print(f"Exception {e} while trying to set {prop}")

mp3.save()
# Get all tags.
tags = mp3.get_tags()
print(tags)

# Tagging ends

# Cleanup

os.remove(os.path.join(os.getcwd(), f"temp/{_meta['id']}"))
