import ast
from typing import List
from os import listdir
import spotipy
import requests
import json as js
import time
import csv
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


def get_streamings(path: str) -> List[dict]:
    
    '''
    Returns a list of dictionaries.
    
    Each dictionary represents a track:
        {
            'endTime': when track finished playing,
            'artistName': name of artist,
            'trackName': name of track,
            'msPlayed': duration track was played for
        }
    '''

    files = [str(path+'/') + x for x in listdir(path)
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


def consolidate_streams(monthly_sort: dict, chosen_month: str, token: str) -> dict:

    '''
    For each list of tracks creates a dictionary, with month keys corresponding to a list of tracks streamed that month.

    Each list is a set of tuples, where the tuples represent track items.
    Each list has tracks sorted in descending order by number of plays.

    Each tuple contains the track ID, and dictionary of the track's details.

        {
            month yyyy-mm: [(track_id, {trackName: __, artistName: __, plays: __}), ], 
        }
    '''

    consolidated_sort = {}

    for month in monthly_sort:

        if chosen_month != None and chosen_month != month:
            continue

        else:

            consolidated_month = {}

            for track in monthly_sort[month]:
                name = track["trackName"]
                artist = track["artistName"]
                time_played = float(track['msPlayed'])
                try:
                    details = get_id(track_name=name, artist_name=artist, token=token)
                    track_id = details[0]
                    duration = float(details[1])
                    proportion_played = time_played/duration
                    if track_id in consolidated_month.keys():
                        consolidated_month[track_id]['plays'] += proportion_played
                    else:
                        consolidated_month[track_id] = {'trackName': name, 'artistName': artist, \
                            'plays': proportion_played}
                except:
                    continue

            sorted_list = sorted(consolidated_month.items(), key=lambda x: x[1]['plays'], reverse=True)
            consolidated_sort[month] = sorted_list

    return consolidated_sort


def create_playlists(consolidated_sort_ids: dict, num_tracks: int, token: str):

    '''
    Creates Monthly Most Played playlists.
    '''

    count = 0

    for month in consolidated_sort_ids:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer ' + token,
        }

        name = {
            "name": month,
            "description": "Your " + str(num_tracks) + " most played tracks for " + month + ". \
Created with spotify-monthly-most-played by Sameer Aggarwal.",
            "public": False
        }
        data = js.dumps(name)

        response1 = requests.post('https://api.spotify.com/v1/users/' + config.username + '/playlists', \
            headers=headers, data=data)

        json = response1.json()
        playlist_id = json['id']
        playlist_url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'

        counter = 0
        playlist_tracks = []
        while counter < num_tracks:
            try:
                playlist_tracks.append('spotify:track:' + consolidated_sort_ids[month][counter][0])
                counter += 1
            except:
                break
        
        track_data = {'uris' : playlist_tracks}
        track_data_json = js.dumps(track_data)

        requests.post(playlist_url, headers=headers, data=track_data_json)
        count += 1

    return count


def monthly_most_played(path: str = 'Data/MyData', month: str = None, num_tracks: int = 25):
    
    start = time.time()

    token = get_token()
    history = get_streamings(path)
    sorted_history = sort_into_months(history)
    consolidated_history = consolidate_streams(sorted_history, month, token)
    counter = create_playlists(consolidated_history, num_tracks, token)
    
    time_taken = time.time() - start
    print('Done. %d playlist(s) created.' % counter)
    print('----- %f seconds -----' % time_taken)


def top_tracks(month: str, path: str, consolidated: dict = None):

    '''Creates CSV with details of tracks streamed in the given month, in descending order of plays.'''

    start = time.time()

    token = get_token()
    history = get_streamings(path)
    sorted_history = sort_into_months(history)

    if consolidated == None:
        data = consolidate_streams(sorted_history, month, token)[month]
    else:
        data = consolidated[month]
    with open('toptracks_'+month+'.csv', 'w', encoding='utf-8') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(['id', 'details'])
        for row in data:
            csv_out.writerow(row)
    
    time_taken = time.time() - start
    print('Done! CSV created.')
    print('------- %f seconds -------\n' % time_taken)