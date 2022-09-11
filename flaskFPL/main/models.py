
# for getting league data like name etc - dont need to save to db as getting from fpl api
class League:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Post('{self.name}', {self.id}')"


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

