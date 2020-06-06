import ast
from typing import List
from os import listdir
import spotipy
import requests
import json as js
import timeit
from math import factorial
import config

def get_token():

    '''Returns Spotify authorisation token'''

    username = config.username
    client_id = config.client_id
    client_secret = config.client_secret
    redirect_uri = config.redirect_uri
    scope = config.scope

    token = spotipy.util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, \
        redirect_uri=redirect_uri)

    return token


def get_streamings(path: str = 'Data/MyData') -> List[dict]:
    
    '''
    Returns a list of dictionaries.
    
    Each dictionary represents a track:
        {
            'endTime': when track finished playing,
            'artistName: name of artist,
            'trackName': name of track,
            'msPlayed': duration track was played for
        }
    '''

    files = ['Data/MyData/' + x for x in listdir(path)
             if x.split('.')[0][:-1] == 'StreamingHistory']
    
    all_streamings = []
    
    for file in files: 
        with open(file, 'r', encoding='UTF-8') as f:
            new_streamings = ast.literal_eval(f.read())
            all_streamings += [streaming for streaming 
                               in new_streamings]
    return all_streamings


def get_id(track_name: str, artist_name: str, token: str) -> str:

    '''Returns the track ID and duration of each track'''

    # Sets header for HTML query
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer ' + token,
    }

    # Sets parameters for HTML query
    params = [('q', "track:" + track_name + " artist:" + artist_name), ('type', 'track')]

    # Searches Spotify database for track, returns ID and duration if track is found
    try:
        response = requests.get('https://api.spotify.com/v1/search', headers = headers, params = params, timeout = 5)
        json = response.json()
        first_result = json['tracks']['items'][0]
        track_id = first_result['id']
        duration = first_result['duration_ms']
        return track_id, duration
    except:
        return None


def sort_into_months(streaming_history: dict) -> dict:

    '''
    Sorts streamed tracks by month streamed.
    Returns a dictionary of lists, where the keys are the months and each value is a list of tracks streamed that month.
    '''

    monthly_sort = {}

    for track in streaming_history:
        date = str(track['endTime'][0:7])       # Extracts the month a track was streamed
        if date in monthly_sort.keys():
            monthly_sort[date].append(track)    # If another track streamed that month, add to list of that month's tracks
        else:
            monthly_sort[date] = []
            monthly_sort[date].append(track)    # If not, create a new list of tracks streamed that month

    return monthly_sort


def consolidate_streams(monthly_sort: dict, token: str) -> dict:

    '''
    For each list of tracks creates a dictionary, with keys of track names corresponding
    with a value made of a dictionary of the ID and total length played
        {
            month yyyy-mm: {track ID 1: proportional plays, track ID 2: proportional plays, etc}
        }
    '''

    consolidated_sort = {}

    for month in monthly_sort:

        consolidated_month = {}

        for track in monthly_sort[month]:
            name = track["trackName"]
            artist = track["artistName"]
            time_played = float(track['msPlayed'])
            if get_id(track_name=name, artist_name=artist, token=token) != None:
                track_id = get_id(track_name=name, artist_name=artist, token=token)[0]
                duration = float(get_id(track_name=name, artist_name=artist, token=token)[1])
                proportion_played = time_played/duration
                if track_id in consolidated_month.keys():
                    consolidated_month[track_id] += proportion_played
                else:
                    consolidated_month[track_id] = proportion_played
            else:
                continue

        sorted_month = sorted(consolidated_month.items(), key=lambda x: x[1], reverse=True)
        consolidated_sort[month] = sorted_month

    return consolidated_sort


def create_playlists(consolidated_sort: dict, token: str):

    '''
    Creates Monthly Most Played playlists.
    '''

    for month in consolidated_sort:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer ' + token,
        }

        name = {"name":month, "description":"Monthly Most Played", "public":False}
        data = js.dumps(name)

        response1 = requests.post('https://api.spotify.com/v1/users/qf2y70lfdxlxj9s4m6lchwkme/playlists', \
            headers=headers, data=data)

        json = response1.json()
        playlist_id = json['id']
        playlist_url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'

        counter = 0
        playlist_tracks = []
        while counter < 25:
            playlist_tracks.append('spotify:track:' + consolidated_sort[month][counter][0])
            counter += 1
        
        track_data = {'uris' : playlist_tracks}
        track_data_json = js.dumps(track_data)

        response2 = requests.post(playlist_url, headers=headers, data=track_data_json)


def monthly_most_played():

    token = get_token()
    history = get_streamings()
    sorted_history = sort_into_months(history)
    consolidated_history = consolidate_streams(sorted_history, token)
    create_playlists(consolidated_history, token)

    print('Done')