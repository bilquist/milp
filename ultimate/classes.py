
import itertools


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


class Team:

    def __init__(self, pods):
        self.pods = pods
        self.score = sum(pod.rank for pod in pods)

    def __str__(self):
        return str([pod.name for pod in self.pods])

    def update_pods_played_with(self):
        for comb in itertools.combinations(self.pods, 2):
            comb[0].play_with(comb[1])
            comb[1].play_with(comb[0])

    def get_mean_played_against_team(self, opponent_team):
        """Returns the combined mean times each pod on a team played against a pod on another team"""
        played_running_total = 0
        for p1 in self.pods:
            for p2 in opponent_team.pods:
                if p2 in p1.played_against:
                    played_running_total += p1.played_against[p2].get('count', 0)
        mean_played_against = played_running_total / (len(self.pods) + len(opponent_team.pods))
        return mean_played_against

    def have_pods_played_together(self, opponent_team):
        for p1 in self.pods:
            for p2 in opponent_team.pods:
                if (p2 in p1.played_with) or (p1 in p2.played_with):
                    return True
        return False


class Season:
    """
    - Each week, 3 teams combine together (and should only play with each other 1 week).
    - 2 games per week (so you interact with 8 other teams each week; 2 with and 6 against)
    - Ideally, shouldn't play against the same team more then 2x.
    - Algorithm should work for over 6 weeks, while keeping teams balanced
      (e.g. if I combine the 1st, 8th, and 12th best team (total 21), then their
       competition should be close to them such as 2nd, 7th, and 11th (total 20)
      ).
    """

    POD_COUNT = 48
    PODS_PER_TEAM = 3
    POD_PARTNERS_PER_WEEK = 2
    GAMES_PER_DAY = 2
    SCHEDULE_WEEKS = 6
    TOP_BOTTOM_POD_COUNT = 12
    MU = 50

    def __init__(self, pods):
        self.pods = pods
        self.sorted_pods = self.sort_pods_by_rank()
        # self.valid_teams = self.generate_valid_teams()
        self.schedule = {}

    #         self.valid_teams, self.valid_bottoms, self.valid_tops = self.generate_potential_teams()
    #         self.teams = {}

    def have_pods_played_together(self, team):
        for comb in itertools.combinations(team.pods, 2):
            if comb[1] in comb[0].played_with:
                return True
        return False

    def sort_pods_by_rank(self):
        """Sort pods by their self-reported rank and record top and bottom flags"""
        sorted_pods = sorted(self.pods, key=lambda x: x.rank, reverse=False)
        for pod in sorted_pods[:self.TOP_BOTTOM_POD_COUNT]:
            pod.is_bottom = True
        for pod in sorted_pods[-self.TOP_BOTTOM_POD_COUNT:]:
            pod.is_top = True
        return sorted_pods

    #     def generate_potential_teams(self):
    #         """
    #         Generate all the possible team pairings, respecting the rules of top
    #         and bottom pairing restrictions
    #         """
    #         valid_teams = []
    #         valid_bottoms = []
    #         valid_tops = []
    #         all_teams = itertools.combinations(self.pods, 3)
    #         for team in all_teams:
    #             bottom = max(pod.is_bottom for pod in team)
    #             top = max(pod.is_top for pod in team)
    #             if not(bottom and top):
    #                 t = Team(pods=team)
    #                 valid_teams.append(t)
    #             if not bottom:
    #                 valid_tops.append(t)
    #             if not top:
    #                 valid_bottoms.append(t)

    #         return valid_teams, valid_bottoms, valid_tops

    def generate_valid_teams(self):
        """Generate all valid pod combinations (aka, teams)"""

        valid_teams = []

        all_teams = itertools.combinations(self.pods, 3)
        for team in all_teams:
            bottom = max(pod.is_bottom for pod in team)
            top = max(pod.is_top for pod in team)
            if not (bottom and top):
                t = Team(pods=team)
                valid_teams.append(t)
        return valid_teams

    #     def generate_weekly_teams(self):
    #         """
    #         We want to find the best schedule for the week subject to the
    #         following constraints:
    #         1. Potential team has never been used in a prior week
    #         2. The deviation of score between the potential teams is as tight as can be
    #         """

    #         # First going to construct the teams that will play vs. tops (more restrictive)
    #         pass

    def generate_matchups(self, collections):
        """
        Generate potential matchups by creating team1 vs. team2 combinations
        from valid teams.
        """

        counter = 0
        matchups = dict()
        for ix, match in enumerate(itertools.product(*collections)):
            team1 = match[0]
            team2 = match[1]
            t1 = set(team1.pods)
            t2 = set(team2.pods)
            if len(t1.intersection(t2)) == 0:
                # Validate the pods on these teams have not previously played together
                # if not team1.have_pods_played_together(team2):
                if not (self.have_pods_played_together(team1) or self.have_pods_played_together(team2)):
                    counter += 1
                    # Update the delta by the penalty of playing against another pod multiple times
                    mean_played_against = team1.get_mean_played_against_team(team2)
                    if mean_played_against > 0:
                        delta = int(round(
                            max(abs(team1.score - team2.score), 1) * (self.MU * mean_played_against),
                            0
                        ))
                    else:
                        delta = abs(team1.score - team2.score)
                    if delta in matchups:
                        matchups[delta].append((team1, team2))
                    else:
                        matchups[delta] = [(team1, team2)]

        print(f'Generated {counter} matchups.')
        return matchups

    def generate_same_day_deltas(self, collections, schedules):
        """
        Generate potential matchups by creating team1 vs.team2 combinations
        from valid teams
        """

        #         print(f'Input collections:')
        #         print(collections)
        #         print(f'Input schedules:')
        #         print(schedules)
        matchups = dict()
        for ix, match in enumerate(itertools.product(*[collections, collections])):
            team1 = match[0]
            team2 = match[1]
            #             print(f'matching: {team1} vs. {team2}')
            if not (
                    (team1, team2) in [(event[0], event[1]) for event in schedules]
                    or (team2, team1) in [(event[0], event[1]) for event in schedules]
            ):
                t1 = set(team1.pods)
                t2 = set(team2.pods)
                if len(t1.intersection(t2)) == 0:
                    # Update the delta by the penalty of playing against another pod multiple times
                    mean_played_against = team1.get_mean_played_against_team(team2)
                    if mean_played_against > 0:
                        #                         print('found a penalty!')
                        delta = int(round(
                            max(abs(team1.score - team2.score), 1) * (self.MU * mean_played_against),
                            0
                        ))
                    #                         print(f'delta: {delta}')
                    else:
                        delta = abs(team1.score - team2.score)
                    #                         print(f'delta: {delta}')
                    if delta in matchups:
                        matchups[delta].append((team1, team2))
                    else:
                        matchups[delta] = [(team1, team2)]
            else:
                #                 print(f'discarding: {team1} vs.{team2}')
                pass
        return matchups

    def initialize_assignments(self):
        """
        Initialize an empty assignment object.
        - Get unique pods from tops: this will be used each round to determine
          which pods yet must be assigned
        """
        assignments = dict()
        for pod in self.sorted_pods:
            if pod not in assignments:
                assignments[pod] = None
        return assignments

    def get_remaining_pods(self, assignments):
        return [pod for pod in assignments.keys() if assignments[pod] is None]

    def generate_matchup_deltas(self, matchups, debug=False):
        deltas = dict()
        removals = list()
        for ix, match in enumerate(matchups):
            team1 = match[0]
            team2 = match[1]
            # Validate the pods on these teams have not previously played together
            if team1.have_pods_played_together(team2):
                # Pods have played together and can only do so once so remove this combination
                # matchups.remove(match)
                # removals.add(match)
                removals.append(ix)
            # We can continue evaluating this as a potential matchup
            else:
                # Update the delta by the penalty of playing against another pod multiple times
                mean_played_against = team1.get_mean_played_against_team(team2)
                if mean_played_against > 0:
                    delta = int(round(
                        max(abs(team1.score - team2.score), 1) * (self.MU * mean_played_against),
                        0
                    ))
                else:
                    delta = abs(team1.score - team2.score)
                if delta in deltas:
                    deltas[delta].append((team1, team2))
                else:
                    deltas[delta] = [(team1, team2)]

        # Remove the removals from matchups
        for index in removals:
            # matchups.remove(match)
            del removals[index]
        print(f'Removed {len(removals)} records from matchups.')

        return deltas

    def generate_first_schedule_of_day(self, matchups, assignments=None, debug=False):
        """
        Create a schedule of team1 vs. team2 for each team in a list. This is the
        first matchup of a day so the teams can be composed of any pods.
        """
        # Iterate throught the matchups and create delta values for each matchup pair
        total_values_to_check = 0
        for delta in matchups:
            total_values_to_check += len(matchups[delta])
        print(f'First schedule of day. {total_values_to_check} items to iterate.')

        # Get a list of deltas sorted from least to greatest
        deltas = list(matchups.keys())
        deltas.sort()

        # Initialize assignments
        if not assignments:
            assignments = self.initialize_assignments()

        # This is the score for the first match in a day
        # (score is the matching algorithm)
        # Initialize the function
        index = 0
        delta = deltas[0]
        cache = [(-1, -1)]
        remaining = self.get_remaining_pods(assignments)
        bypass = False
        debug_cntr = 0
        schedule = []
        team_stack = []

        while len(remaining) > 0:

            # Debug print statements
            debug_cntr += 1
            if debug and debug_cntr % 100000000 == 0:
                print(f'Debug:{debug_cntr / 100000000} (100M)\tIndex: {index}\Delta: {delta}\tschedule:')
                for pair in schedule:
                    print(pair[0], pair[1])
                print(f'remaining: {len(remaining)}')

            # Get current match
            matches = matchups[delta]
            match = matches[index]

            # Validate whether this match can be added to the stack
            if not bypass:
                team1 = match[0]
                team2 = match[1]
                # Check for pod existence
                is_pod_exhausted = False
                for pod in team1.pods + team2.pods:
                    if pod not in remaining:
                        is_pod_exhausted = True
                        break
                if not is_pod_exhausted:
                    # schedule.append(match)
                    schedule.append((match[0], match[1], delta, (match[0].score, match[1].score)))
                    team_stack.append(team1)
                    team_stack.append(team2)
                    cache.append((index, delta))
                    # Add the pods to the assignments
                    for pod in team1.pods:
                        assignments[pod] = delta
                    for pod in team2.pods:
                        assignments[pod] = delta

            # Reset bypass to False in case it was set to True
            bypass = False

            # See if we solved it
            remaining = self.get_remaining_pods(assignments)

            # Schedule unfinished.
            # 1. Get the next index if an index exists
            if len(remaining) > 0:
                index += 1
                if index >= len(matches):
                    # We've exhaused the current delta. Get the next.
                    try:
                        delta = min([d for d in list(matchups.keys()) if d > delta])
                        index = 0
                    except ValueError:
                        # There is no next delta... reverse course
                        team1 = team_stack.pop()
                        team2 = team_stack.pop()
                        schedule.pop()
                        #                     print(f'popping cache: {cache}')
                        #                     print(f'cur index/delta: {index}::{delta}')
                        index, delta = cache.pop()
                        bypass = True
                        for pod in team1.pods:
                            assignments[pod] = None
                        for pod in team2.pods:
                            assignments[pod] = None
                        if index == -1 and delta == -1:
                            # We went back further than possible. Give up and die.
                            if debug:
                                print(f'Assignments:\n{assignments}\n\n')
                                print(f'schedule:\n{schedule}\n\n')
                                print(f'team_stack:\n{team_stack}\n\n')
                                print(f'cache:\n{cache}\n')
                            raise ValueError("We died.")

        # Outside the while loop means solved
        if debug:
            print('SOLVED')
        return schedule

    def generate_subsequent_schedule_of_day(
            self, schedules, debug=False
    ):
        """Create matches subsequent to the first matches of the day"""
        # Teams stay the same for a day so now we need to rotate the teams to play
        # against different teams but also make sure they minimize the count of times
        # they've played other pods previously.

        shuffle_teams = []
        for event in schedules:
            shuffle_teams.append(event[0])
            shuffle_teams.append(event[1])

        # matchups = self.generate_same_day_matchups(*[shuffle_teams, shuffle_teams], schedules)
        matchups = self.generate_same_day_deltas(shuffle_teams, schedules)
        #         print(f'second matchups: {len(matchups)}')
        #         print(list(matchups.keys()))

        # Get unique pods from tops: this will be used each round to determine which pods yet must be assigned
        assignments = self.initialize_assignments()
        #         print('assignments:')
        #         print(assignments)

        # Get the new schedule for the day
        schedule2 = self.generate_first_schedule_of_day(
            matchups=matchups, assignments=assignments, debug=debug
        )
        return schedule2

    def update_teams_played_against(self, team1, team2):
        # After the first event of the day, update the played_against schedule
        # for event in schedule:
        # team1 = event[0]
        # team2 = event[1]
        for p1 in team1.pods:
            for p2 in team2.pods:
                p1.play_against(p2)
                p2.play_against(p1)

    def update_schedule(self, week, day, game, schedule):
        if week in self.schedule:
            if day in self.schedule[week]:
                if game in self.schedule[week][day]:
                    for event in schedule:
                        self.schedule[week][day][game].append({
                            'team1': event[0],
                            'team2': event[1],
                            'delta': event[2],
                            'team1_rank': event[0].score,
                            'team2_rank': event[1].score
                        })
                        self.update_teams_played_against(event[0], event[1])
                else:
                    self.schedule[week][day][game] = []
                    for event in schedule:
                        self.schedule[week][day][game].append({
                            'team1': event[0],
                            'team2': event[1],
                            'delta': event[2],
                            'team1_rank': event[0].score,
                            'team2_rank': event[1].score
                        })
                        self.update_teams_played_against(event[0], event[1])
            else:
                self.schedule[week][day] = {game: []}
                for event in schedule:
                    self.schedule[week][day][game].append({
                        'team1': event[0],
                        'team2': event[1],
                        'delta': event[2],
                        'team1_rank': event[0].score,
                        'team2_rank': event[1].score
                    })
                    self.update_teams_played_against(event[0], event[1])
        else:
            self.schedule[week] = {day: {game: []}}
            for event in schedule:
                self.schedule[week][day][game].append({
                    'team1': event[0],
                    'team2': event[1],
                    'delta': event[2],
                    'team1_rank': event[0].score,
                    'team2_rank': event[1].score
                })
                self.update_teams_played_against(event[0], event[1])
