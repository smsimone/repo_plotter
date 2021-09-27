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

    def __init__(self, commits=None):
        if commits is None:
            commits = []
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
                "initialDate":
                f"{self.initialDate.year}-{self.initialDate.month}-{self.initialDate.day}",
                "finalDate":
                f"{self.finalDate.year}-{self.finalDate.month}-{self.finalDate.day}",
                "languages": self.languages,
                "preprocessed": self.preprocessed,
                "commits": [commit.as_map() for commit in self.commits],
            }
        else:
            return {
                "initialDate": self.initialDate,
                "finalDate": self.finalDate,
                "preprocessed": self.preprocessed,
                "commits": [commit.as_map() for commit in self.commits],
            }

    def get_commit_dates(self) -> typing.List[datetime.datetime]:
        """
        if `self.preprocessed` is `True`
            Returns all the dates of the preprocessed commits
        else:
            Returns a list of integers
        """
        print("Getting preprocessed data:", self.preprocessed)
        if self.preprocessed:
            return [item.date for item in self.commits]
        else:
            return list(range(len(self.commits)))

    def get_commit_data(self,
                        languages=None,
                        field="code") -> typing.List[typing.List[FileData]]:
        """
        returns a list of list of FileData

        First level has the same dimension of parameter `languages` and each index refers the the
        language in the same index in `languages`
        """
        if languages is None:
            languages = []
        to_return = [[] for _ in languages]
        for commit in self.commits:
            for data in commit.langData:
                if data.lang in languages:
                    index = languages.index(data.lang)
                    to_return[index].append(data.get_field(field))
        return to_return

    def preprocess_commits(self, not_preprocessing: bool):
        """
        Prepares the repo history to be plotted

        If not_preprocessing is `False` it will:
            - squash the commits done on same days on a single fake commit that sums all the stats

        In very case it will:
            - calculate the initial and final dates
            - get all languages used in the commits
        """
        commits = self.commits
        starting_commits = len(self.commits)
        commits.sort(key=lambda x: x.date)
        self.initialDate = commits[0].date
        self.finalDate = commits[-1].date
        if not not_preprocessing:
            new_commits = []

            grouped_commits = {}
            for commit in commits:
                date = commit.date.date()
                if date not in grouped_commits:
                    grouped_commits[date] = []
                grouped_commits[date].append(commit)

            for date in grouped_commits:
                temp_commits = grouped_commits[date]
                temp_commits.sort(key=lambda x: x.date.date())
                new_commits.append(temp_commits[-1])

            print(
                f"Reduced from {starting_commits} to {len(new_commits)} total commits.\nThe plot will start in {self.initialDate} and will end on {self.finalDate}"
            )
            self.commits = new_commits
            self.preprocessed = True
        self.languages = flatten_list(
            [commit.get_languages() for commit in commits], asSet=True)


def parse_repo_history(input_file: str) -> RepoHistory:

    if not os.path.exists(input_file):
        print(f"File {input_file} doesn't exists")
        exit(-1)

    with open(input_file, "r") as f:
        data = json.loads(f.read())

    repo_history = RepoHistory()
    repo_history.__set_initial_date__(data["initialDate"])
    repo_history.__set_final_date__(data["finalDate"])
    repo_history.__set_preprocessed__(data["preprocessed"])

    commits = data["commits"]
    parsed_commits = [parse_commit(item) for item in commits]
    repo_history.__set_commits__(parsed_commits)

    return repo_history
