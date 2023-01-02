
import itertools
import json
from typing import Tuple


def generate_output(season):

    pod_map = {}
    team_map = {}

    SCHEDULE = []
    POD = []
    POD_PLAYED_WITH = []
    POD_PLAYED_AGAINST = []
    TEAM = []
    TEAM_PODS = []
    GAME = []

    schedule_pk = 1
    pod_pk = 1
    team_pk = 1
    team_pods_pk = 1
    game_pk = 1
    pod_played_with_pk = 1
    pod_played_against_pk = 1

    for week in season.schedule.keys():
        for intraweek in season.schedule[week].keys():
            for intraday in season.schedule[week][intraweek].keys():
                matches = season.schedule[week][intraweek][intraday]
                for match in matches:
                    map_team1_to_pods = False
                    map_team2_to_pods = False

                    # TEAMs
                    # Assign the team1 a pk value
                    if match['team1'] in team_map:
                        # Team already exists so use the same pk as previously granted
                        team1_id = team_map[match['team1']]
                    else:
                        team1_id = team_pk
                        team_map[match['team1']] = team_pk
                        team_pk += 1
                        map_team1_to_pods = True
                    TEAM.append({
                        "model": "core.Team",
                        "pk": team1_id,
                        "fields": {
                            "score": match['team1'].score,
                            "string_agg": str(match['team1'])
                        }
                    })
                    # Assign the team2 a pk value
                    if match['team2'] in team_map:
                        # Team already exists so use the same pk as previously granted
                        team2_id = team_map[match['team2']]
                    else:
                        team2_id = team_pk
                        team_map[match['team2']] = team_pk
                        team_pk += 1
                        map_team2_to_pods = True
                    TEAM.append({
                        "model": "core.Team",
                        "pk": team2_id,
                        "fields": {
                            "score": match['team2'].score,
                            "string_agg": str(match['team2'])
                        }
                    })

                    # GAME
                    # Assign the team1 and team2 to a game (team1 is home by default)
                    game_id = game_pk
                    GAME.append({
                        "model": "core.Game",
                        "pk": game_pk,
                        "fields": {
                            "home_team": team1_id,
                            "away_team": team2_id
                        }
                    })
                    game_pk += 1

                    # SCHEDULE
                    # Assign the game to a schedule
                    SCHEDULE.append({
                        "model": "core.Schedule",
                        "pk": schedule_pk,
                        "fields": {
                            "week": week,
                            "game_of_week": intraweek,
                            "game_of_day": intraday,
                            "game": game_id
                        }
                    })

                    # PODs
                    # Assign pods to model if not already exist (team1)
                    team1_pod_ids = []
                    for pod in match['team1'].pods:
                        if pod in pod_map:
                            pod_id = pod_map[pod]
                        else:
                            pod_id = pod_pk
                            pod_map[pod] = pod_pk
                            pod_pk += 1
                            POD.append({
                                "model": "core.Pod",
                                "pk": pod_id,
                                "fields": {
                                    "name": pod.name,
                                    "score": pod.rank
                                }
                            })
                        team1_pod_ids.append(pod_id)
                    # Assign pods to model if not already exist (team2)
                    team2_pod_ids = []
                    for pod in match['team2'].pods:
                        if pod in pod_map:
                            pod_id = pod_map[pod]
                        else:
                            pod_id = pod_pk
                            pod_map[pod] = pod_pk
                            pod_pk += 1
                            POD.append({
                                "model": "core.Pod",
                                "pk": pod_id,
                                "fields": {
                                    "name": pod.name,
                                    "score": pod.rank
                                }
                            })
                        team2_pod_ids.append(pod_id)

                    # TEAMPODs
                    if map_team1_to_pods:
                        for id_ in team1_pod_ids:
                            TEAM_PODS.append({
                                "model": "core.TeamPod",
                                "pk": team_pods_pk,
                                "fields": {
                                    "team": team1_id,
                                    "pod": id_
                                }
                            })
                            team_pods_pk += 1
                    if map_team2_to_pods:
                        for id_ in team2_pod_ids:
                            TEAM_PODS.append({
                                "model": "core.TeamPod",
                                "pk": team_pods_pk,
                                "fields": {
                                    "team": team2_id,
                                    "pod": id_
                                }
                            })
                            team_pods_pk += 1

                    # PODPLAYEDAGAINST
                    for pod1 in team1_pod_ids:
                        for pod2 in team2_pod_ids:
                            POD_PLAYED_AGAINST.append({
                                "model": "core.PodPlayedAgainst",
                                "pk": pod_played_against_pk,
                                "fields": {
                                    "game": game_id,
                                    "pod": pod1,
                                    "opponent": pod2
                                }
                            })
                            pod_played_against_pk += 1
                            POD_PLAYED_AGAINST.append({
                                "model": "core.PodPlayedAgainst",
                                "pk": pod_played_against_pk,
                                "fields": {
                                    "game": game_id,
                                    "pod": pod2,
                                    "opponent": pod1
                                }
                            })
                            pod_played_against_pk += 1

                    # PODPLAYEDWITH
                    # Team1
                    for pod_couple in itertools.combinations(team1_pod_ids, 2):
                        pod1 = pod_couple[0]
                        pod2 = pod_couple[1]
                        POD_PLAYED_WITH.append({
                            "model": "core.PodPlayedWith",
                            "pk": pod_played_with_pk,
                            "fields": {
                                "game": game_id,
                                "pod": pod1,
                                "teammate": pod2
                            }
                        })
                        pod_played_with_pk += 1
                        POD_PLAYED_WITH.append({
                            "model": "core.PodPlayedWith",
                            "pk": pod_played_with_pk,
                            "fields": {
                                "game": game_id,
                                "pod": pod2,
                                "teammate": pod1
                            }
                        })
                        pod_played_with_pk += 1
                    # Team2
                    for pod_couple in itertools.combinations(team2_pod_ids, 2):
                        pod1 = pod_couple[0]
                        pod2 = pod_couple[1]
                        POD_PLAYED_WITH.append({
                            "model": "core.PodPlayedWith",
                            "pk": pod_played_with_pk,
                            "fields": {
                                "game": game_id,
                                "pod": pod1,
                                "teammate": pod2
                            }
                        })
                        pod_played_with_pk += 1
                        POD_PLAYED_WITH.append({
                            "model": "core.PodPlayedWith",
                            "pk": pod_played_with_pk,
                            "fields": {
                                "game": game_id,
                                "pod": pod2,
                                "teammate": pod1
                            }
                        })
                        pod_played_with_pk += 1

    return SCHEDULE, POD, POD_PLAYED_WITH, POD_PLAYED_AGAINST, TEAM, TEAM_PODS, GAME


