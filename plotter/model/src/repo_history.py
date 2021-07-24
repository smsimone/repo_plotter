import datetime
import json
import os

from .commit import Commit


class RepoHistory(object):
    """
        Contains all the history of the repository
    """

    def __init__(self,  commits=[]):
        self.commits = commits
        self.initialDate = None
        self.finalDate = None
        self.preprocessed = False

    def __set_initial_date__(self, date: datetime):
        self.initialDate = date

    def __set_final_date__(self, date: datetime):
        self.finalDate = date

    def add_commit(self, commit: Commit):
        self.commits.append(commit)

    def as_map(self):
        return {
            'initialDate': self.initialDate,
            'finalDate': self.finalDate,
            'preprocessed': self.preprocessed,
            'commits': [commit.as_map() for commit in self.commits],
        }

    def preprocess_commits(self):
        """
            Prepares the repo history to be plotted

            It will:
                - squash the commits done on same days on a single fake commit that sums all the stats
                - calculates the initial and final dates
        """
        if self.preprocessed:
            print("Data was already been preprocessed")
            return
        self.preprocessed = True


def parse_repo_history(input_file: str) -> RepoHistory:

    if not os.path.exists(input_file):
        print(f"File {input_file} doesn't exists")
        exit(-1)

    with open(input_file, 'r') as f:
        data = json.loads(f.read())

    repo_history = RepoHistory()
    repo_history.__set_initial_date__(data['initialDate'])
    repo_history.__set_final_date__(data['finalDate'])
    return repo_history
