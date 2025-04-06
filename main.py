import os
import re
import subprocess

from pytubefix import Playlist
from pytubefix import YouTube


# def download_instagram_reels(username, max_retries, folder_path):
#     # Create an Instaloader instance
#     L = instaloader.Instaloader(
#         download_pictures=False,
#         download_videos=True,
#         download_comments=False,
#         download_geotags=False,
#         download_video_thumbnails=False,
#         filename_pattern="{shortcode}"  # Use shortcode as filename
#     )
    
#     # Login with session persistence
#     ig_username = input("Enter your Instagram username: ")
#     session_file = f"{folder_path}/session-{ig_username}"
    
#     try:
#         # Load existing session if available
#         if os.path.exists(session_file):
#             L.load_session_from_file(ig_username, session_file)
#             print("Loaded saved session successfully!")
#         else:
#             # New login
#             ig_password = getpass("Enter your Instagram password: ")
#             print("Waiting before login attempt...")
#             time.sleep(random.uniform(2, 5))
#             L.login(ig_username, "r44yee6z5#@//%;Srf")
#             L.save_session_to_file(session_file)  # Save session after successful login
#             print("Logged in and saved session successfully!")
    
#     except instaloader.exceptions.TwoFactorAuthRequiredException:
#         print("Two-factor authentication is required.")
#         two_factor_code = input("Enter the 2FA code sent to your device: ")
#         try:
#             L.two_factor_login(two_factor_code)
#             L.save_session_to_file(session_file)  # Save session after 2FA
#             print("2FA login successful and session saved!")
#         except Exception as e:
#             print(f"2FA login failed: {str(e)}")
#             return
    
#     except instaloader.exceptions.BadCredentialsException:
#         print("Login failed: Incorrect username or password.")
#         return
    
#     except Exception as e:
#         print(f"Login failed: {str(e)}")
#         return
    
#     # Create directory for downloads if it doesn't exist
#     download_dir = f"{folder_path}/{username}/reels_{username}"
#     if not os.path.exists(download_dir):
#         os.makedirs(download_dir)
    
#     # File to track downloaded videos
#     downloaded_file = f"{folder_path}/{username}/downloaded_{username}.txt"
#     downloaded_ids = set()
#     if os.path.exists(downloaded_file):
#         with open(downloaded_file, 'r') as f:
#             downloaded_ids = set(line.strip() for line in f)
    
#     try:
#         # Get profile
#         profile = instaloader.Profile.from_username(L.context, username)
#         new_downloads = 0
        
#         with open(downloaded_file, 'a') as f:
#             for post in profile.get_posts():
#                 if post.is_video and post.shortcode not in downloaded_ids:
#                     print(f"Preparing to download reel: {post.shortcode}")
#                     for attempt in range(max_retries):
#                         try:
#                             delay = random.uniform(5, 10)
#                             print(f"Waiting {delay:.2f} seconds before download...")
#                             time.sleep(delay)
                            
#                             # Download the post
#                             L.download_post(post, target=download_dir)
                            
#                             # Keep only the .mp4 file, remove .zip and .json
#                             for file in os.listdir(download_dir):
#                                 file_path = os.path.join(download_dir, file)
#                                 if file.endswith(('.json.xz', '.zip')):
#                                     os.remove(file_path)
#                                 elif file.endswith('.mp4'):
#                                     # Rename to ensure uniqueness if needed
#                                     new_name = f"{post.shortcode}.mp4"
#                                     os.rename(file_path, os.path.join(download_dir, new_name))
                            
#                             # Record the shortcode
#                             f.write(f"{post.shortcode}\n")
#                             downloaded_ids.add(post.shortcode)
#                             new_downloads += 1
#                             print(f"Successfully downloaded {post.shortcode}.mp4")
#                             break
                        
#                         except instaloader.exceptions.TooManyRequestsException:
#                             if attempt < max_retries - 1:
#                                 wait_time = (attempt + 1) * 120
#                                 print(f"Rate limit hit. Waiting {wait_time} seconds...")
#                                 time.sleep(wait_time)
#                             else:
#                                 print(f"Failed {post.shortcode} after {max_retries} attempts.")
#                         except Exception as e:
#                             print(f"Error downloading {post.shortcode}: {str(e)}")
#                             break
        
#         print(f"\nDownload complete! New reels downloaded: {new_downloads}")
#         print(f"Total reels stored in {download_dir} (only .mp4 files)")
    
#     except Exception as e:
#         print(f"Error: {str(e)}")


def sanitize_title(title):
    # replace any character that's not a letter or number with an underscore
    return re.sub(r'[^a-zA-Z0-9]', '_', title)

def download_video(yt, download_folder):
    title_safe = sanitize_title(yt.title)
    
    try:
        video_path = os.path.join(download_folder, title_safe + "_video.mp4")
        audio_path = os.path.join(download_folder, title_safe + "_audio.mp4")
        final_path = os.path.join(download_folder, title_safe + ".mp4")

        if not os.path.exists(final_path):
            # Get the best video-only stream (highest resolution)
            video = yt.streams.filter(adaptive=True, file_extension="mp4").order_by("resolution").desc().first()
            video.download(output_path=download_folder, filename=title_safe + "_video.mp4")

            # Get the best audio-only stream
            audio = yt.streams.filter(only_audio=True, file_extension="mp4").order_by("abr").desc().first()
            audio.download(output_path=download_folder, filename=title_safe + "_audio.mp4")

            # Merge video and audio using ffmpeg
            subprocess.run([
                "ffmpeg", "-i", video_path, "-i", audio_path,
                "-c:v", "copy", "-c:a", "aac", "-strict", "experimental",
                "-y", final_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            # Remove intermediate files
            os.remove(video_path)
            os.remove(audio_path)

            print(f'Successfully downloaded: {yt.title}')
        else:
            print(f'Already downloaded: {yt.title}.mp4')

    except Exception as e:
        if os.path.exists(audio_path):
            os.remove(audio_path)

        if os.path.exists(video_path):
            os.remove(video_path)

        if os.path.exists(final_path):
            os.remove(final_path)
        
        print(f'Error downloading {yt.title}: {e}')

    print("\n")


def download_audio(yt, download_folder):
    title_safe = sanitize_title(yt.title)
    path = os.path.join(download_folder, title_safe + ".mp3")
    int_title = title_safe + "_unprocessed.mp4" 
    intermediate_path = os.path.join(download_folder, int_title)
    
    try:
        if not os.path.exists(path):

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
            if os.path.exists(intermediate_path):
                os.remove(intermediate_path)
            print(f"Error converting {yt.title}: {e.stderr.decode()}")
    except Exception as e:
            print(f"Error downloading {yt.title}: {e.stderr.decode()}")
    
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
        
        #file.truncate(0) # empty the file 


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
        
        #file.truncate(0) # empty the file 



if __name__ == "__main__":

    pref = "C:/Users/ebz/Desktop/auto_download/"

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








