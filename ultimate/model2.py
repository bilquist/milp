
import itertools
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model

from ultimate.classes import Pod, Team


def main(pods, teams=None, num_top=12, num_bot=12, max_play_with=1, max_play_against=2):

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

    # Model
    model = cp_model.CpModel()

    # Variables
    # x[i, j] is an array of 0-1 variables, which will be 1 if player i is assigned to team j
    x = {}
    for ii in iter_pods:
        for jj in iter_teams:
            x[ii, jj] = model.NewIntVar(0, 1, f'x[{ii}, {jj}]')

    # Constraints
    # Each team is composed of three pods
    for jj in iter_teams:
        model.Add(sum([x[ii, jj] for ii in iter_pods]) == 3)

    # Each pod can only be assigned once
    for ii in iter_pods:
        model.Add(sum([x[ii, jj] for jj in iter_teams]) == 1)

    # Top pods cannot play bottom pods
    for ii in range(num_top):
        for jj in range(num_pods - num_bot, num_pods):
            for kk in range(num_teams):
                # print(f'Adding constraint: x[{ii}, {kk}], x[{jj}, {kk}]')
                # Same team constraint
                model.Add(sum([x[ii, kk], x[jj, kk]]) <= 1)
                # Opponent constraint (only add when on an even team iteration)
                if kk % 2 == 0:
                    # print(f'Adding constraint: x[{ii}, {kk}, x[{jj}, {kk + 1}]')
                    model.Add(sum([x[ii, kk], x[jj, kk + 1]]) <= 1)
                    # print(f'Adding constraint: x[{ii}, {kk + 1}], x[{jj}, {kk}]')
                    model.Add(sum([x[ii, kk + 1], x[jj, kk]]) <= 1)

    # Pods cannot play with someone more than max_play_with
    for ii in iter_pods:
        # print(f'Pod: {pod}')
        # print(f'Played with: {[key.rank for key in pod.played_with}]')
        for teammate in pods[ii].played_with:
            # Add the constraint
            if ii == 0:
                print(f'Pod: {pods[ii].rank}::: With: {teammate.rank}')
            for kk in range(num_teams):
                limit = 2 if max_play_with - pods[ii].played_with[teammate]['count'] > 0 else 1
                if limit == 0:
                    raise ValueError(
                        f"LIMIT IS 0:\npod: {pods[ii]}\nConstraint:"
                        f'WITH: x[{ii}, {kk}], x[{teammate.rank - 1, kk}]'
                    )
                # print(f'WITH: x[{ii}, {kk}], x[{teammate.rank - 1, kk}]')
                model.Add(sum([x[ii, kk], x[teammate.rank - 1, kk]]) <= limit)

    # Pods cannot play against someone more than max_play_against
    for ii in range(len(pods)):
        # print(f'POD: {pod}')
        # print(f'Played against: {[key.rank for key in pod.played_against}]')
        for opponent in pods[ii].played_against:
            # Add the constraint
            if ii == 0:
                print(f'Pod: {pods[ii].rank}::: Against: {opponent.rank}')
            for kk in range(num_teams):
                limit = 2 if max_play_against - pods[ii].played_against[opponent]['count'] > 0 else 1
                # print(f'AGAINST: x[{ii}, {kk}], x[{opponent.rank - 1}, {kk}] <= {limit}]')
                # model.Add(sum([x[ii, kk], x[opponent.rank - 1, kk]]) <= limit)  # old condition... oops!
                if kk % 2 == 0:
                    model.Add(sum([x[ii, kk], x[opponent.rank - 1, kk + 1]]) <= limit)
                    model.Add(sum([x[ii, kk + 1], x[opponent.rank - 1, kk]]) <= limit)

    # If teams is included, constrain the pods presented to be forced to play with one-another
    if teams:
        if len(teams) != num_teams:
            raise ValueError("Input teams does not match the number of teams extracted from the pod count.")
        for tt in iter_teams:
            if tt % 2 == 0:
                # Collect home vs. away from input teams
                team1 = teams[tt]
                team2 = teams[tt + 1]
                # Construct the constraints forcing the values to be equal among them
                for kk in iter_teams:
                    # if tt == 0:
                    #     print('constraints:')
                    for comb in itertools.combinations(team1.pods, 2):
                        # if tt == 0:
                        #     print(f'x[{comb[0].rank - 1}, {kk}] == x[{comb[1].rank - 1}, {kk}]')
                        model.Add(x[comb[0].rank - 1, kk] == x[comb[1].rank - 1, kk])
                    for comb in itertools.combinations(team2.pods, 2):
                        # if tt == 0:
                        #     print(f'x[{comb[0].rank - 1}, {kk}] == x[{comb[1].rank - 1}, {kk}]')
                        model.Add(x[comb[0].rank - 1, kk] == x[comb[1].rank - 1, kk])
                    if kk % 2 == 0:
                        # if tt == 0:
                        #     print(f'[x[{team1.pods[0].rank - 1}, {kk}], x[{team2.pods[0].rank - 1}, {kk + 1}]] <= 1')
                        #     print(f'[x[{team1.pods[0].rank - 1}, {kk + 1}], x[{team2.pods[0].rank - 1}, {kk}]] <= 1')
                        model.Add(sum([
                            x[team1.pods[0].rank - 1, kk],
                            x[team2.pods[0].rank - 1, kk + 1]
                        ]) <= 1)
                        model.Add(sum([
                            x[team1.pods[0].rank - 1, kk + 1],
                            x[team2.pods[0].rank - 1, kk]
                        ]) <= 1)
            #
            #
            #             comb[0].play_with(comb[1])
            #             comb[1].play_with(comb[0])
            #
            #
            #
            # team1_pods = [x[pod.rank - 1, kk] for pod in team1.pods]
            # print('team1_pods:')
            # print(team1_pods)
            # # Keep the same pods
            # model.Add(sum(team1_pods) == len(team1.pods))
            # if kk % 2 == 0:
            #     team2 = teams[kk + 1]
            #     # Construct the team pod constraints
            #
            #     team2_pods = [x[pod.rank - 1, kk + 1] for pod in team2.pods]
            #     # Keep the same pods
            #
            #     print('team2_pods:')
            #     print(team2_pods)
            #
            #     model.Add(sum(team2_pods) == len(team2.pods))
            #     # Prevent the teams from playing for a second time that day
            #     print('prevent:')
            #     print([team1_pods[0], team2_pods[0]])
            #     # model.Add(sum([team1_pods[0], team2_pods[0]]) <= 1)
            #     # all_pods = team1_pods + team2_pods
            #     # model.Add(all_pods == len(team1.pods))

    # Objective
    homes = []
    aways = []
    for jj in iter_teams:
        if jj % 2 == 0:
            homes.append(sum([pods[ii].rank * x[ii, jj] for ii in iter_pods]))
        else:
            aways.append(sum([pods[ii].rank * x[ii, jj] for ii in iter_pods]))

    # Pairwise sum of abs differences: need to minimize in obj fn
    # x_loss_abs = [model.NewIntVar(0, 1000000, 'x_loss_abs_%i' % i) for i in range(len(homes))]

    x_loss_abs = []
    for ih in range(len(homes)):
        # v = model.NewIntVar(-1000000, 1000000, 'v')  # Temporary variable
        # model.Add(v == (homes[ih] - aways[ih])
        # model.AddAbsEquality(x_loss_abs[ih], v)
        # Different attempt:
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
        for jj in iter_teams:
            for ii in iter_pods:
                # Test if x[ii, jj] is 1 (with tolerance for floating point arithmetic).
                # if x[ii, jj].solution_value() > 0.5:
                if solver.BooleanValue(x[ii, jj]):
                    if jj in pod_teams:
                        pod_teams[jj].append(pods[ii])
                    else:
                        pod_teams[jj] = [pods[ii]]
        teams = []
        for tt in iter_teams:
            msg = f'Team{tt}: {sum([pod.rank for pod in pod_teams[tt]])} Pods: {[pod.rank for pod in pod_teams[tt]]}'
            team = Team(pods=pod_teams[tt])
            teams.append(team)
            if tt % 2 != 0:
                team1_cost = sum([pod.rank for pod in pod_teams[tt - 1]])
                team2_cost = sum([pod.rank for pod in pod_teams[tt]])
                delta = abs(team1_cost - team2_cost)
                msg += f':  Cost: {delta} => ({team1_cost} - {team2_cost})'
            print(msg)
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
