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
                yt = YouTube(link, "WEB")
                download_video(yt, path)

def save_video_playlists(path, txt):


    with open(txt, 'r') as file:
        links = file.readlines()

        for link in links:
            link = link.strip()
            if link:

                if link.find(">h") == -1:
                    pl = Playlist(link, "WEB")

                    start_index = 0
                    end_index = len(pl.video_urls)

                    title_safe = sanitize_title(pl.title)

                    download_video_playlist(pl, os.path.join(path, title_safe), start_index, end_index)

                else:
                    start_pos = link.find("<")
                    end_pos = link.find(">h")

                    pl = Playlist(link[end_pos + 1:], "WEB")

                    start_index = link[start_pos + 1] if link[start_pos + 1] != ':' else 0
                    end_index = link[end_pos - 1] if link[end_pos - 1] != ':' else len(pl.video_urls)

                    title_safe = sanitize_title(pl.title)

                    download_video_playlist(pl, os.path.join(path, title_safe), start_index, end_index)


def save_audio(path, txt):

    with open(txt, 'r') as file:
        links = file.readlines()

        for link in links:
            link = link.strip()
            if link:
                yt = YouTube(link, "WEB")
                download_audio(yt, path)

def save_audio_playlists(path, txt):
    with open(txt, 'r') as file:
        links = file.readlines()

        for link in links:
            link = link.strip()  # Remove any extra whitespace
            if link:

                if link.find(">h") == -1:
                    pl = Playlist(link, "WEB")
                    start_index = 0
                    end_index = len(pl.video_urls)

                    title_safe = sanitize_title(pl.title)

                    print(os.path.join(path, title_safe))


                    download_audio_playlist(pl, os.path.join(path, title_safe), start_index, end_index)

                else:
                    start_pos = link.find("<")
                    end_pos = link.find(">h")

                    pl = Playlist(link[end_pos + 1:], "WEB")

                    start_index = link[start_pos + 1] if link[start_pos + 1] != ':' else 0
                    end_index = link[end_pos - 1] if link[end_pos - 1] != ':' else len(pl.video_urls)

                    title_safe = sanitize_title(pl.title)

                    download_audio_playlist(pl, os.path.join(path, title_safe), start_index, end_index)



if __name__ == "__main__":

    pref = "C:/Users/ebube/Desktop/auto_download/"

    video_txt_filePath = pref + "video/videos.txt"
    video_download_folder = pref + "video/videos"

    audio_txt_file_path = pref + "audio/audios.txt"
    audio_download_folder = pref + "audio/audios"

    audio_playlist_txt_path = pref + "audio/playlists.txt"
    audio_playlist_folder  =  pref + "audio/playlists"

    video_playlist_txt_path = pref + "video/playlists.txt"
    video_playlist_folder = pref + "video/playlists"


    save_video(video_download_folder, video_txt_filePath)
    save_video_playlists(video_playlist_folder, video_playlist_txt_path)


    save_audio(audio_download_folder, audio_txt_file_path)
    save_audio_playlists(audio_playlist_folder, audio_playlist_txt_path)


