import pandas as pd
import requests
from flaskFPL.models import Manager
from natsort import natsorted

pd.set_option('display.max_columns', None)
base_url = 'https://fantasy.premierleague.com/api/'
test_id = 6106451
test_gw = requests.get(base_url + "/entry/" + str(test_id) + "/history/").json()
try:
    current_week = len(test_gw['current'])
except KeyError as error:
    if error:
        # no_season = True
        print("Currently off season")
        quit()



def get_league_name(lid=0):
    if lid == 0:
        lid = input("Enter league ID: ")
    r = requests.get(base_url + "leagues-classic/" + str(lid) + "/standings/").json()
    league = r['league']
    league_name = league['name']
    return league_name


def get_league_table(lid=0):
    if lid == 0:
        lid = input("Enter league ID: ")
    r = requests.get(base_url + "leagues-classic/" + str(lid) + "/standings/").json()
    teams = r['standings']
    league_standings = pd.json_normalize(teams["results"])
    table_standings = league_standings[['entry', 'entry_name', 'player_name', 'rank', 'total']]
    table_standings = table_standings.rename(  # renames the columns
        columns={'entry': 'ID',
                 'entry_name': 'Team Name',
                 'player_name': 'Player Name',
                 'total': 'Total',
                 'rank': 'Rank',
                 }
    )
    pd.set_option("display.colHeader_justify", "right")
    df = pd.DataFrame(table_standings)
    return df


def get_managers(lid=0):
    if lid == 0:
        lid = input("Enter league ID: ")
    r = requests.get(base_url + "leagues-classic/" + str(lid) + "/standings/").json()
    teams = r['standings']
    managers = [Manager(manager['player_name'], manager['entry_name'], manager['entry'],
                        manager['total'], manager['rank'],
                        get_gw_scores(manager['entry'])) for manager in teams['results']]
    return managers


def get_gw_scores(uid=0):
    if uid == 0:
        uid = input("Enter a User ID: ")
    rg = requests.get(base_url + "/entry/" + str(uid) + "/history/").json()
    gameweeks = rg['current']
    gw_scores = {"GW" + str(week['event']): week['points'] for week in gameweeks}
    if len(gw_scores) < 38:
        x = 38 - len(gw_scores)
        y = 1
        while y <= x:
            gw_scores["GW" + str(y)] = 0
            y += 1
    gw_scores = natsorted(gw_scores.values())
    return gw_scores


# function below works to get lowest scorer
def get_lowest_score_comments(all_managers, gw=0):
    low_score = -1
    lowest_player = []
    if gw == 0:
        gw = int(input("Enter a gameweek to find the lowest scorer: "))
    for man in all_managers:
        if man.scores[gw-1] < low_score or low_score < 0:
            low_score = man.scores[gw-1]
            lowest_player = [man.name]

        elif man.scores[gw-1] == low_score:
            lowest_player.append(man.name)
        else:
            pass
    if len(lowest_player) == 1:
        lowest_player_comment = " ".join(lowest_player) + " was lowest of GW" + str(gw) + " with a score of " + str(low_score)
    else:
        l_players = ", ".join(lowest_player[:-1]) + " and " + lowest_player[-1]
        lowest_player_comment = l_players + " were lowest of GW" + str(gw) + " with a score of " + str(low_score)
    return lowest_player_comment


def get_lowest_score(all_managers, gw=0):
    low_score = -1
    lowest_player = []
    if gw == 0:
        gw = int(input("Enter a gameweek to find the lowest scorer: "))
    for man in all_managers:
        if man.scores[gw-1] < low_score or low_score < 0:
            low_score = man.scores[gw-1]
            lowest_player = [man.name]
        elif man.scores[gw-1] == low_score:
            lowest_player.append(man.name)
        else:
            pass
    return lowest_player


def get_all_lowest(managers, current_gw=0):
    names_lowest = []
    gw = 1
    if current_gw == 0:
        current_gw = int(input("Enter GW so far: "))
    final_list = []
    while gw <= current_gw:
        names_lowest.append(get_lowest_score(managers, gw))
        gw += 1
    for my_list in names_lowest:
        for word in my_list:
            final_list.append(word)
    return final_list


def get_all_lowest_comments(managers, current_gw=38):
    names_lowest = []
    gw = 1
    if current_gw == 0:
        current_gw = int(input("Enter GW so far: "))
    final_list = []
    while gw <= current_gw:
        names_lowest.append(get_lowest_score_comments(managers, gw))
        gw += 1
    for my_list in names_lowest:
        for word in my_list:
            final_list.append(word)
    return names_lowest


# below converts my list to a dict with counts
def list_to_dict(a_list, show_output=False):
    counts = dict()
    for name in a_list:
        counts[name] = counts.get(name, 0) + 1
    if show_output:
        print(counts)
    return counts


# works out how much each player owes based on times they lost and input from above
def get_amount_owed(a_dict, price=0):
    new_dict = dict(a_dict)
    for key in new_dict:
        new_dict[key] *= float(price)
    return new_dict

