import pandas as pd
import requests
from flaskFPL.main.models import Manager


# check the week has finished so that we get fully updated scores
def finished_week():
    gws = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
    gws1 = gws['events']
    latest_finished_gw = 0
    for gw in gws1:
        if gw['is_current']:
            latest_finished_gw = gw['id'] - 1
    if latest_finished_gw == 0:
        print("off season")
        # add an off season page link
    return latest_finished_gw


latest_week = finished_week()


# gets the league name and table
def get_league_data(lid=0):
    if lid == 0:
        lid = input("Enter league ID: ")
    r = requests.get("https://fantasy.premierleague.com/api/" + "leagues-classic/" + str(lid) + "/standings/").json()
    league = r['league']
    league_name = league['name']
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
    league_data = {'league_name': league_name, 'league_table': df}
    return league_data


def get_managers(lid=654321):
    if lid == 0:
        lid = input("Enter league ID: ")
    r = requests.get("https://fantasy.premierleague.com/api/" + "leagues-classic/" + str(lid) + "/standings/").json()
    teams = r['standings']
    managers = [Manager(manager['player_name'], manager['entry_name'], manager['entry'],
                        manager['total'], manager['rank'],
                        get_gw_scores(manager['entry'])) for manager in teams['results']]
    return managers


def get_gw_scores(uid=0):
    if uid == 0:
        uid = input("Enter a User ID: ")
    rg = requests.get("https://fantasy.premierleague.com/api/" + "/entry/" + str(uid) + "/history/").json()
    gameweeks = rg['current']
    gw_scores = {"GW" + str(week['event']): week['points'] for week in gameweeks}
    if list(gw_scores)[-1] != f"GW{latest_week}":
        gw_scores.popitem()
    # added to fix issue with late joiners having no scores for the weeks they weren't playing - made them 0
    gw_start = 1
    while len(gw_scores) != latest_week:
        gw_scores[f"GW{gw_start}"] = 0
        gw_start += 1
    return gw_scores


# find the lowest score and name or number of players the user enters in their selection for the given gw
def get_nth_lowest_info(all_managers, gw=latest_week, n=0):
    gw_scores = []
    # retrieve all players scores for the week
    for man in all_managers:
        gw_scores.append(man.scores[f"GW{gw}"])
    # sort them lowest => highest
    gw_scores.sort()
    # remove duplicates
    gw_scores = list(dict.fromkeys(gw_scores))

    lowest_info_list = []
    x = 0
    while x <= int(n):
        # check if list has enough for our requirement and if not assign None
        if len(gw_scores) <= x:
            nth_lowest_score = None

        else:
            # else assign the x index score in the list
            nth_lowest_score = gw_scores[x]
        lowest_player = []
        # check if lowest_score exists and if not then nobody is lowest for that specific position
        if nth_lowest_score is None:
            lowest_player = ["Nobody"]
        # else we look at all managers and see who has the lowest score and add their name to the lowest player list
        else:
            for man in all_managers:
                if man.scores[f"GW{gw}"] == nth_lowest_score:
                    lowest_player.append(man.name)
                else:
                    pass
        lowest_info = {f'{x}lowest_score': nth_lowest_score, f'{x}lowest_player': lowest_player}
        lowest_info_list.append(lowest_info)
        x += 1
    lowest_info_list.append({'gw': gw})
    return lowest_info_list


