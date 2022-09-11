import pandas as pd
from collections import Counter

from flaskFPL.main.functions import get_managers, get_league_table, get_league_name, get_all_lowest, get_amount_owed, list_to_dict, \
    get_all_lowest_comments,\
    get_all_nth_lowest_comments, latest_gw, get_all_nth_lowest
from flask import render_template, flash, Blueprint
from flaskFPL.main.forms import EnterID

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
@main.route('/home', methods=['GET', 'POST'])
def home():
    form = EnterID()
    if form.validate_on_submit():
        flash(f"Retrieved data for {get_league_name(form.league_id.data)}!", "success")

        # get basic league table
        df1 = get_league_table(form.league_id.data)

        # league name for showing on page
        league_name = get_league_name(form.league_id.data)

        # get the objects of each manager
        all_managers = get_managers(form.league_id.data)

        # get the comments for breakdown of lowest scorers
        lowest_comments = get_all_lowest_comments(all_managers)

        second_lowest_comments = get_all_nth_lowest_comments(all_managers, latest_gw, 1)

        third_lowest_comments = get_all_nth_lowest_comments(all_managers, latest_gw, 2)

        # get 2nd lowest comments
        # second_lowest_comments = get_all_nth_lowest_comments(all_managers, latest_gw, form.league_id.data)

        # get a list of all lowest players per week
        all_lowest = get_all_lowest(all_managers)

        # get all 2nd lowest
        all_second_lowest = get_all_nth_lowest(all_managers, latest_gw, 1)

        all_third_lowest = get_all_nth_lowest(all_managers, latest_gw, 2)

        # counts how many times they appear in the previous list
        times_last = list_to_dict(all_lowest)

        times_second_last = list_to_dict(all_second_lowest)

        times_third_last = list_to_dict(all_third_lowest)

        # calculates amount owed based on form input
        amount_owed_last = get_amount_owed(times_last, form.amount_owed.data)

        amount_owed_second_last = get_amount_owed(times_second_last, form.amount_owed_2.data)

        amount_owed_third_last = get_amount_owed(times_third_last, form.amount_owed_3.data)

        if int(form.select_one.data) == 1:
            amount_owed = amount_owed_last

        elif int(form.select_one.data) == 2:
            amount_owed = dict(Counter(amount_owed_last)+Counter(amount_owed_second_last))

        elif int(form.select_one.data) == 3:
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
        elif int(form.select_one.data) == 2:
            times_second_last_df = pd.DataFrame.from_dict(times_second_last, orient='index',
                                         columns=['Times Second Bottom'])

            times_second_last_df = times_second_last_df.rename_axis('Player Name')

            df = df.merge(times_second_last_df, how="outer", right_on='Player Name', left_on='Player Name')

            amount_owed_second_df = pd.DataFrame.from_dict(amount_owed_second_last, orient='index', columns=["Amount Owed"])

            # rename column
            amount_owed_second_df = amount_owed_second_df.rename_axis('Player Name')
            amount_owed_df = amount_owed_df.add(amount_owed_second_df, fill_value=0)

            df = df.merge(amount_owed_df, how="outer", right_on='Player Name', left_on='Player Name')
            # df = second_df.merge(amount_owed_second_df, how="outer", right_on='Player Name', left_on='Player Name')

        elif int(form.select_one.data) == 3:
            times_second_last_df = pd.DataFrame.from_dict(times_second_last, orient='index',
                                                          columns=['Times Second Bottom'])

            times_second_last_df = times_second_last_df.rename_axis('Player Name')

            df = df.merge(times_second_last_df, how="outer", right_on='Player Name', left_on='Player Name')

            amount_owed_second_df = pd.DataFrame.from_dict(amount_owed_second_last, orient='index',
                                                           columns=["Amount Owed"])

            # rename column
            amount_owed_second_df = amount_owed_second_df.rename_axis('Player Name')
            amount_owed_df = amount_owed_df.add(amount_owed_second_df, fill_value=0)
            # df = second_df.merge(amount_owed_df, how="outer", right_on='Player Name', left_on='Player Name')
            # df = second_df.merge(amount_owed_second_df, how="outer", right_on='Player Name', left_on='Player Name')

            times_third_last_df = pd.DataFrame.from_dict(times_third_last, orient='index',
                                                          columns=['Times Third Bottom'])

            times_third_last_df = times_third_last_df.rename_axis('Player Name')

            third_df = df.merge(times_third_last_df, how="outer", right_on='Player Name', left_on='Player Name')

            amount_owed_third_df = pd.DataFrame.from_dict(amount_owed_third_last, orient='index',
                                                           columns=["Amount Owed"])
            # rename column
            amount_owed_third_df = amount_owed_third_df.rename_axis('Player Name')
            amount_owed_df = amount_owed_df.add(amount_owed_third_df, fill_value=0)

            df = third_df.merge(amount_owed_df, how="outer",
                                right_on='Player Name', left_on='Player Name')

        df = df.fillna(0)

        return render_template("fpl.html",
                               title=f"League Data for {league_name}", tables=[df.to_html(classes='data', index=False)],
                               titles=df.columns.values, form=form, all_lowest=all_lowest,
                               amount_owed=amount_owed,
                               lowest_comments=lowest_comments, league_name=league_name,
                               second_lowest_comments=second_lowest_comments,
                               third_lowest_comments=third_lowest_comments)
    return render_template("home.html", title="Home", form=form)


@main.route("/about")
def about():
    return render_template('about.html', title='About')


@main.route('/lowest', methods=['GET', 'POST'])
def lowest():
    return render_template("lowest.html", title="Lowest Scorers", legend="Lowest Scorers")



