
from typing import List

from ultimate.models.pod import Pod
from ultimate.models.team import Team


class TeamPods:

    def __init__(self, team: Team, pods: set[Pod]):
        self.team = team
        self.pods = pods

    def __eq__(self, other: 'TeamPods') -> bool:
        """Compares itself to another TeamPods object to determine if they are equivalent"""
        return self.team == other.team and len(self.pods.symmetric_difference(other.pods)) == 0
