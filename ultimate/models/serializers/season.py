
from ultimate.models.season import Season


class SeasonSerializer:

    def __init__(self, season: Season):


    def serialize(self, data=None):
        if data is None:
            data = self.season

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
