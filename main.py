import os
import re
import subprocess

from pytubefix import Playlist
from pytubefix import YouTube


def sanitize_title(title):
    # replace any character that's not a letter or number with an underscore
    return re.sub(r'[^a-zA-Z0-9]', '_', title)


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
    
    print("\n")


def download_audio(yt, download_folder):
    title_safe = sanitize_title(yt.title)
    path = os.path.join(download_folder, title_safe + ".mp3")
    
    try:
        if not os.path.exists(path):
            int_title = title_safe + "_unprocessed.mp4" 
            intermediate_path = os.path.join(download_folder, int_title)

            ys = yt.streams.get_audio_only()
            ys.download(output_path=download_folder, filename=int_title)
            print(f"Successfully downloaded: {yt.title}.mp4")

            result = subprocess.run([
                    "ffmpeg", "-i", intermediate_path,
                    "-vn",
                    "-ar", "44100", 
                    "-ac", "2",
                    "-b:a", "192k", 
                    "-y",
                    path
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            os.remove(intermediate_path)
            print(f"Successfully converted: {yt.title}.mp4")
        else:
                print(f"Already downloaded: {yt.title}.mp3")
    except subprocess.CalledProcessError as e:
            # If ffmpeg fails print the error output
            print(f"Error converting {yt.title}.mp4: {e.stderr.decode()}")
    except Exception as e:
            print(f"Error downloading {yt.title}: {e}")
    
    print("\n")


def download_file_playlist(pl, download_folder, start_index, end_index, func):
     for i in range(start_index, end_index):
        func(pl.videos[i], download_folder)


def save_file(path, txt, func):

    with open(txt, 'r+') as file:
        links = file.readlines()

        for link in links:
            link = link.strip()
            if link:
                yt = YouTube(link, "WEB")
                func(yt, path)
        
        file.truncate(0) # empty the file 


def save_file_playlists(path, txt, func):
    with open(txt, 'r+') as file:
        links = file.readlines()

        for link in links:
            link = link.strip()  # Remove any extra whitespace
            if link:

                if link.find(">h") == -1:
                    pl = Playlist(link, "WEB")
                    start_index = 0
                    end_index = len(pl.video_urls)

                    title_safe = sanitize_title(pl.title)

                    download_file_playlist(pl, os.path.join(path, title_safe), start_index, end_index, func)

                else:
                    start_pos = link.find("<")
                    end_pos = link.find(">h")

                    pl = Playlist(link[end_pos + 1:], "WEB")

                    start_index = link[start_pos + 1] if link[start_pos + 1] != ':' else 0
                    end_index = link[end_pos - 1] if link[end_pos - 1] != ':' else len(pl.video_urls)

                    title_safe = sanitize_title(pl.title)

                    download_file_playlist(pl, os.path.join(path, title_safe), start_index, end_index, func)
        
        file.truncate(0) # empty the file 



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


    formats = {
        "video": {
            "txt_file_path": video_txt_filePath,
            "download_folder": video_download_folder,
            "playlist_txt_path": video_playlist_txt_path,
            "playlist_folder": video_playlist_folder,
            "download_function": download_video
        },
        "audio": {
            "txt_file_path": audio_txt_file_path,
            "download_folder": audio_download_folder,
            "playlist_txt_path": audio_playlist_txt_path,
            "playlist_folder": audio_playlist_folder,
            "download_function": download_audio
        }
    }

    for key, format_info in formats.items():
        print(f"Processing {key} format\n")
        save_file(format_info["download_folder"], format_info["txt_file_path"], format_info["download_function"])
        save_file_playlists(format_info["playlist_folder"], format_info["playlist_txt_path"], format_info["download_function"])
        print("\n\n\n")


