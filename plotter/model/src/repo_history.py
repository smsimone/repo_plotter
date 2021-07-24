import datetime
import json
import os
import typing

from .commit import Commit, parse_commit


class RepoHistory(object):
    """
        Contains all the history of the repository
    """

    def __init__(self,  commits=[]):
        self.commits = commits
        self.initialDate = None
        self.finalDate = None

    def __set_initial_date__(self, date: datetime):
        self.initialDate = date

    def __set_final_date__(self, date: datetime):
        self.finalDate = date

    def add_commit(self, commit: Commit):
        self.commits.append(commit)

    def __set_commits__(self, commits: typing.List[Commit]):
        self.commits = commits

    def as_map(self):
        return {
            'initialDate':  f"{self.initialDate.year}-{self.initialDate.month}-{self.initialDate.day}",
            'finalDate': f"{self.finalDate.year}-{self.finalDate.month}-{self.finalDate.day}",
            'commits': [commit.as_map() for commit in self.commits],
        }

    def preprocess_commits(self):
        """
            Prepares the repo history to be plotted

            It will:
                - squash the commits done on same days on a single fake commit that sums all the stats
                - calculates the initial and final dates
        """
        commits = self.commits
        starting_commits = len(self.commits)
        commits.sort(key=lambda x: x.date)
        self.initialDate = commits[0].date
        self.finalDate = commits[-1].date
        new_commits = []
        same_commits = []
        for i in range(len(commits)):
            if i not in same_commits:
                commit: Commit = commits[i]
                current_date = commit.date
                for j in range(i, len(commits)):
                    if commits[j].date != current_date:
                        break
                    else:
                        commit.add_commit_data(commits[j])
                        same_commits.append(j)
                new_commits.append(commit)
        print(
            f"Reduced from {starting_commits} to {len(new_commits)} total commits.\nThe plot will start in {self.initialDate} and will end on {self.finalDate}")
        self.commits = new_commits


def parse_repo_history(input_file: str) -> RepoHistory:

    if not os.path.exists(input_file):
        print(f"File {input_file} doesn't exists")
        exit(-1)

    with open(input_file, 'r') as f:
        data = json.loads(f.read())

    repo_history = RepoHistory()
    repo_history.__set_initial_date__(data['initialDate'])
    repo_history.__set_final_date__(data['finalDate'])

    commits = data['commits']
    parsed_commits = [parse_commit(item) for item in commits]
    repo_history.__set_commits__(parsed_commits)

    return repo_history
