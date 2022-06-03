import pandas as pd

from flaskFPL.functions import get_managers, get_league_table, get_league_name, get_gw_scores, get_lowest_score,\
    get_all_lowest, get_amount_owed, list_to_dict, get_lowest_score_comments, get_all_lowest_comments
from flask import render_template, flash
from flaskFPL import app
from flaskFPL.forms import EnterID


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
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

        # get the comments for breakdown of lowest scorer
        lowest_comments = get_all_lowest_comments(all_managers)

        # get a list of all lowest players per week
        all_lowest = get_all_lowest(all_managers)

        # counts how many times they appear in the previous list
        times_last = list_to_dict(all_lowest)

        # calculates amount owed based on form input
        amount_owed = get_amount_owed(times_last, form.amount_owed.data)

        # fixes df orientation and adds the times last column
        df3 = pd.DataFrame.from_dict(times_last, orient='index', columns=['Times Last'])

        # rename the column so it is same as df1
        df3 = df3.rename_axis('Player Name')

        # merge both tables
        df4 = df1.merge(df3, how="outer", right_on='Player Name', left_on='Player Name')

        # make a table based on amounts owed per player

        df2 = pd.DataFrame.from_dict(amount_owed, orient='index', columns=["Amount Owed"])

        # rename column
        df2 = df2.rename_axis('Player Name')

        # merge all tables
        df5 = df4.merge(df2, how="outer", right_on='Player Name', left_on='Player Name')

        # make nan show as 0
        df5 = df5.fillna(0)

        return render_template("fpl.html",
                               title="League Data", tables=[df5.to_html(classes='data', index=False)],
                               titles=df5.columns.values, form=form, all_lowest=all_lowest, amount_owed=amount_owed,
                               lowest_comments=lowest_comments, league_name=league_name)
    return render_template("home.html", title="Home", form=form)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route('/lowest', methods=['GET', 'POST'])
def lowest():
    return render_template("lowest.html", title="Lowest Scorers", legend="Lowest Scorers")



