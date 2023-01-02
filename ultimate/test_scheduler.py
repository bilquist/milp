
import json
import os

from ultimate.models.pod import Pod
from ultimate.models.season import Season
from ultimate.optimizers.optimizer2 import main as optimizer
from ultimate.utils import generate_output


def main():

    BASEPATH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isdir(os.path.join(BASEPATH_DIR, 'data')):
        os.makedirs(os.path.join(BASEPATH_DIR, 'data'))

    GAMES_PER_DAY = 2
    GAMES_PER_WEEK = 1
    SCHEDULE_WEEKS = 6
    debug = True

    pods = [Pod(name=ix, rank=ix) for ix in range(1, 43)]
    season = Season(pods=pods)

    NUM_TOP = 12
    NUM_BOT = 12
    MAX_PLAY_WITH = 1
    MAX_PLAY_AGAINST = 3

    for ix in range(0, SCHEDULE_WEEKS):
        for iy in range(0, GAMES_PER_WEEK):
            daily_schedules = []
            # for iz in range(0, GAMES_PER_DAY):
            print(f'{ix}:{iy}:::')
            games_teams = optimizer(
                pods,
                num_top=NUM_TOP,
                num_bot=NUM_BOT,
                max_play_with=MAX_PLAY_WITH,
                max_play_against=MAX_PLAY_AGAINST,
                games_per_day=GAMES_PER_DAY
            )
            # return games
            print(f'****len(games): {len(games_teams)}')
            print(f'****len(teams): {len(games_teams[-1])}')
            for kk in range(len(games_teams)):  # games
                schedule = []
                for tt in range(0, len(games_teams[kk]), 2):  # teams
                    team1 = games_teams[kk][tt]
                    team2 = games_teams[kk][tt + 1]
                    score1 = sum([p.rank for p in team1.pods])
                    score2 = sum([p.rank for p in team2.pods])
                    schedule.append((team1, team2, abs(score1 - score2), (score1, score2)))
                season.update_schedule(ix + 1, iy + 1, kk + 1, schedule)

                # Update the 'played with' for pods on the last game of the day
                if kk == (GAMES_PER_DAY - 1):
                    for event in schedule:
                        event[0].update_pods_played_with()
                        event[1].update_pods_played_with()

    with open(os.path.join(BASEPATH_DIR, 'data', 'out.json'), 'w') as f:
        f.writelines(json.dumps(season.schedule, indent=2, default=str))

    return season, generate_output(season)  # TODO: FIGURE THIS OUT. FUCK THE COUGH.
