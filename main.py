import os
import re
import yt_dlp
import json
from pathlib import Path

def sanitize_title(title):
    # replace any character that's not a letter or number with an underscore
    return re.sub(r'[^a-zA-Z0-9]', '_', title)

def load_tracking_file(tracking_file):
    if os.path.exists(tracking_file):
        with open(tracking_file, 'r') as f:
            return json.load(f)
    return {}

def save_tracking_file(tracking_file, data):
    with open(tracking_file, 'w') as f:
        json.dump(data, f, indent=4)

def update_tracking(download_folder, tracking_file):
    tracking = load_tracking_file(tracking_file)
    current_files = {f.stem: str(f) for f in Path(download_folder).glob('*.mp4') if '_video' not in f.stem and '_audio' not in f.stem}
    current_files.update({f.stem: str(f) for f in Path(download_folder).glob('*.mp3')})
    
    # Update tracking with existing files
    for title, path in current_files.items():
        if title not in tracking:
            tracking[title] = {"path": path, "url": None}  # URL unknown for existing files
    
    # Remove entries for files that no longer exist
    tracking = {k: v for k, v in tracking.items() if os.path.exists(v["path"])}
    
    save_tracking_file(tracking_file, tracking)
    return tracking

def download_video(url, download_folder, tracking_file):
    tracking = update_tracking(download_folder, tracking_file)
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title_safe = sanitize_title(info['title'])
            final_path = os.path.join(download_folder, f"{title_safe}.mp4")
            
        if title_safe not in tracking or not os.path.exists(tracking[title_safe]["path"]):
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'outtmpl': final_path,
                'quiet': True,
                'extract_flat': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            tracking[title_safe] = {"path": final_path, "url": url}
            save_tracking_file(tracking_file, tracking)
            print(f'Successfully downloaded: {title_safe}')
        else:
            print(f'Already downloaded: {title_safe}.mp4')
            
    except Exception as e:
        print(f'Error downloading {url}: {e}')
    
    print("\n")

def download_audio(url, download_folder, tracking_file):
    tracking = update_tracking(download_folder, tracking_file)
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title_safe = sanitize_title(info['title'])
            final_path = os.path.join(download_folder, f"{title_safe}.mp3")
            
        if title_safe not in tracking or not os.path.exists(tracking[title_safe]["path"]):
            ydl_opts = {
                'format': 'bestaudio/best',
                'extract_flat': True,
                'outtmpl': os.path.join(download_folder, title_safe),  # No extension here
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            tracking[title_safe] = {"path": final_path, "url": url}
            save_tracking_file(tracking_file, tracking)
            print(f'Successfully downloaded: {title_safe}.mp3')
        else:
            print(f'Already downloaded: {title_safe}.mp3')
            
    except Exception as e:
        print(f'Error downloading {url}: {e}')
    
    print("\n")

def download_file_playlist(pl_url, download_folder, start_index, end_index, func, tracking_file):
    with yt_dlp.YoutubeDL({'quiet': True, 'ignoreerrors': True}) as ydl:
        info = ydl.extract_info(pl_url, download=False)
        if info is None:
            print(f"Failed to extract playlist info for {pl_url}")
            return
        
        videos = info['entries'][start_index:] if (end_index == -1) else info['entries'][start_index:end_index]
        
        for video in videos:
            # Skip unavailable videos
            if video is None or 'webpage_url' not in video:
                print(f"Skipping unavailable video in playlist {pl_url}")
                continue
            video_url = video['webpage_url']
            func(video_url, download_folder, tracking_file)
            
def save_file(path, txt, func, tracking_file):
    with open(txt, 'r+') as file:
        links = file.readlines()

        for link in links:
            link = link.strip()
            if link:
                func(link, path, tracking_file)

def save_file_playlists(path, txt, func, tracking_file):
    with open(txt, 'r+') as file:
        links = file.readlines()

        for link in links:
            link = link.strip()
            if link:
                if link.find(">h") == -1:
                    with yt_dlp.YoutubeDL({'quiet': True, 'ignoreerrors': True}) as ydl:
                        info = ydl.extract_info(link, download=False)
                        title_safe = sanitize_title(info['title'])
                    download_file_playlist(link, os.path.join(path, title_safe), 0, -1, func, tracking_file)
                else:
                    start_pos = link.find("<")
                    end_pos = link.find(">h")
                    
                    pl_url = link[end_pos + 1:]
                    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                        info = ydl.extract_info(pl_url, download=False)
                        title_safe = sanitize_title(info['title'])
                    
                    start_index = int(link[start_pos + 1]) if link[start_pos + 1] != ':' else 0
                    end_index = int(link[end_pos - 1]) if link[end_pos - 1] != ':' else len(info['entries'])
                    
                    download_file_playlist(pl_url, os.path.join(path, title_safe), start_index, end_index, func, tracking_file)

if __name__ == "__main__":
    pref = "C:/Users/ebube/Desktop/auto_download/"

    video_txt_filePath = pref + "video/videos.txt"
    video_download_folder = pref + "video/videos"
    video_tracking_file = pref + "video/videos_tracking.json"

    audio_txt_file_path = pref + "audio/audios.txt"
    audio_download_folder = pref + "audio/audios"
    audio_tracking_file = pref + "audio/audios_tracking.json"

    audio_playlist_txt_path = pref + "audio/playlists.txt"
    audio_playlist_folder = pref + "audio/playlists"
    audio_playlist_tracking_file = pref + "audio/playlists_tracking.json"

    video_playlist_txt_path = pref + "video/playlists.txt"
    video_playlist_folder = pref + "video/playlists"
    video_playlist_tracking_file = pref + "video/playlists_tracking.json"

    formats = {
        "video": {
            "txt_file_path": video_txt_filePath,
            "download_folder": video_download_folder,
            "tracking_file": video_tracking_file,
            "playlist_txt_path": video_playlist_txt_path,
            "playlist_folder": video_playlist_folder,
            "playlist_tracking_file": video_playlist_tracking_file,
            "download_function": download_video
        },
        "audio": {
            "txt_file_path": audio_txt_file_path,
            "download_folder": audio_download_folder,
            "tracking_file": audio_tracking_file,
            "playlist_txt_path": audio_playlist_txt_path,
            "playlist_folder": audio_playlist_folder,
            "playlist_tracking_file": audio_playlist_tracking_file,
            "download_function": download_audio
        }
    }

    for key, format_info in formats.items():
        print(f"Processing {key} format\n")
        # Ensure download folders exist
        os.makedirs(format_info["download_folder"], exist_ok=True)
        os.makedirs(format_info["playlist_folder"], exist_ok=True)
        
        # Process single files
        save_file(format_info["download_folder"], format_info["txt_file_path"], format_info["download_function"], format_info["tracking_file"])
        
        # Process playlists
        save_file_playlists(format_info["playlist_folder"], format_info["playlist_txt_path"], format_info["download_function"], format_info["playlist_tracking_file"])
        print("\n\n\n")