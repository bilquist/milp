
import json
import os

from ultimate.classes import Pod, Season
from ultimate.model import main as first_run
from ultimate.model2 import main as next_run


BASEPATH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not os.path.isdir(os.path.join(BASEPATH_DIR, 'data')):
    os.makedirs(os.path.join(BASEPATH_DIR, 'data'))

GAMES_PER_DAY = 2
GAMES_PER_WEEK = 1
SCHEDULE_WEEKS = 6
debug = True

pods = [Pod(name=ix, rank=ix) for ix in range(1, 49)]
season = Season(pods=pods)

NUM_TOP = 2
NUM_BOT = 2
MAX_PLAY_WITH = 2
MAX_PLAY_AGAINST = 2


for ix in range(0, SCHEDULE_WEEKS):
    for iy in range(0, GAMES_PER_WEEK):
        daily_schedules = []
        for iz in range(0, GAMES_PER_DAY):
            print(f'{ix}:{iy}:{iz}:::')
            schedule = []
            if iz == 0:
                print('generating first schedule of day...')
                teams = first_run(
                    pods,
                    num_top=NUM_TOP,
                    num_bot=NUM_BOT,
                    max_play_with=MAX_PLAY_WITH,
                    max_play_against=MAX_PLAY_AGAINST
                )
                print(f'****len(teams): {len(teams)}')
                for tt in range(len(teams)):
                    if tt % 2 == 0:
                        score1 = sum([p.rank for p in teams[tt].pods])
                        score2 = sum([p.rank for p in teams[tt + 1].pods])
                        schedule.append((teams[tt], teams[tt + 1], abs(score1 - score2), (score1, score2)))
                season.update_schedule(ix + 1, iy + 1, iz + 1, schedule)
                daily_schedules += schedule
                with open(os.path.join(BASEPATH_DIR, 'data', 'out.json'), 'w') as f:
                    f.writelines(json.dumps(season.schedule, indent=2, default=str))
            else:
                print('generating second schedule of day...')
                # schedule = season.generate_subsequent_schedule_of_day(schedule, debug=True)
                # for event in schedule:
                #     print(f'{event[0]} vs. {event[1]}')
                # Construct the teams from the first game
                static_teams = []
                # print('Daily Schedule:')
                # print(daily_schedules)
                for match in daily_schedules:
                    static_teams.append(match[0])
                    static_teams.append(match[1])
                # print('static teams!')
                # for team2 in static_teams:
                #     print([pod.rank for pod in team2.pods])
                # print('***********************')
                # Second model passed, constraining the teams to the same pod composition
                teams = next_run(
                    pods,
                    static_teams,
                    num_top=NUM_TOP,
                    num_bot=NUM_BOT,
                    max_play_with=MAX_PLAY_WITH,
                    max_play_against=MAX_PLAY_AGAINST
                )
                # Slow assertion (optimize later)
                for team1 in teams:
                    did_find = False
                    for team2 in static_teams:
                        if team1.has_same_pods(team2):
                            did_find = True
                    if not did_find:
                        print([pod.rank for pod in team1.pods])
                        print('-----------')
                        for team2 in static_teams:
                            print([pod.rank for pod in team2.pods])
                        raise ValueError("Team deviation!")

                for tt in range(len(teams)):
                    if tt % 2 == 0:
                        score1 = sum([p.rank for p in teams[tt].pods])
                        score2 = sum([p.rank for p in teams[tt + 1].pods])
                        schedule.append((teams[tt], teams[tt + 1], abs(score1 - score2), (score1, score2)))
                season.update_schedule(ix + 1, iy + 1, iz + 1, schedule)
                daily_schedules += schedule
                with open(os.path.join(BASEPATH_DIR, 'data', 'out.json'), 'w') as f:
                    f.writelines(json.dumps(season.schedule, indent=2, default=str))

            # Update the 'played with' for pods on the last game of the day
            if iz == (GAMES_PER_DAY - 1):
                for event in schedule:
                    event[0].update_pods_played_with()
                    event[1].update_pods_played_with()

with open(os.path.join(BASEPATH_DIR, 'data', 'out.json'), 'w') as f:
    f.writelines(json.dumps(season.schedule, indent=2, default=str))
