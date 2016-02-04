from django import template
from django.conf import settings

from ..apps.users.models import LeagueRating

import os
import re
import requests
import time

register = template.Library()

API_BASE = 'https://psyonix-rl.appspot.com'
API_VERSION = '105'


def api_login():

    HEADERS = {
        'DBVersion': '00.03.0011-00.01.0011',
        'LoginSecretKey': 'dUe3SE4YsR8B0c30E6r7F2KqpZSbGiVx',
        'CallProcKey': 'pX9pn8F4JnBpoO8Aa219QC6N7g18FJ0F',
        'DB': 'BattleCars_Prod',
    }

    login_data = {
        'PlayerName': "RocketLeagueReplays.com",
        'PlayerID': os.getenv('STEAM_ID'),
        'Platform': 'Steam',
        'BuildID': 64123161,
        'AuthCode': '1400000007975B47F1DEFD678CA3E50201001001F581785618000000010000000200000048FA925600000000B698010001000000BE0000003E000000040000008CA3E5020100100116DC03003352A75664C0FEA900000000457E7856C52D94560100E4780000020000FA05000000B22E0600000000006CFF6B550F2F82520844764F624C679B4FC142A0736366E063CD4031788A853D9DB99551F3EF9C71F3B91AC7F8257C63BB4AF2250F8C4EEFD9583F121EBA6ADE224E52594128BB9FC714F167C82FE785921348B1907FB719DF2A6BB2D48482B489F190633FCC135D4C60987AC8F25E613859D8C3308D6BF48E4175F28C46D3CF',
    }

    r = requests.post(API_BASE + '/auth/'.format(API_VERSION), headers=HEADERS, data=login_data)

    if r.text.strip() == 'SCRIPT ERROR PlatformAuthError:':
        # Wait a few seconds and try again.
        print 'Hit PlatformAuthError, trying again in 5 seconds.'
        time.sleep(5)
        return api_login()

    elif r.text != '1':
        raise Exception("Unable to login.")

    HEADERS['SessionID'] = r.headers['sessionid']

    return HEADERS


def get_leaderboards(headers):

    r = requests.post(API_BASE + '/callproc/'.format(API_VERSION), headers=headers, data={
        'Proc[]': [
            'GetLeaderboard',
        ],
        'P0P[]': [
            'Skill10',
            '1000',  # Get the top 500 for PC and PS4
        ],
    })

    matches = re.findall(r'UserName=(.*)&Value=(\d+)&Platform=(Steam|PSN)(?:&SteamID=(\d+))?', r.text)

    print matches

    # "&Proc[]=GetLeaderboardRankForUsersSteam&P0P[]=Skill12&P0P[]=76561197960768016&P0P[]=76561197962143153&P0P[]=76561197962637102&P0P[]=76561197967712669&P0P[]=76561197970878898&P0P[]=76561197971142652&P0P[]=76561197972314809&P0P[]=76561197973286641&P0P[]=76561197976476356&P0P[]=76561197981862109&P0P[]=76561197982230152&P0P[]=76561197982668909&P0P[]=76561197983053524&P0P[]=76561197984330337&P0P[]=76561197985349259&P0P[]=76561197986686129&P0P[]=76561197987756440&P0P[]=76561197988397209&P0P[]=76561197988514399&P0P[]=76561197989005550&P0P[]=76561197989253137&P0P[]=76561197992954702&P0P[]=76561197997152315&P0P[]=76561197997245695&P0P[]=76561197998038750&P0P[]=76561197998176289&P0P[]=76561197999425814&P0P[]=76561198002101324&P0P[]=76561198003067301&P0P[]=76561198005537380&P0P[]=76561198005776507&P0P[]=76561198007277388&P0P[]=76561198008522750&P0P[]=76561198010382418&P0P[]=76561198010936007&P0P[]=76561198011058278&P0P[]=76561198011930168&P0P[]=76561198012936322&P0P[]=76561198013275714&P0P[]=76561198015574926&P0P[]=76561198018462678&P0P[]=76561198018573967&P0P[]=76561198019284249&P0P[]=76561198021253213&P0P[]=76561198022033034&P0P[]=76561198022035654&P0P[]=76561198023497277&P0P[]=76561198025133766&P0P[]=76561198025410399&P0P[]=76561198025592563&P0P[]=76561198033631878&P0P[]=76561198034526912&P0P[]=76561198038791419&P0P[]=76561198039163322&P0P[]=76561198040729865&P0P[]=76561198040816773&P0P[]=76561198042103209&P0P[]=76561198043568489&P0P[]=76561198049513845&P0P[]=76561198052128676&P0P[]=76561198059426800&P0P[]=76561198060952657&P0P[]=76561198075523217&P0P[]=76561198077855562&P0P[]=76561198125565514&P0P[]=76561198204292324&P0P[]=76561198008869772&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&P0P[]=0&Proc[]=GetLeaderboardValueForUserSteam&P1P[]=76561198008869772&P1P[]=Skill12"

    # Build up a mega request.
    data = {
        'Proc[]': [
            'GetLeaderboardRankForUsersSteam',
            'GetLeaderboardValueForUserSteam'
        ],
        'P0P[]': [
            'Skill12'
        ],
        'P1P[]': [
            os.getenv('STEAM_ID'),
            'Skill12',
        ]
    }

    # Proc[]=GetLeaderboardValueForUserSteam&P1P[]=76561198008869772&P1P[]=Skill12

    for index, match in enumerate(matches):
        if match[2] == 'Steam':
            data['P0P[]'].append(match[3])

    print data

    r = requests.post(API_BASE + '/callproc{}/'.format(API_VERSION), headers=headers, data=data)

    print dir(r.request)
    import urllib
    print urllib.unquote(r.request.body)
    print r.text
    return


