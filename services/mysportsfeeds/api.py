import base64
import json
import os
import requests

# credentials
USERNAME=os.getenv('MYSPORTSFEEDS_USER')
PASSWORD=os.getenv('MYSPORTSFEEDS_PASSWORD')

# API URL components
BASE_URL='https://api.mysportsfeeds.com/v1.2/pull/mlb/{}-{}/{}.json'
DEFAULT_SEASON=2018
REGULAR_SEASON='regular'

# feed types
FEED__FULL_GAME_SCHEDULE='full_game_schedule'
FEED__GAME_PLAYBYPLAY='game_playbyplay'
FEED__PLAYER_GAMELOGS='player_gamelogs'


def get_game_pitches(season=DEFAULT_SEASON, season_type=REGULAR_SEASON, **kwargs):
    at_bats = get_game_playbyplay(season, season_type, playtype='batter-up,pitch', **kwargs)['gameplaybyplay']['atBats']['atBat']

    for ab in at_bats:                                
        del ab['atBatPlay'][0]

    return at_bats


def get_game_playbyplay(season=DEFAULT_SEASON, season_type=REGULAR_SEASON, **kwargs):
    return get_feed(season, season_type, FEED__GAME_PLAYBYPLAY, **kwargs)


def get_player_gamelogs(season=DEFAULT_SEASON, season_type=REGULAR_SEASON, **kwargs):
    return get_feed(season, season_type, FEED__PLAYER_GAMELOGS, **kwargs)
    
    
def get_game_identifiers(season=DEFAULT_SEASON, season_type=REGULAR_SEASON):
    games = get_feed(season, season_type, FEED__FULL_GAME_SCHEDULE)

    game_identifiers = []

    for game in games['fullgameschedule']['gameentry']:
        date = game['date'].replace('-', '')
        away = game['awayTeam']['Abbreviation']
        home = game['homeTeam']['Abbreviation']

        game_identifier = '{}-{}-{}'.format(date, away, home)
        game_identifiers.append(game_identifier)

    return game_identifiers


def get_feed(season=DEFAULT_SEASON, season_type=REGULAR_SEASON, feed=FEED__FULL_GAME_SCHEDULE, **kwargs):
    try:
        response = requests.get(
            url = BASE_URL.format(season, season_type, feed),
            headers = {
                "Authorization": "Basic " + base64.b64encode('{}:{}'.format(USERNAME, PASSWORD).encode('utf-8')).decode('ascii')
            },
            params = kwargs
        )

        return json.loads(response.content)
    except requests.exceptions.RequestException as e:
        print('HTTP Request failed:')
    except json.JSONDecodeError:
        print('JSON decode failed:')
        print(response.content)
