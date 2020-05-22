#First I need to Login to Youtube and look at my liked videos
#Then open Spotify
#Create Playlist in Spotify
#Find Song
#Add Song to the created Playlist

#I need to import json first in order to use the relevant calls.  I also need to import requests to make the HTTP request.
#I found my spotify user ID and token and it is contained in a separate file called 'private' and assigned to the variable spotify_user_id


import json
import requests
from private import spotify_user_id, spotify_token

#this section was taken from Youtube's API documentation 
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl

class CreateSpotifyPlaylist:

    def __init__(self):
        self.youtube = self.get_youtube_client()
        self.all_song_info = {}
    
    def get_youtube_client(self):
        #this is all copied from Youtube API Documentation
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube
    
    def get_liked_videos(self):
        #also taken from the Youtube API documentation
        request = self.youtube.videos().list(
        part="snippet,contentDetails,statistics",
        myRating="like"
    )
        response = request.execute()

        for item in response["items"]:
            title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(item["id"])

            video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
            song_name = video["track"]
            artist = video["artist"]

            if song_name is not None and artist is not None:
                self.all_song_info[video_title]={
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,

                    "spotify_uri":self.get_spotify_uri(song_name, artist)
                }

    def create_playlist(self):
        
        request_body = json.dumps({
            "name": "Youtube Liked Videos",
            "description": "Videos that I have liked on Youtube",
            "public": True
        })

        query = f"https://api.spotify.com/v1/users/{spotify_user_id}/playlists"
        response = requests.post(
            query,
            data = request_body,
            headers={
                "Content-Type: application/json"
                f"Authorization: Bearer {spotify_token}"
            }
        )
        response_json = response.json()

        #this is our playlist ID
        return response_json["id"]
    def get_spotify_uri(self,song,artist):
        
        query = f"https://api.spotify.com/v1/search?q=artist:{artist}%20track:{song}&type=track"

        response = requests.get(
            query,
            headers={
                "Content-Type: application/json"
                f"Authorization: Bearer {spotify_token}"
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        uri = songs[0]["uri"]

        return uri

    def add_song(self):
        self.get_liked_videos()

        uris = [info["spotify_uri"]
        for song, info in self.all_song_info.items()]

        playlist_id = self.create_playlist()

        request_data = json.dumps(uris)

        query = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

        response = requests.post(
            query,
            data = request_data,
            headers={
                "Content-Type: application/json"
                f"Authorization: Bearer {spotify_token}"
            }
        )
        response_json = response.json()
        return response_json

        

if __name__ == '__main__':
    csp = CreateSpotifyPlaylist()
    csp.add_song()


