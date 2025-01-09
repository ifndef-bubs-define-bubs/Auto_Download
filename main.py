from pytubefix import YouTube
import os
import re
from pytubefix import Playlist
import subprocess

def sanitize_title(title):
    invalid_chars = ' /"\''
    translation_table = str.maketrans({ch: "_" for ch in invalid_chars})
    return title.translate(translation_table)


def download_video(yt, download_folder):
    title_safe = sanitize_title(yt.title)
    try:
        path = download_folder + "/" + title_safe + ".mp4"
        if not os.path.exists(path):
            video = yt.streams.get_highest_resolution()
            video.download(output_path=download_folder, filename=title_safe + ".mp4")
            print(f'Successfully downloaded: {yt.title}')
        else:
            print(f'Already downloaded: {yt.title}.mp4')
    except Exception as e:
        print(f'Error downloading {yt.title}: {e}')

def download_audio(yt, download_folder):
    title_safe = sanitize_title(yt.title)
    path = os.path.join(download_folder, title_safe + ".mp3")
    try:
        path = download_folder + "/" + title_safe + ".mp3"
        if not os.path.exists(path):
            ys = yt.streams.get_audio_only()
            ys.download(output_path=download_folder, filename=title_safe + "_unprocessed.mp3")
            print(f'Successfully downloaded: {yt.title}.mp3')

            subprocess.run([
                "ffmpeg", "-i", os.path.join(download_folder, title_safe + "_unprocessed.mp3"), # Input file
                "-vn",
                "-ar", "44100",
                "-ac", "2",
                "-b:a", "192k",
                "-y",
                path
            ], check=True)

            os.remove(os.path.join(download_folder, title_safe + "_unprocessed.mp3"))

        else:
            print(f'Already downloaded: {yt.title}.mp3')
    except Exception as e:
        print(f'Error downloading {yt.title}: {e}')

def download_video_playlist(pl, download_folder, start_index, end_index):
    for i in range(start_index, end_index):
        download_video(pl.videos[i], download_folder)

def download_audio_playlist(pl, download_folder, start_index, end_index):
     for i in range(start_index, end_index):
        download_audio(pl.videos[i], download_folder)

def save_video(path, txt):

    with open(txt, 'r') as file:
        links = file.readlines()

        for link in links:
            link = link.strip()  # Remove any extra whitespace
            if link:
                yt = YouTube(link)
                download_video(yt, path)

def save_video_playlists(path, txt):


    with open(txt, 'r') as file:
        links = file.readlines()

        for link in links:
            link = link.strip()  # Remove any extra whitespace
            if link:
                
                try:
                    match = re.match(r"<(\d*):(\d*)>(https?://[^\s]+)", link.strip())
                    
                    url = match.group(3)
                    pl = Playlist(url)

                    start_index = int(match.group(1)) if match.group(1) else 0
                    end_index = int(match.group(2)) if match.group(2) else len(pl.videos) 

                    title_safe = sanitize_title(pl.title)
                    download_video_playlist(pl, os.path.join(path, title_safe), start_index, end_index)
                except:
                    continue

def save_audio(path, txt):

    with open(txt, 'r') as file:
        links = file.readlines()

        for link in links:
            link = link.strip()
            if link:
                yt = YouTube(link)
                download_audio(yt, path)

def save_audio_playlists(path, txt):
    with open(txt, 'r') as file:
        links = file.readlines()

        for link in links:
            link = link.strip()  # Remove any extra whitespace
            if link:

                try:
                    match = re.match(r"<(\d*):(\d*)>(https?://[^\s]+)", link.strip())
                    
                    url = match.group(3)
                    pl = Playlist(url)

                    start_index = int(match.group(1)) if match.group(1) else 0
                    end_index = int(match.group(2)) if match.group(2) else len(pl.videos) 

                    title_safe = sanitize_title(pl.title)
                    download_audio_playlist(pl, os.path.join(path, title_safe), start_index, end_index)
                except:
                    continue

if __name__ == "__main__":

    video_txt_filePath = "C:/Users/ebz/Desktop/auto_download/video/videos.txt"
    video_download_folder = "C:/Users/ebz/Desktop/auto_download/video/videos"

    audio_txt_file_path = "C:/Users/ebz/Desktop/auto_download/audio/audios.txt"  # Change this to your txt file path
    audio_download_folder = "C:/Users/ebz/Desktop/auto_download/audio/audios"  # Change this to the desired download folder

    audio_playlist_txt_path = "C:/Users/ebz/Desktop/auto_download/audio/playlists.txt"
    audio_playlist_folder  = "C:/Users/ebz/Desktop/auto_download/audio/playlists"

    video_playlist_txt_path = "C:/Users/ebz/Desktop/auto_download/video/playlists.txt"
    video_playlist_folder = "C:/Users/ebz/Desktop/auto_download/video/playlists"


    save_video(video_download_folder, video_txt_filePath)
    save_video_playlists(video_playlist_folder, video_playlist_txt_path)


    save_audio(audio_download_folder, audio_txt_file_path)
    save_audio_playlists(audio_playlist_folder, audio_playlist_txt_path)