def tabulize(season) -> Tuple:
    """Tabulizes the season into multiple json files, structured to be ingested by a rdbms system"""

    pod_map = {}
    team_map = {}
    team_pods_map = {}  # Shouldn't be necessary. This is a just-in-case.

    _pods = []
    _teams = []
    _team_pods = []
    _games = []
    _schedule = []
    _pod_played_with = []
    _pod_played_against = []

    for week in season.schedule.keys():
        for intraweek in season.schedule[week].keys():
            for intraday in season.schedule[week][intraweek].keys():
                matches = season.schedule[week][intraweek][intraday]
                for match in matches:
                    map_team_to_pods = False

                    # Teams
                    # Assign the team1 a pk value
                    team1 = match['team1']
                    team2 = match['team2']
                    delta = match['delta']
                    team1_rank = match['team1_rank']
                    team2_rank = match['team2_rank']

                    # Generate the team objects
                    home_team = None
                    away_team = None
                    for ix, team in enumerate([team1, team2]):
                        if team in team_map:
                            team_id = team_map[team]
                        else:
                            team_id = len(team_map) + 1
                            team_map[team] = team_id
                            _teams.append({
                                'id': team_id,
                                'score': team.score,
                                'string_agg': str(team)
                            })
                            map_team_to_pods = True

                        # Generate the pod and team_pods objects
                        if map_team_to_pods:
                            # Generate the pod objects
                            for pod in team.pods:
                                if pod in pod_map:
                                    pod_id = pod_map[pod]
                                else:
                                    pod_id = len(pod_map) + 1
                                    pod_map[pod] = pod_id
                                    _pods.append({
                                        'id': pod_id,
                                        'name': pod.name,
                                        'score': pod.rank,
                                        # played_with
                                        # played_against
                                    })

                                # Generate the team_pods objects
                                if (team, pod) in team_pods_map:
                                    team_pods_id = team_pods_map[(team, pod)]
                                else:
                                    team_pods_id = len(team_pods_map) + 1
                                    _team_pods.append({
                                        'id': team_pods_id,
                                        'team': team_id,
                                        'pod': pod_id
                                    })

                        # Assign home/away teams
                        if ix == 0:
                            home_team = team
                        else:
                            away_team = team

                    # Generate the game objects
                    game_id = len(_games) + 1
                    _games.append({
                        'id': game_id,
                        'home_team': team_map[home_team],
                        'away_team': team_map[away_team]
                    })

                    # Generate the schedule objects
                    schedule_id = len(_schedule) + 1
                    _schedule.append({
                        'id': schedule_id,
                        'week': week,
                        'game_of_week': intraweek,
                        'game_of_day': intraday,
                        'game': game_id
                    })

                    # Generate the 'Played Against' objects
                    for pod1 in home_team.pods:
                        for pod2 in away_team.pods:
                            pod_played_against_id = len(_pod_played_against) + 1
                            # Home -> Away
                            _pod_played_against.append({
                                'id': pod_played_against_id,
                                'game': game_id,
                                'pod': pod_map[pod1],
                                'opponent': pod_map[pod2]
                            })
                            # Away -> Home
                            _pod_played_against.append({
                                'id': pod_played_against_id + 1,
                                'game': game_id,
                                'pod': pod_map[pod2],
                                'opponent': pod_map[pod1]
                            })

                    # Generate the 'Played With' objects
                    for team in [home_team, away_team]:
                        for duo in itertools.combinations(team.pods, 2):
                            pod1 = duo[0]
                            pod2 = duo[1]
                            pod_played_with_id = len(_pod_played_with) + 1
                            # Pod1 -> Pod2
                            _pod_played_with.append({
                                'id': pod_played_with_id,
                                'game': game_id,
                                'pod': pod_map[pod1],
                                'teammate': pod_map[pod2]
                            })
                            # Pod2 -> Pod1
                            _pod_played_with.append({
                                'id': pod_played_with_id + 1,
                                'game': game_id,
                                'pod': pod_map[pod2],
                                'teammate': pod_map[pod1]
                            })

    return _pods, _teams, _team_pods, _games, _schedule, _pod_played_with, _pod_played_against