def get_nth_lowest_score_comments(all_managers, gw, n):
    lowest_info = get_nth_lowest_info(all_managers, gw, n)
    x = 0
    lowest_player_comments = []
    while x < len(lowest_info) - 1:
        if x == 0:
            suffix = "st"
        elif x == 1:
            suffix = "nd"
        elif x == 2:
            suffix = "rd"
        else:
            suffix = "th"
        if len(lowest_info[x][f'{x}lowest_player']) == 1:
            if lowest_info[x][f'{x}lowest_player'] == ["Nobody"]:
                if x == 0:
                    lowest_player_comment = " ".join(lowest_info[x][f'{x}lowest_player']) + " was lowest of GW" + str(gw)
                else:
                    lowest_player_comment = " ".join(lowest_info[x][f'{x}lowest_player']) + " was " + str(x + 1) \
                                            + suffix + " lowest of GW" + str(gw)
            else:
                if x == 0:
                    lowest_player_comment = " ".join(lowest_info[x][f'{x}lowest_player']) + " was lowest of GW" + str(gw) \
                                            + " with a score of " + str(lowest_info[x][f'{x}lowest_score'])
                else:
                    lowest_player_comment = " ".join(lowest_info[x][f'{x}lowest_player']) + " was " + str(x + 1) \
                                            + suffix + " lowest of GW" + str(gw) + " with a score of " \
                                            + str(lowest_info[x][f'{x}lowest_score'])
        elif len(lowest_info[x][f'{x}lowest_player']) == len(all_managers):
            lowest_player_comment = "Everybody was lowest of GW" + str(gw) + " with a score of " \
                                    + str(lowest_info[x][f'{x}lowest_score'])
        else:
            if x == 0:
                lowest_player_comment = ", ".join(lowest_info[x][f'{x}lowest_player'][:-1]) + " and " \
                                        + lowest_info[x][f'{x}lowest_player'][-1]\
                                        + " were lowest of GW" + str(gw) + " with a score of " \
                                        + str(lowest_info[x][f'{x}lowest_score'])
            else:
                lowest_player_comment = ", ".join(lowest_info[x][f'{x}lowest_player'][:-1]) + " and " \
                                        + lowest_info[x][f'{x}lowest_player'][-1]\
                                        + " were " + str(x+1) + suffix + " lowest of GW" + str(gw) \
                                        + " with a score of " + str(lowest_info[x][f'{x}lowest_score'])
        lowest_player_comments.append(lowest_player_comment)
        x += 1
    return lowest_player_comments


# returns a list of lists of players names every time they came nth last. each nth index of list relates to the place
def get_all_nth_lowest_players(all_managers, current_gw=latest_week, n=0):
    final_list = []
    gw = 1
    # loop through each week
    while gw <= current_gw:
        x = 0
        # get information on where they came for each week
        info = get_nth_lowest_info(all_managers, gw, n) # returns dictionaries of all lowest people i asked for.
        while x <= int(n):
            if len(final_list) <= int(n):
                final_list.append([])
            # put just the names into a list based on their position (x)
            names_lowest = info[x][f'{x}lowest_player']
            for name in names_lowest:
                final_list[x].append(name)
            x += 1
        gw += 1
    return final_list


def get_all_nth_lowest_comments(all_managers, current_gw=latest_week, n=0):
    final_list = []
    gw = 1
    # loop through each week
    while gw <= latest_week:
        x = 0
        # get information on where they came for each week
        # info = data
        info = get_nth_lowest_score_comments(all_managers, gw, n) # returns dictionaries of all lowest people i asked for.
        while x <= int(n):
            if len(final_list) <= int(n):
                final_list.append([])
            # put just the comments into a list based on their position (x)
            final_list[x].append(info[x])
            x += 1
        gw += 1
    return final_list


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
        new_dict[key] *= price
    return new_dict


def get_nth_lowest_info_scorer(all_managers, gw=latest_week, n=0):
    lowest_players = []
    if n == 0:
        return get_nth_lowest_info(all_managers, gw, n)
    # if we want to get a number of lowest scorers rather than going by score we have to count how many we currently
    # have and continue to add more until we have the amount we are after.
    x = 0
    while len(lowest_players) <= int(n):
        lowest_players.extend(get_nth_lowest_info(all_managers, gw, x)[x][f'{x}lowest_player'])
        x += 1

    info = get_nth_lowest_info(all_managers, gw, x - 1)
    index = (int(n) + 2) - len(info)
    i = 1
    while i <= index:
        if index == 1 and len(info) != 2:
            dict_to_merge = {f'{i+1}lowest_score': None, f'{i+1}lowest_player': ['Nobody']}
            info.insert(i+1, dict_to_merge)
            i += 1
        elif index == 1 and len(info) == 2:
            dict_to_merge = {f'{i}lowest_score': None, f'{i}lowest_player': ['Nobody']}
            info.insert(i, dict_to_merge)
            i += 1
        elif i <= index:
            dict_to_merge = {f'{i}lowest_score': None, f'{i}lowest_player': ['Nobody']}
            info.insert(i, dict_to_merge)
            i += 1

    return info


