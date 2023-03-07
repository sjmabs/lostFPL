
# for getting league data like name etc - dont need to save to db as getting from fpl api
class League:
    def __init__(self, lid, name, table, all_nth_lowest_players, all_nth_lowest_comments):
        self.lid = lid
        self.name = name
        self.table = table
        self.all_nth_lowest_players = all_nth_lowest_players
        self.all_nth_lowest_comments = all_nth_lowest_comments

    def __repr__(self):
        return f"Post('{self.name}', {self.lid}')"


# used to display manager details - dont need to save to db as getting from fpl api
class Manager:
    def __init__(self, name, teamname, entry, total, rank, scores):
        self.name = name
        self.teamname = teamname
        self.entry = entry
        self.total = total
        self.scores = scores

    def __repr__(self):
        return f"Manager('{self.name}', '{self.teamname}', '{self.entry}')"

