import time

import pandas as pd
from collections import Counter

from flaskFPL.main.functions import get_managers, get_league_data, get_amount_owed, \
    list_to_dict, get_nth_lowest_info, get_nth_lowest, latest_week, get_all_nth_lowest, \
    get_all_nth_lowest_comments_scorer, \
    get_all_nth_lowest_scorer


from flask import render_template, flash, Blueprint
from flaskFPL.main.forms import EnterID

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
@main.route('/home', methods=['GET', 'POST'])
def home():
    form = EnterID()
    if form.validate_on_submit():
        start = time.time()
        league_data = get_league_data(form.league_id.data)
        # league name for showing on page
        league_name = league_data['league_name']
        flash(f"Retrieved data for {league_data['league_name']}!", "success")

        # get basic league table
        df1 = league_data['league_table']


        # get the objects of each manager
        all_managers = get_managers(form.league_id.data)
        start_length = len(all_managers)

        # won't need this now
        lowest_comments = get_all_nth_lowest_comments(all_managers)
        all_lowest = get_all_nth_lowest(all_managers)
        times_last = list_to_dict(all_lowest)

        # calculates amount owed based on form input
        #won't need this now
        amount_owed_last = get_amount_owed(times_last, form.amount_owed.data)

        if "Scores" in form.scores_scorers.data:
            # get the comments for breakdown of lowest scorers

            data = get_nth_lowest_info(all_managers, latest_week, int(form.select_one.data))

            if int(form.select_one.data) == 2:
                second_lowest_comments = get_all_nth_lowest_comments(all_managers, latest_week, 1)
                all_second_lowest = get_all_nth_lowest(all_managers, latest_week, 1)

                times_second_last = list_to_dict(all_second_lowest)

                amount_owed_second_last = get_amount_owed(times_second_last, form.amount_owed_2.data)
                if int(form.select_one.data) >= 3:
                    second_lowest_comments = get_all_nth_lowest_comments(all_managers, latest_week, 1)
                    all_second_lowest = get_all_nth_lowest(all_managers, latest_week, 1)

                    times_second_last = list_to_dict(all_second_lowest)

                    amount_owed_second_last = get_amount_owed(times_second_last, form.amount_owed_2.data)

                    third_lowest_comments = get_all_nth_lowest_comments(all_managers, latest_week, 2)

                    all_third_lowest = get_all_nth_lowest(all_managers, latest_week, 2)

                    times_third_last = list_to_dict(all_third_lowest)

                    amount_owed_third_last = get_amount_owed(times_third_last, form.amount_owed_3.data)

        else:
            if int(form.select_one.data) == 2:
                second_lowest_comments = get_all_nth_lowest_comments_scorer(all_managers, 2,  latest_week, 1)

                all_second_lowest = get_all_nth_lowest_scorer(all_managers, 2, latest_week, 1)

                times_second_last = list_to_dict(all_second_lowest)

                amount_owed_second_last = get_amount_owed(times_second_last, form.amount_owed_2.data)

            elif int(form.select_one.data) == 3:
                second_lowest_comments = get_all_nth_lowest_comments_scorer(all_managers, 3, latest_week, 1)

                all_second_lowest = get_all_nth_lowest_scorer(all_managers, 3, latest_week, 1)

                times_second_last = list_to_dict(all_second_lowest)

                amount_owed_second_last = get_amount_owed(times_second_last, form.amount_owed_2.data)

                third_lowest_comments = get_all_nth_lowest_comments_scorer(all_managers, 3, latest_week, 2)

                all_third_lowest = get_all_nth_lowest_scorer(all_managers, 3, latest_week, 2)

                times_third_last = list_to_dict(all_third_lowest)

                amount_owed_third_last = get_amount_owed(times_third_last, form.amount_owed_3.data)

        if int(form.select_one.data) >= 1:
            amount_owed = amount_owed_last

            if int(form.select_one.data) >= 2:
                amount_owed = dict(Counter(amount_owed_last) + Counter(amount_owed_second_last))

                if int(form.select_one.data) >= 3:
                    amount_owed = dict(
                        Counter(amount_owed_last)
                        + Counter(amount_owed_second_last)
                        + Counter(amount_owed_third_last))

        # make a table based on amounts owed per player

        amount_owed_df = pd.DataFrame.from_dict(amount_owed_last, orient='index', columns=["Amount Owed"])

        # rename column
        amount_owed_df = amount_owed_df.rename_axis('Player Name')

        times_last_df = pd.DataFrame.from_dict(times_last, orient='index', columns=['Times Bottom'])

        # rename the column so it is same as df1
        times_last_df = times_last_df.rename_axis('Player Name')

        df = df1.merge(times_last_df, how="outer", right_on='Player Name', left_on='Player Name')

        # df = df.merge(amount_owed_df, how="outer", right_on='Player Name', left_on='Player Name')
        if int(form.select_one.data) == 1:
            df = df.merge(amount_owed_df, how="outer", right_on='Player Name', left_on='Player Name')
            df = df.astype(
                {"ID": "int", "Rank": "int", "Total": "int", "Times Bottom": "int"})
        elif int(form.select_one.data) == 2:
            times_second_last_df = pd.DataFrame.from_dict(times_second_last, orient='index',
                                                          columns=['Times Second Bottom'])

            times_second_last_df = times_second_last_df.rename_axis('Player Name')

            df = df.merge(times_second_last_df, how="outer", right_on='Player Name', left_on='Player Name').fillna(0)

            amount_owed_second_df = pd.DataFrame.from_dict(amount_owed_second_last, orient='index',
                                                           columns=["Amount Owed"])

            # rename column
            amount_owed_second_df = amount_owed_second_df.rename_axis('Player Name')
            amount_owed_df = amount_owed_df.add(amount_owed_second_df, fill_value=0)

            df = df.merge(amount_owed_df, how="outer", right_on='Player Name', left_on='Player Name')
            # df = second_df.merge(amount_owed_second_df, how="outer", right_on='Player Name', left_on='Player Name')
            df = df.astype(
                {"ID": "int", "Rank": "int", "Total": "int", "Times Bottom": "int", "Times Second Bottom": "int"})

        elif int(form.select_one.data) == 3:
            times_second_last_df = pd.DataFrame.from_dict(times_second_last, orient='index',
                                                          columns=['Times Second Bottom']).fillna(0)

            times_second_last_df = times_second_last_df.rename_axis('Player Name')

            df = df.merge(times_second_last_df, how="outer", right_on='Player Name', left_on='Player Name').fillna(0)

            amount_owed_second_df = pd.DataFrame.from_dict(amount_owed_second_last, orient='index',
                                                           columns=["Amount Owed"])

            # rename column
            amount_owed_second_df = amount_owed_second_df.rename_axis('Player Name')
            amount_owed_df = amount_owed_df.add(amount_owed_second_df, fill_value=0)

            times_third_last_df = pd.DataFrame.from_dict(times_third_last, orient='index',
                                                         columns=['Times Third Bottom']).fillna(0)

            times_third_last_df = times_third_last_df.rename_axis('Player Name')

            third_df = df.merge(times_third_last_df, how="outer", right_on='Player Name', left_on='Player Name').fillna(0)

            amount_owed_third_df = pd.DataFrame.from_dict(amount_owed_third_last, orient='index',
                                                          columns=["Amount Owed"])
            # rename column
            amount_owed_third_df = amount_owed_third_df.rename_axis('Player Name')
            amount_owed_df = amount_owed_df.add(amount_owed_third_df, fill_value=0)

            df = third_df.merge(amount_owed_df, how="outer",
                                right_on='Player Name', left_on='Player Name')

            df = df.astype(
                {"ID": "int", "Rank": "int", "Total": "int", "Times Bottom": "int", "Times Second Bottom": "int",
                 "Times Third Bottom": "int"})

        df = df.fillna(0)
        df = df[df["Player Name"].str.contains("Nobody") == False]
        df.drop("ID", inplace=True, axis=1)

        end = time.time()

        print(end - start)

        if int(form.select_one.data) == 1:
            return render_template("fpl.html",
                                   title=f"League Data for {league_name}",
                                   tables=[df.to_html(classes=['data', 'table-striped'], justify="center", index=False)],
                                   titles=df.columns.values, form=form, all_lowest=all_lowest,
                                   amount_owed=amount_owed,
                                   lowest_comments=lowest_comments, league_name=league_name)

        elif int(form.select_one.data) == 2:

            return render_template("fpl.html",
                                   title=f"League Data for {league_name}",
                                   tables=[df.to_html(classes=['data', 'table-striped'], justify="center", index=False)],
                                   amount_owed=amount_owed,
                                   lowest_comments=lowest_comments, league_name=league_name,
                                   second_lowest_comments=second_lowest_comments)

        return render_template("fpl.html",
                               title=f"League Data for {league_name}",
                               tables=[df.to_html(classes=['data', 'table-striped'], justify="center", index=False)],
                               titles=df.columns.values, form=form, all_lowest=all_lowest,
                               amount_owed=amount_owed,
                               lowest_comments=lowest_comments, league_name=league_name,
                               second_lowest_comments=second_lowest_comments,
                               third_lowest_comments=third_lowest_comments)
    return render_template("home.html", title="Home", form=form)


@main.route('/about')
def about():
    return render_template("about.html", title="About")


@main.route('/leagueID')
def LeagueID():
    return render_template("LeagueIDGuide.html", title="How To Find Your League ID")
