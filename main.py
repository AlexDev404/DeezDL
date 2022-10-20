import deezdl
import json, ffmpeg, os, re, requests
from urllib.parse import urlparse
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error


# Query

schemaPath = os.path.join(os.getcwd(), "deezdl/schema/TrackFull.json")
schema = json.load(open(schemaPath))
TId = input("Track Link: ")
TId = urlparse(TId)
schema["variables"]["trackId"] = os.path.basename(TId.path)

metadata = deezdl.authorize(schema)
metadata = metadata["data"]["track"]

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
deezdl.download(metadata["artwork"], os.path.join(os.getcwd(), "temp"), metadata["id"])

# Sift through YouTube for the track and download m4a format
deezdl.search(f"{metadata['artist']} - {metadata['title']}", metadata)
stream = ffmpeg.input(os.path.join(os.getcwd(), f"temp/{metadata['id']}"))
stream = ffmpeg.output(stream, os.path.join(os.getcwd(), f"temp/{metadata['id']}.mp3"))
ffmpeg.run(stream)

# Tagging starts
thisMP3 = os.path.join(os.getcwd(), f"temp/{metadata['id']}.mp3")
mp3 = EasyID3(thisMP3)

thisID = metadata["id"]
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
# tags = mp3.get_tags()
# print(tags)

# Tagging ends


# Add cover art
mp3 = MP3(thisMP3, ID3=ID3)
try:
    mp3.add_tags()
except error:
    pass
# print(mp3.getall('APIC'))
coverpath = os.path.join(os.getcwd(), f"temp/{thisID}.jpg")
cover = open(coverpath, "rb")
mp3.tags.add( APIC(
        mime='image/jpeg',
        type=3,  # 3 is for album art
        desc=u'Cover',
        data=cover.read()  # Reads and adds album art
    ))
# print(mp3.getall('APIC'))
# End cover art


# Cleanup
# Remove redundant files
cover.close()
mp3.save()
os.remove(coverpath)
os.remove(os.path.join(os.getcwd(), f"temp/{thisID}"))

# Rename accordingly
fname = f"{metadata['artist']} - {metadata['title']}"
fname = re.sub(r'[<>:"\/\\|?*]+', ' -', fname)
os.rename(thisMP3, os.path.join(os.getcwd(), f"temp/{fname}.mp3"))
