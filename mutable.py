from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import os
def input_audio_path(): # input audio file path (.mp3)
    filepath = input('Enter the Path to the audio file: ')
    if os.path.isfile(filepath) and filepath.endswith('mp3'):
        return filepath
    else:
        print('Wrong Path Entered, TRY AGAIN!') # warning message
        filepath = input_audio_path()
        return filepath
def input_cover_path(): # input cover picture path (.png) or (.jpg)
    cover_path = input('Enter the Path to the album art:')
    if os.path.isfile(cover_path) and (cover_path.endswith('png') or cover_path.endswith('jpg')):
        return cover_path
    else:
        print('Wrong Path Entered, TRY AGAIN!') # warning message
        cover_path = input_cover_path()
        return cover_path
if __name__ == '__main__':
    audio_path = input_audio_path()
    picture_path = input_cover_path()
    audio = MP3(audio_path, ID3=ID3)
    # adding ID3 tag if it is not present
    try:
        audio.add_tags()
    except error:
        pass
    audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(picture_path,'rb').read()))
    # edit ID3 tags to open and read the picture from the path specified and assign it
    audio.save()  # save the current changes