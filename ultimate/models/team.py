
import itertools
from typing import Set

from ultimate.models.pod import Pod


class Team:

    def __init__(self, pods: Set[Pod]):
        self.pods: Set[Pod] = pods
        self.score: int = sum(pod.rank for pod in pods)

    def __str__(self) -> str:
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
        # mean_played_against = played_running_total / (len(self.pods) + len(opponent_team.pods))
        mean_played_against = played_running_total / len(self.pods)
        return mean_played_against

    def have_pods_played_together(self, opponent_team):
        """
        Returns a boolean stating whether any of the pods in this team have played any
        of the pods in the opponent team.
        """
        for p1 in self.pods:
            for p2 in opponent_team.pods:
                if (p2 in p1.played_with) or (p1 in p2.played_with):
                    return True
        return False

    def has_same_pods(self, team):
        """
        Returns a boolean stating whether the pods in this class are the same as
        the pods in the input team.
        """
        for p1 in self.pods:
            did_find = False
            for p2 in team.pods:
                if p1 == p2:
                    did_find = True
                    break
            if not did_find:
                return False
        return True
