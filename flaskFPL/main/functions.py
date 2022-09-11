import pandas as pd
import requests
from flaskFPL.main.models import Manager
from natsort import natsorted

pd.set_option('display.max_columns', None)
base_url = 'https://fantasy.premierleague.com/api/'


def finished_week():
    gws = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
    gws1 = gws['events']
    current_gw = 0
    for gw in gws1:
        if gw['finished']:
            current_gw += 1
    if current_gw == 0:
        print("off season")
        # add an off season page link
    return current_gw


latest_gw = finished_week()


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
    to_remove = len(gameweeks) - latest_gw
    while to_remove != 0:
        gameweeks.pop()
        to_remove -= 1
    gw_scores = {"GW" + str(week['event']): week['points'] for week in gameweeks}
    gw_scores = natsorted(gw_scores.values())
    while len(gw_scores) != latest_gw:
        gw_scores.insert(0, 0)

    return gw_scores


# function below works to get lowest scorer
def get_lowest_score_comments(all_managers, gw=latest_gw):
    low_score = get_lowest_score(all_managers, gw)
    lowest_player = get_lowest_player(all_managers, gw)
    if len(lowest_player) == 1:
        lowest_player_comment = " ".join(lowest_player) + " was lowest of GW" + str(gw)\
                                + " with a score of " + str(low_score)
    else:
        l_players = ", ".join(lowest_player[:-1]) + " and " + lowest_player[-1]
        lowest_player_comment = l_players + " were lowest of GW" + str(gw) + " with a score of " + str(low_score)
    return lowest_player_comment


def get_nth_lowest_score_comments(all_managers, gw=latest_gw, n=0):
    if n == 0:
        low_score = get_lowest_score(all_managers, gw)
        lowest_player = get_lowest_player(all_managers, gw)
    else:
        low_score = get_nth_lowest_score(all_managers, gw, n)
        lowest_player = get_nth_lowest_player(all_managers, gw, n)
    if n+1 == 1:
        suffix = "st"
    elif n+1 == 2:
        suffix = "nd"
    elif n+1 == 3:
        suffix = "rd"
    else:
        suffix = "th"
    if len(lowest_player) == 1:
        lowest_player_comment = " ".join(lowest_player) + " was " + str(n+1) + suffix + " lowest of GW" + str(gw)\
                                + " with a score of " + str(low_score)
    else:
        l_players = ", ".join(lowest_player[:-1]) + " and " + lowest_player[-1]
        lowest_player_comment = l_players + " were " + str(n+1) + suffix + " lowest of GW" + str(gw) + " with a score of " + str(low_score)
    return lowest_player_comment


def get_lowest_player(all_managers, gw=latest_gw):
    low_score = get_lowest_score(all_managers, gw)
    lowest_player = []
    for man in all_managers:
        if man.scores[gw-1] == low_score:
            lowest_player.append(man.name)
        else:
            pass
    return lowest_player


def get_nth_lowest_player(all_managers, gw=latest_gw, n=0):
    low_score = get_nth_lowest_score(all_managers, gw, n)
    nth_lowest_player = []
    for man in all_managers:
        if man.scores[gw-1] == low_score:
            nth_lowest_player.append(man.name)
        else:
            pass
    return nth_lowest_player


def get_lowest_score(all_managers, gw=latest_gw):
    low_score = -1
    for man in all_managers:
        if man.scores[gw-1] < low_score or low_score < 0:
            low_score = man.scores[gw-1]
        else:
            pass
    return low_score


def get_nth_lowest_score(all_managers, gw=latest_gw, n=0):
    all_managers_copy = all_managers.copy()
    if n == 0:
        return get_lowest_score(all_managers, gw)
    low_score = get_lowest_score(all_managers, gw)
    for man in all_managers:
        if man.scores[gw - 1] == low_score:
            all_managers_copy.remove(man)
    if n == 2:
        low_score = get_nth_lowest_score(all_managers_copy, gw, n+1)
    else:
        low_score = get_lowest_score(all_managers_copy, gw)
    return low_score


def get_all_lowest(all_managers, current_gw=latest_gw):
    names_lowest = []
    gw = 1
    final_list = []
    while gw <= current_gw:
        names_lowest.append(get_lowest_player(all_managers, gw))
        gw += 1
    for my_list in names_lowest:
        for word in my_list:
            final_list.append(word)
    return final_list


def get_all_nth_lowest(all_managers, current_gw=latest_gw, n=0):
    names_lowest = []
    gw = 1
    final_list = []
    while gw <= current_gw:
        names_lowest.append(get_nth_lowest_player(all_managers, gw, n))
        gw += 1
    for my_list in names_lowest:
        for word in my_list:
            final_list.append(word)
    return final_list


def get_all_lowest_comments(managers, current_gw=latest_gw):
    names_lowest = []
    gw = 1
    final_list = []
    while gw <= current_gw:
        names_lowest.append(get_lowest_score_comments(managers, gw))
        gw += 1
    for my_list in names_lowest:
        for word in my_list:
            final_list.append(word)
    return names_lowest


def get_all_nth_lowest_comments(managers, current_gw=latest_gw, n=0):
    names_lowest = []
    gw = 1
    final_list = []
    while gw <= current_gw:
        names_lowest.append(get_nth_lowest_score_comments(managers, gw, n))
        gw += 1
    for my_list in names_lowest:
        for word in my_list:
            final_list.append(word)
    return names_lowest


# below converts my list to a dict with counts
def list_to_dict(a_list):
    counts = dict()
    for name in a_list:
        counts[name] = counts.get(name, 0) + 1
    return counts


# works out how much each player owes based on times they lost and input from above
def get_amount_owed(a_dict, price=0):
    new_dict = dict(a_dict)
    for key in new_dict:
        new_dict[key] *= float(price)
    return new_dict



