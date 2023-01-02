
class Pod:
    is_bottom = False
    is_top = False

    def __init__(self, name, rank):
        self.name = name
        self.rank = rank
        self.played_with = {}
        self.played_against = {}

    def play_with(self, pod):
        if pod in self.played_with:
            self.played_with[pod]['count'] += 1
            # self.played_with (things like week, etc. could go here)
        else:
            self.played_with[pod] = {'count': 1}

    def play_against(self, pod):
        if pod in self.played_against:
            self.played_against[pod]['count'] += 1
        else:
            self.played_against[pod] = {'count': 1}

    def __str__(self):
        return str(self.name)
