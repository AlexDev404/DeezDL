import json
import os
import requests
from urllib.parse import urlparse


def download(url):
    url = str(url)
    g = requests.get(url, allow_redirects=True)
    url = urlparse(url)
    open(os.path.basename(url.path), 'wb').write(g.content)


# Query

r = r"""{
    "operationName": "TrackFull",
    "variables": {
        "trackId": "602456552",
        "relatedAlbumsFirst": 0
    },
	"query": "query TrackFull($trackId: String!, $relatedAlbumsFirst: Int) {\r\n  track(trackId: $trackId) {\r\n    ...TrackMasthead\r\n    ...TrackLyrics\r\n    ...TrackRelatedAlbums\r\n    __typename\r\n  }\r\n}\r\n\r\nfragment TrackMasthead on Track {\r\n  ...TrackBase\r\n  duration\r\n  isExplicit\r\n  __typename\r\n}\r\n\r\nfragment TrackBase on Track {\r\n  id\r\n  title\r\n  ...TrackContributors\r\n  album {\r\n    id\r\n    displayTitle\r\n    cover {\r\n      small: urls(pictureRequest: {width: 100, height: 100})\r\n      medium: urls(pictureRequest: {width: 264, height: 264})\r\n      large: urls(pictureRequest: {width: 500, height: 500})\r\n      explicitStatus\r\n      __typename\r\n    }\r\n    __typename\r\n  }\r\n  __typename\r\n}\r\n\r\nfragment TrackContributors on Track {\r\n  contributors {\r\n    edges {\r\n      cursor\r\n      roles\r\n      node {\r\n        ... on Artist {\r\n          id\r\n          name\r\n          picture {\r\n            small: urls(pictureRequest: {width: 100, height: 100})\r\n            medium: urls(pictureRequest: {width: 264, height: 264})\r\n            large: urls(pictureRequest: {width: 500, height: 500})\r\n            copyright\r\n            explicitStatus\r\n            __typename\r\n          }\r\n          __typename\r\n        }\r\n        __typename\r\n      }\r\n      __typename\r\n}\r\n    __typename\r\n  }\r\n  __typename\r\n}\r\n\r\nfragment TrackLyrics on Track {\r\n  id\r\n  lyrics {\r\n    id\r\n    copyright\r\n    synchronizedLines {\r\n      line\r\n      __typename\r\n    }\r\n    text\r\n    writers\r\n    __typename\r\n  }\r\n  __typename\r\n}\r\n\r\nfragment TrackRelatedAlbums on Track {\r\n  relatedTracks(first: $relatedAlbumsFirst) {\r\n    edges {\r\n      node {\r\n        ...TrackBase\r\n        __typename\r\n      }\r\n      __typename\r\n    }\r\n    __typename\r\n  }\r\n  __typename\r\n}"
    
}"""

rq = json.loads(r)

# TId = input("Track ID: ")
# rq["variables"]["trackId"] = TId

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
    "artwork": "BUFFER",  # done
    "title": "STRING",  # done
    "artist": "STRING",  # done
    "album": "STRING",  # done
    "year": "INT",  # idc
    "trackN": "INT",  # idk
    "genre": "STRING",  # idek
    "comment": "SUS",  # yes
    "alb_artist": "STRING",
    "duration": "INT"
}

# Cleanup

# ARTWORK
# Album Cover
print(metadata["album"]["cover"]["large"][0])
_meta["artwork"] = metadata["album"]["cover"]["large"][0]


# TRACK / ALBUM NAME
print("Track Title: " + metadata["title"] + "\n", "Album Name: " + metadata["album"]["displayTitle"])
_meta["title"] = metadata["title"]
_meta["album"] = metadata["album"]["displayTitle"]

# ARTISTS

artists = ""

for artist in metadata["contributors"]["edges"]:
    if artists == "":
        artists = artist["node"]["name"]
        _meta["alb_artist"] = artist["node"]["name"]
    else:
        artists = artists + " and " + artist["node"]["name"]

print(artists)
_meta["artist"] = artists
# DURATION (I don't know who needs this)
# Round to 3 decimal places

print(str(round(int(metadata["duration"]) / 60, 3)) + " minutes")
_meta["duration"] = metadata["duration"]

metadata = _meta
print(metadata)

download(metadata["artwork"])