def get_league_data(steam_ids):
    """
    Playlist=0&Mu=20.6591&Sigma=4.11915&RankPoints=100
    Playlist=10&Mu=27.0242&Sigma=2.96727&RankPoints=292
    Playlist=11&Mu=37.0857&Sigma=2.5&RankPoints=618
    Playlist=12&Mu=35.8244&Sigma=2.5&RankPoints=500
    Playlist=13&Mu=33.5018&Sigma=2.5&RankPoints=468
    """

    all_steam_ids = list(steam_ids)

    for steam_ids in chunks(all_steam_ids, 10):
        data = {
            'Proc[]': [
                'GetPlayerSkillAndRankPointsSteam'
            ] * len(steam_ids),
        }

        for index, steam_id in enumerate(steam_ids):
            data['P{}P[]'.format(index)] = [str(steam_id)]

        headers = api_login()
        r = requests.post(
            API_BASE + '/callproc{}/'.format(API_VERSION),
            headers=headers,
            data=data
        )

        if r.text.strip() == 'SCRIPT ERROR SessionNotActive:':
            print 'Hit SessionNotActive'
            continue

        # Split the response into individual chunks.
        response_chunks = r.text.strip().split('\r\n\r\n')

        for index, response in enumerate(response_chunks):
            print 'Getting rating data for', steam_ids[index]
            matches = re.findall(r'Playlist=(\d+)&.+RankPoints=(\d+)', response)

            if not matches:
                print 'no matches'

            matches = dict(matches)

            # Store this, cache it, do something with it.
            LeagueRating.objects.create(
                steamid=steam_ids[index],
                duels=matches.get(str(settings.PLAYLISTS['RankedDuels']), 0),
                doubles=matches.get(str(settings.PLAYLISTS['RankedDoubles']), 0),
                solo_standard=matches.get(str(settings.PLAYLISTS['RankedSoloStandard']), 0),
                standard=matches.get(str(settings.PLAYLISTS['RankedStandard']), 0),
            )


def chunks(input_list, chunk_length):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(input_list), chunk_length):
        yield input_list[i:i+chunk_length]


def debug_id(steam_id):
    """
    Playlist=0&Mu=20.6591&Sigma=4.11915&RankPoints=100
    Playlist=10&Mu=27.0242&Sigma=2.96727&RankPoints=292
    Playlist=11&Mu=37.0857&Sigma=2.5&RankPoints=618
    Playlist=12&Mu=35.8244&Sigma=2.5&RankPoints=500
    Playlist=13&Mu=33.5018&Sigma=2.5&RankPoints=468
    """
    data = {
        'Proc[]': [
            'GetPlayerSkillAndRankPointsSteam'
        ],
        'P0P[]': [str(steam_id)]
    }

    headers = api_login()
    r = requests.post(
        API_BASE + '/callproc{}/'.format(API_VERSION),
        headers=headers,
        data=data
    )

    if r.text.strip() == 'SCRIPT ERROR SessionNotActive:':
        print 'Hit SessionNotActive'

    print r.text

    matches = re.findall(r'Playlist=(\d+)&.+RankPoints=(\d+)', r.text)

    if not matches:
        print 'no matches'

    matches = dict(matches)

    import pprint
    pprint.pprint(matches)

    print 'duels', matches.get(str(settings.PLAYLISTS['RankedDuels']), 0)
    print 'doubles', matches.get(str(settings.PLAYLISTS['RankedDoubles']), 0)
    print 'solo_standard', matches.get(str(settings.PLAYLISTS['RankedSoloStandard']), 0)
    print 'standard', matches.get(str(settings.PLAYLISTS['RankedStandard']), 0)
