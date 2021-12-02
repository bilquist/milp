
from ortools.linear_solver import pywraplp

from ultimate.classes import Pod


def main():

    # Declare pods
    pods = [Pod(name=ix, rank=ix) for ix in range(1, 49)]
    # sorted_pods = sorted(self.pods, key=lambda x: x.rank, reverse=False)

    # Data
    num_top = 1
    num_bot = 1
    max_play_with = 1
    max_play_against = 2
    # TODO: padding for pod count not divisible by 3
    num_teams = 16

    # Solver
    # Create the mip solver with the SCIP backend
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Variables
    # x[i, j] is an array of 0-1 variables, which will be 1
    # if worker i is assigned to team j
    x = {}
    for jj in range(num_teams):
        for ii in range(len(pods)):
            x[ii, jj] = solver.IntVar(0, 1, '')

    # Constraints
    # Each team is composed of three pods
    for jj in range(num_teams):
        solver.Add(solver.Sum([x[ii, jj] for ii in range(len(pods))]) == 3)

    # Each pod can only be assigned once
    for ii in range(len(pods)):
            solver.Add(solver.Sum([x[ii, jj] for jj in range(num_teams)]) == 1)

    # Top pods cannot play with bottom pods
    for ii in range(num_top):
        for jj in range(len(pods) - num_bot, len(pods)):
            for kk in range(num_teams):
                # print(f'Adding constraint: x[{ii}, {kk}], x[{jj}, {kk}]')
                solver.Add(solver.Sum([x[ii, kk], x[jj, kk]]) <= 1)

    # Top pods cannot play against bottom pods
    for kk in range(num_teams):
        if kk % 2 == 0:
            # Even row so combine this row and the next
            for ii in range(num_top):
                for jj in range(len(pods) - num_bot, len(pods)):
                    solver.Add(solver.Sum([x[ii, kk]]))

    # Pods cannot play with someone more than max_play_with
    for ii in range(len(pods)):
        pod = pods[ii]
        for teammate in pod.played_with:
            # Get the opponents ordinal position
            teammate_ix = None
            for ix, pod_ in enumerate(pods):
                if teammate == pod_:
                    teammate_ix = ix
            if teammate_ix is None:
                raise ValueError(f"Could not find the teammate, {teammate}, in pods for pod, {pod}.")
            # Add the constraint
            for kk in range(num_teams):
                limit = max_play_with - pod.played_with[teammate]['count']
                solver.Add(solver.Sum([x[ii, kk], x[teammate_ix, kk]]) <= limit)

    # Pods cannot play against someone more than max_play_against
    for ii in range(len(pods)):
        pod = pods[ii]
        for opponent in pod.played_against:
            # Get the opponents ordinal position
            opponent_ix = None
            for ix, pod_ in enumerate(pods):
                if opponent == pod_:
                    opponent_ix = ix
            if opponent_ix is None:
                raise ValueError(f"Could not find the opponent, {opponent}, in pods for pod, {pod}.")

    # Objective
    homes = []
    aways = []
    for jj in range(num_teams):
        for ii in range(len(pods)):
            if jj % 2 == 0:
                homes.append(pods[ii].rank * x[ii, jj])
            else:
                aways.append(pods[ii].rank * x[ii, jj])
    sums = []
    # matchups = [homes[ih] - aways[ih] for ih in range(len(homes))]
    # for ix, match in enumerate(matchups):
    for ih in range(len(homes)):
        t = solver.IntVar(0, 10000, f'match_{ih}')
        solver.Add(homes[ih] - aways[ih] <= t)
        solver.Add(homes[ih] - aways[ih] >= -t)
        sums.append(t)

    # print('***matchups***')
    # print(matchups)
    # solver.Minimize(solver.Sum(matchups))
    solver.Minimize(solver.Sum(sums))

    # Solve
    status = solver.Solve()

    # Print solution
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f'Total cost = {solver.Objective().Value()}\n')
        for jj in range(num_teams):
            for ii in range(len(pods)):
                # Test if x[ii, jj] is 1 (with tolerance for floating point arithmetic).
                if x[ii, jj].solution_value() > 0.5:
                    print(f'Pod {ii} assigned to team {jj}. Cost = {pods[ii].rank}.')
    else:
        print('UUUUU')


if __name__ == '__main__':
    main()
