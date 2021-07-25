import datetime
import json
import os
import typing

import numpy as np
from plotter.model.src import filedata
from plotter.model.src.aggregated import AggregatedData
from plotter.model.src.filedata import FileData
from plotter.utilities import flatten_list

from .commit import Commit, parse_commit


class RepoHistory(object):
    """
        Contains all the history of the repository
    """

    def __init__(self,  commits=[]):
        self.commits = commits
        self.initialDate = None
        self.finalDate = None
        self.preprocessed = False
        self.languages = []

    def __set_preprocessed__(self, preprocessed: bool):
        self.preprocessed = preprocessed

    def __set_initial_date__(self, date: datetime):
        self.initialDate = date

    def __set_final_date__(self, date: datetime):
        self.finalDate = date

    def add_commit(self, commit: Commit):
        self.commits.append(commit)

    def __set_commits__(self, commits: typing.List[Commit]):
        self.commits = commits

    def as_map(self):
        if self.initialDate != None and self.finalDate != None:
            return {
                'initialDate':  f"{self.initialDate.year}-{self.initialDate.month}-{self.initialDate.day}",
                'finalDate': f"{self.finalDate.year}-{self.finalDate.month}-{self.finalDate.day}",
                'languages': self.languages,
                'preprocessed': self.preprocessed,
                'commits': [commit.as_map() for commit in self.commits],
            }
        else:
            return {
                'initialDate': self.initialDate,
                'finalDate': self.finalDate,
                'preprocessed': self.preprocessed,
                'commits': [commit.as_map() for commit in self.commits],
            }

    def get_commit_dates(self) -> typing.List[datetime.datetime]:
        """
        Returns all the dates of the preprocessed commits
        """
        return [item.date for item in self.commits]

    def get_commit_data(self, languages=[], field='code') -> typing.List[typing.List[FileData]]:
        """
        returns a list of list of FileData

        First level has the same dimension of parameter `languages` and each index refers the the
        language in the same index in `languages`
        """
        to_return = [[] for _ in languages]
        for commit in self.commits:
            for data in commit.langData:
                if data.lang in languages:
                    index = languages.index(data.lang)
                    to_return[index].append(data.get_field(field))
        return to_return

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
                        commit.add_squashed_hash(commits[j].commitHash)
                        same_commits.append(j)
                new_commits.append(commit)
        print(
            f"Reduced from {starting_commits} to {len(new_commits)} total commits.\nThe plot will start in {self.initialDate} and will end on {self.finalDate}")
        self.commits = new_commits
        self.languages = flatten_list(
            [commit.get_languages() for commit in commits], asSet=True)
        print(f"Languages: {self.languages}")
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
    repo_history.__set_preprocessed__(data['preprocessed'])

    commits = data['commits']
    parsed_commits = [parse_commit(item) for item in commits]
    repo_history.__set_commits__(parsed_commits)

    return repo_history
