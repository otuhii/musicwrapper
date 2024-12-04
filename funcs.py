import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from aiogram.types import FSInputFile
import os

import yt_dlp

from config_exmp import client_id, client_secret


class workflow():
    def __init__(self):
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
        ))

        # Configure yt-dlp options
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True
        }


    def get_playlist_list(self, link, state):
        #PLAYLIST
        if state == 1:
            songs = self.spotify.playlist_items(
                playlist_id=link, 
                fields="items.track(name,artists(name))"
            )
            return [f"{s['track']['name']} by {', '.join(artist['name'] for artist in s['track']['artists'])}" 
                   for s in songs['items']]
        #ALBUM
        elif state == 2:
            songs = self.spotify.album_tracks(album_id=link)
            return [f"{s['name']} by {', '.join(artist['name'] for artist in s['artists'])}" 
                   for s in songs['items']]
        #SINGLE SONG
        elif state == 3:
            song = self.spotify.track(track_id=link)
            return f"{song['name']} by {', '.join(artist['name'] for artist in song['artists'])}"
        

    #bot dependant function
    async def download_and_send_songs(self, songs_list: list, message):
        if not isinstance(songs_list, list):
            songs_list = [songs_list]  # Convert single song to list
            
        for song_name in songs_list:
            try:
                # Search and download
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    result = ydl.extract_info(f"ytsearch1:{song_name}", download=False)['entries'][0]
                    ydl.download([f"ytsearch1:{song_name}"])
                    
                    # Get the file path
                    file_path = f"{result['title']}.mp3"
                    
                    # Send the audio file
                    audio = FSInputFile(file_path)
                    await message.answer_audio(
                        audio,
                        caption=f"Downloaded: {song_name}"
                    )
                    
                    # Delete the file
                    os.remove(file_path)
                    
            except Exception as e:
                await message.answer(f"Error downloading {song_name}: {str(e)}")
                continue
                
        await message.answer("All available songs have been downloaded and sent!")
    


