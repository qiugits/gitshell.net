import requests


class VainAPI:
    ''' vainglory api '''
    def __init__(self):
        with open('secrets/vain-api', 'r') as f:
            self.apikey = f.read().rstrip()

    def request(self, url, params):
        headers = {
            'Authorization': self.apikey,
            'X-TITLE-ID': 'semc-vainglory',
            'Accept': 'application/vnd.api+json',
            # 'Accept-Encoding': 'gzip',
        }
        return requests.get(url, headers=headers, params=params).json()

    def single_player(self, reg, ign):
        url = f'https://api.dc01.gamelockerapp.com/shards/{reg}/players'
        params = {
            'filter[playerNames]': [ign],
        }
        res = self.request(url, params)
        if res.get('errors', ''):
            wrapped = res
        else:
            _attributes = res['data'][0]['attributes']
            wrapped = {
                'id': res['data'][0]['id'],
                'time': _attributes['createdAt'],
                'shrd': _attributes['shardId'],
                'name': _attributes['name'],
                'elo8': _attributes['stats']['elo_earned_season_8'],
                'wstr': _attributes['stats']['winStreak'],
                'lstr': _attributes['stats']['lossStreak'],
                'wins': _attributes['stats']['wins'],
                'tier': _attributes['stats']['skillTier'],
                'rnkp': _attributes['stats']['rankPoints']['ranked'],
                'blzp': _attributes['stats']['rankPoints']['blitz'],
            }
        return wrapped

    def matches(self, reg, ign, mode='ranked'):
        url = f'https://api.dc01.gamelockerapp.com/shards/{reg}/matches'
        params = {
            'filter[playerNames]': [ign],
            'sort': 'createdAt',
            'filter[gameMode]': mode,
        }
        res = self.request(url, params)

        # ================
        # Reshape the data
        # ================

        if res.get('errors', ''):
            matches = res
        else:

            # matches is one time only
            _matches = {i['id']: [i['attributes']['duration'],
                                  i['attributes']['gameMode'],
                                  i['attributes']['patchVersion'],
                                  i['relationships']['rosters']['data']]
                        for i in res['data']}
            _rosters = {i['id']: [i['attributes']['stats']['heroKills'],
                                  i['attributes']['stats']['side'],
                                  i['attributes']['stats']['turretKills'],
                                  i['attributes']['stats']['turretsRemaining'],
                                  i['relationships']['participants']['data']]
                        for i in res['included'] if i['type'] == 'roster'}
            # participants is to be saved
            _participants = {i['id']: [i['attributes']['actor'],
                                       i['attributes']['shardId'],
                                       i['attributes']['stats']['kills'],
                                       i['attributes']['stats']['deaths'],
                                       i['attributes']['stats']['assists'],
                                       i['attributes']['stats']['gold'],
                                       i['attributes']['stats']['farm'],
                                       i['attributes']['stats']['items'],
                                       i['attributes']['stats']['skillTier'],
                                       i['attributes']['stats']['winner'],
                                       i['relationships']['player']['data']['id']]
                             for i in res['included'] if i['type'] == 'participant'}
            participants = {k: {'actor': v[0],
                                'shard': v[1],
                                'kills': v[2],
                                'deaths': v[3],
                                'assists': v[4],
                                # KDA
                                'kda': (v[2] + v[4]) / (v[3] + 1),
                                'gold': int(v[5]),
                                'farm': int(v[6]),
                                'items': v[7],
                                'tier': v[8],
                                'won': v[9],
                                'player_id': v[10]}
                            for k, v in _participants.items()}
            rosters = {k: {'team_kill_score': v[0],
                           'side': v[1].replace('/', '-'),
                           'turret_kill': v[2],
                           'turret_remain': v[3],
                           'participants': [participants[data['id']] for data in v[4]]}
                       for k, v in _rosters.items()}
            matches = [{'duration': v[0],
                        'mode': v[1],
                        'version': v[2],
                        'rosters': [rosters[r['id']] for r in v[3]],
                        }
                       for v in _matches.values()]
            # for m in matches:
            #     m['participants'] = {k: v for k, v in participants.items()
            #                          if k in [i for r in m['rosters']
            #                                   for i in r['participants']]}
        return matches


# ================
# Utilities
# ================
def itemname_to_cssreadable(name):
    return name.replace(' ', '-').replace("'", "").lower()


def particularplayer_from_singlematch(match, player_id):
    for r in match['rosters']:
        for p in r['participants']:
            if p['player_id'] == player_id:
                return p