def get_nth_lowest_score_comments_scorer(all_managers, gw=latest_week, n=0):
    lowest_info = get_nth_lowest_info_scorer(all_managers, gw, n)
    x = 0
    lowest_player_comments = []
    while x < len(lowest_info) - 1:
        lowest_player_names = lowest_info[x][f'{x}lowest_player']
        if x == 0:
            suffix = "st"
        elif x == 1:
            suffix = "nd"
        elif x == 2:
            suffix = "rd"
        else:
            suffix = "th"
        if len(lowest_info[x][f'{x}lowest_player']) == 1:
            if lowest_info[x][f'{x}lowest_player'] == ["Nobody"]:
                if x == 0:
                    lowest_player_comment = " ".join(
                        lowest_info[x][f'{x}lowest_player']) + " was lowest of GW" + str(gw)
                else:
                    lowest_player_comment = " ".join(lowest_info[x][f'{x}lowest_player']) + " was " + str(x + 1) \
                                            + suffix + " lowest of GW" + str(gw)
            else:
                if x == 0:
                    lowest_player_comment = " ".join(
                        lowest_info[x][f'{x}lowest_player']) + " was lowest of GW" + str(gw) \
                                            + " with a score of " + str(lowest_info[x][f'{x}lowest_score'])
                else:
                    lowest_player_comment = " ".join(lowest_info[x][f'{x}lowest_player']) + " was " + str(x + 1) \
                                            + suffix + " lowest of GW" + str(gw) + " with a score of " \
                                            + str(lowest_info[x][f'{x}lowest_score'])
        elif len(lowest_info[x][f'{x}lowest_player']) == len(all_managers):
            lowest_player_comment = "Everybody was lowest of GW" + str(gw) + " with a score of " \
                                    + str(lowest_info[x][f'{x}lowest_score'])
        else:
            if x == 0:
                lowest_player_comment = ", ".join(lowest_info[x][f'{x}lowest_player'][:-1]) + " and " \
                                        + lowest_info[x][f'{x}lowest_player'][-1] \
                                        + " were lowest of GW" + str(gw) + " with a score of " \
                                        + str(lowest_info[x][f'{x}lowest_score'])
            else:
                lowest_player_comment = ", ".join(lowest_info[x][f'{x}lowest_player'][:-1]) + " and " \
                                        + lowest_info[x][f'{x}lowest_player'][-1] \
                                        + " were " + str(x + 1) + suffix + " lowest of GW" + str(gw) \
                                        + " with a score of " + str(lowest_info[x][f'{x}lowest_score'])
        lowest_player_comments.append(lowest_player_comment)
        x += 1
    return lowest_player_comments


def get_all_nth_lowest_players_scorer(all_managers, current_gw=latest_week, n=0):
    final_list = []
    gw = 1
    # loop through each week
    while gw <= current_gw:
        x = 0
        # get information on where they came for each week
        info = get_nth_lowest_info_scorer(all_managers,  gw, n) # returns dictionaries of all lowest people i asked for.
        while x <= n:
            try:
                if len(final_list) <= n:
                    final_list.append([])
                # put just the names into a list based on their position (x)
                names_lowest = info[x][f'{x}lowest_player']
                for name in names_lowest:
                    final_list[x].append(name)
            except IndexError:
                pass
            x += 1
        gw += 1
    if not final_list[-1]:
        final_list.pop()
    return final_list


def get_all_nth_lowest_comments_scorer(all_managers, current_gw=latest_week, n=0):
    final_list = []
    gw = 1
    # loop through each week

    while gw <= latest_week:
        x = 0
        # get information on where they came for each week
        info = get_nth_lowest_score_comments_scorer(all_managers, gw, n) # returns dictionaries of all lowest people i asked for.
        while x <= int(n):
            if len(final_list) <= int(n):
                final_list.append([])
            # put just the comments into a list based on their position (x)
            final_list[x].append(info[x])
            x += 1
        gw += 1
    return final_list

