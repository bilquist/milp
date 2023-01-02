
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model

from ultimate.classes import Pod, Team


def main(pods, num_top=12, num_bot=12, max_play_with=1, max_play_against=2, games_per_day=1):

    # Declare pods
    # pods = [Pod(name=ix, rank=ix) for ix in range(1, 49)]
    # sorted_pods = sorted(self.pods, key=lambda x: x.rank, reverse=False)

    # Data
    # num_top = 12
    # num_bot = 12
    # max_play_with = 1
    # max_play_against = 2
    # TODO: padding for pod count not divisible by 3
    num_teams = int(len(pods) / 3)
    if len(pods) % 3 != 0:
        raise ValueError("Pods not divisible by 3.")
    num_pods = len(pods)

    iter_pods = range(num_pods)
    iter_teams = range(num_teams)
    iter_games = range(games_per_day)
    iter_team_games = range(num_teams * games_per_day)

    # Model
    model = cp_model.CpModel()

    # Variables
    # x[i, j] is an array of 0-1 variables, which will be 1 if player i is assigned to team j
    x = {}
    for kk in iter_games:
        for ii in iter_pods:
            for jj in iter_teams:
                x[ii, jj, kk] = model.NewIntVar(0, 1, f'x[{ii}, {jj}, {kk}]')

    # Constraints
    # Each team is composed of three pods
    for kk in iter_games:
        for jj in iter_teams:
            model.Add(sum([x[ii, jj, kk] for ii in iter_pods]) == 3)

    # Each pod can only be assigned once per game
    for kk in iter_games:
        for ii in iter_pods:
            model.Add(sum([x[ii, jj, kk] for jj in iter_teams]) == 1)

    # Top pods cannot play bottom pods
    for kk in iter_games:
        for ii in range(num_top):
            for jj in range(num_pods - num_bot, num_pods):
                for tt in range(num_teams):
                    # print(f'Adding constraint: x[{ii}, {kk}], x[{jj}, {kk}]')
                    # Same team constraint
                    model.Add(sum([x[ii, tt, kk], x[jj, tt, kk]]) <= 1)
                    # Opponent constraint (only add when on an even team iteration)
                    if tt % 2 == 0:
                        # print(f'Adding constraint: x[{ii}, {kk}, x[{jj}, {kk + 1}]')
                        model.Add(sum([x[ii, tt, kk], x[jj, tt + 1, kk]]) <= 1)
                        # print(f'Adding constraint: x[{ii}, {kk + 1}], x[{jj}, {kk}]')
                        model.Add(sum([x[ii, tt + 1, kk], x[jj, tt, kk]]) <= 1)

    # Pods cannot play with someone more than max_play_with
    for kk in iter_games:
        for ii in iter_pods:
            # print(f'Pod: {pod}')
            # print(f'Played with: {[key.rank for key in pod.played_with}]')
            for teammate in pods[ii].played_with:
                # Add the constraint
                if ii == 0:
                    print(f'Pod: {pods[ii].rank}::: With: {teammate.rank}')
                for tt in range(num_teams):
                    limit = 2 if max_play_with - pods[ii].played_with[teammate]['count'] > 0 else 1
                    if limit == 0:
                        raise ValueError(
                            f"LIMIT IS 0:\npod: {pods[ii]}\nConstraint:"
                            f'WITH: x[{ii}, {tt}, {kk}], x[{teammate.rank - 1}, {tt}, {kk}]'
                        )
                    # print(f'WITH: x[{ii}, {kk}], x[{teammate.rank - 1, kk}]')
                    model.Add(sum([x[ii, tt, kk], x[teammate.rank - 1, tt, kk]]) <= limit)

    # Pods cannot play against someone more than max_play_against
    for kk in iter_games:
        for ii in range(len(pods)):
            # print(f'POD: {pod}')
            # print(f'Played against: {[key.rank for key in pod.played_against}]')
            for opponent in pods[ii].played_against:
                # Add the constraint
                if ii == 0:
                    print(f'Pod: {pods[ii].rank}::: Against: {opponent.rank}')
                for tt in range(num_teams):
                    limit = 2 if max_play_against - pods[ii].played_against[opponent]['count'] > 0 else 1
                    # print(f'AGAINST: x[{ii}, {kk}], x[{opponent.rank - 1}, {kk}] <= {limit}]')
                    # model.Add(sum([x[ii, kk], x[opponent.rank - 1, kk]]) <= limit)  # old condition... oops!
                    if tt % 2 == 0:
                        model.Add(sum([x[ii, tt, kk], x[opponent.rank - 1, tt + 1, kk]]) <= limit)
                        model.Add(sum([x[ii, tt + 1, kk], x[opponent.rank - 1, tt, kk]]) <= limit)

    # # Teams must remain the same from game to game on the same day
    # for k1 in range(games_per_day - 1):
    #     for k2 in range(k1 + 1, games_per_day):
    #         print(f'k1: {k1} => k2: {k2}')
    #         for j1 in iter_teams:
    #             game_sum = 0
    #             jjs = []
    #             for j2 in iter_teams:
    #                 # model.AddMultiplicatoinEquality()
    #                 # model.AddMultiplicationEquality(3 == x[:, j1, k1] * x[:, j2, k2])
    #                 print(f'[ii, {j1}, {k1}] * [ii, {j2}, {k2}] for all i in I == 3')
    #                 # model.Add(sum([x[ii, j1, k1] * x[ii, j2, k2] for ii in iter_pods]) == 3)
    #                 # game_sum += sum([x[ii, j1, k1] * x[ii, j2, k2] for ii in iter_pods])
    #                 iis = []
    #                 for ii in iter_pods:
    #                     param_name = f'[{ii}, {j1}, {k1}] * [{ii}, {j2}, {k2}]'
    #                     i_var = model.NewIntVar(x[ii, j1, k1] * x[ii, j2, k2], name=param_name)
    #                     iis.append(i_var)
    #                 jjs.append(iis)
    #             model.Add(sum([iis for iis in jjs]) == 3)

    # # Objective
    # homes = []
    # aways = []
    # for kk in iter_games:
    #     kk_homes = []
    #     kk_aways = []
    #     for jj in iter_teams:
    #         if jj % 2 == 0:
    #             kk_homes.append(sum([pods[ii].rank * x[ii, jj, kk] for ii in iter_pods]))
    #         else:
    #             kk_aways.append(sum([pods[ii].rank * x[ii, jj, kk] for ii in iter_pods]))
    #     homes.append(kk_homes)
    #     aways.append(kk_aways)


    # Multi-game Objective
    if num_teams % games_per_day != 0:
        raise ValueError("Teams cannot be divided into equal games-per-day groups.")
    # opt_teams = [[] for ix in range(1 + games_per_day)]
    matches = []
    match_teams = []
    matches_labels = []
    played_cache = set()
    for kk in range(games_per_day):
        matches.append([[], []])
        matches_labels.append([[], []])
        match_teams.append([])
        pool = set([ii for ii in iter_teams])
        team1 = None
        while len(pool) > 0:
            if team1 is None:
                team1 = pool.pop()
            else:
                team2 = pool.pop()
                match_up = (team1, team2) if team1 < team2 else (team2, team1)  # Attempt a consistent ordering
                if match_up in played_cache or match_up in played_cache:
                    pool.add(team2)
                else:
                    matches[kk][0].append(sum([pods[ii].rank * x[ii, team1, kk] for ii in iter_pods]))
                    matches[kk][1].append(sum([pods[ii].rank * x[ii, team2, kk] for ii in iter_pods]))
                    matches_labels[kk][0].append(team1)
                    matches_labels[kk][1].append(team2)
                    played_cache.add(match_up)
                    team1 = None
                    match_teams[kk].append(match_up)
        print(f'Matches [{kk}]:')
        print(match_teams[kk])

    # Pairwise sum of abs differences: need to minimize in obj fn
    # x_loss_abs = [model.NewIntVar(0, 1000000, 'x_loss_abs_%i' % i) for i in range(len(homes))]

    # x_loss_abs = []
    # for ik in range(len(homes)):
    #     for ih in range(len(homes[ik])):
    #         # v = model.NewIntVar(-1000000, 1000000, 'v')  # Temporary variable
    #         # model.Add(v == (homes[ih] - aways[ih])
    #         # model.AddAbsEquality(x_loss_abs[ih], v)
    #         # Different attempt:
    #         v1 = model.NewIntVar(0, 1000, 'v1_%i' % ih)
    #         model.Add(homes[ik][ih] - aways[ik][ih] <= v1)
    #         model.Add(aways[ik][ih] - homes[ik][ih] <= v1)
    #         x_loss_abs.append(v1)
    x_loss_abs = []
    for im in range(len(matches)):
        homes = matches[im][0]
        aways = matches[im][1]
        homes_label = matches_labels[im][0]
        aways_label = matches_labels[im][1]
        for ih in range(len(homes)):
            print('*********************************************************************')
            print(f'Adding Objective Match: [{homes_label[ih]} - {aways_label[ih]} <= v1]')
            print(f'Adding Objective Match: [{aways_label[ih]} - {homes_label[ih]} <= v1]')
            print('*********************************************************************')
            v1 = model.NewIntVar(0, 1000, 'v1_%i' % ih)
            model.Add(homes[ih] - aways[ih] <= v1)
            model.Add(aways[ih] - homes[ih] <= v1)
            x_loss_abs.append(v1)

    # print('***matchups***')
    model.Minimize(sum(x_loss_abs))

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60 * 30
    solver.parameters.num_search_workers = 24
    status = solver.Solve(model)

    # Print solution
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Total cost = {solver.ObjectiveValue()}\n')
        pod_teams = {}
        for kk in iter_games:
            pod_teams[kk] = {}
            for jj in iter_teams:
                for ii in iter_pods:
                    # Test if x[ii, jj] is 1 (with tolerance for floating point arithmetic).
                    # if x[ii, jj].solution_value() > 0.5:
                    if solver.BooleanValue(x[ii, jj, kk]):
                        if jj in pod_teams[kk]:
                            pod_teams[kk][jj].append(pods[ii])
                        else:
                            pod_teams[kk][jj] = [pods[ii]]
        teams = []
        for kk in iter_games:
            kk_teams = []
            for tt in iter_teams:
                msg = (
                    f'Team{tt}: {sum([pod.rank for pod in pod_teams[kk][tt]])} '
                    f'Pods: {[pod.rank for pod in pod_teams[kk][tt]]} Game: {kk}'
                )
                team = Team(pods=pod_teams[kk][tt])
                kk_teams.append(team)
                if tt % 2 != 0:
                    team1_cost = sum([pod.rank for pod in pod_teams[kk][tt - 1]])
                    team2_cost = sum([pod.rank for pod in pod_teams[kk][tt]])
                    delta = abs(team1_cost - team2_cost)
                    msg += f':  Cost: {delta} => ({team1_cost} - {team2_cost})'
                print(msg)
            teams.append(kk_teams)
        return teams

    elif status == cp_model.INFEASIBLE:
        print('INFEASIBLE SOLUTION')
        return None

    else:
        print('NO SOLUTION')
        print(dir(cp_model))
        print(status)
        return None


if __name__ == '__main__':
    pods = [Pod(name=ix, rank=ix) for ix in range(1, 49)]
    # pods[0].play_with(pods[4])
    # pods[0].play_with(pods[11])
    main(pods)
