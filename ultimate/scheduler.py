
import json
import os

from ultimate.classes import Pod, Season
from ultimate.model import main as first_run


BASEPATH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not os.path.isdir(os.path.join(BASEPATH_DIR, 'data')):
    os.makedirs(os.path.join(BASEPATH_DIR, 'data'))

GAMES_PER_DAY = 2
GAMES_PER_WEEK = 1
SCHEDULE_WEEKS = 6
debug = True

pods = [Pod(name=ix, rank=ix) for ix in range(1, 49)]
season = Season(pods=pods)


for ix in range(0, SCHEDULE_WEEKS):
    for iy in range(0, GAMES_PER_WEEK):
        daily_schedules = []
        for iz in range(0, GAMES_PER_DAY):
            print(f'{ix}:{iy}:{iz}:::')
            if iz == 0:
                print('generating first schedule of day...')
                schedule = []
                teams = first_run(pods)
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
                schedule = season.generate_subsequent_schedule_of_day(schedule, debug=True)
                for event in schedule:
                    print(f'{event[0]} vs. {event[1]}')
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
