
import datetime
import os
from plotter.model.src.aggregated import AggregatedData
import typing
from plotter.model.src.filedata import FileData
import subprocess

from plotter.utilities import get_cloc_data


class Commit(object):

    """
        Class that contains the info regarding a single commit

        It contains the `hash` of the commit, its date and its `cloc` data
    """

    def __init__(self, data: str):
        commit, date = data.replace('"', '').split(" ")
        self.commitHash = commit
        year, month, day = date.split("-")
        self.date = datetime.datetime(
            year=int(year), month=int(month), day=int(day))

    def __set_commit_hash__(self, hash: str):
        self.commitHash = hash

    def __set_date__(self, date: datetime):
        self.date = date

    def __set_file_data__(self, data: typing.List[FileData]):
        self.langData = data

    def __set_aggregated_data__(self, data: AggregatedData):
        self.aggregated = data

    def compare_to(self, other):
        """
            Compares `self` and `other` (if it's a `Commit`)

            returns:
                - -1 if `other` was done before
                - 0 if `self` and `other` have the same date
                - 1 if `self` was done before
        """
        if not isinstance(other, Commit):
            raise Exception(
                "Cannot compare to an object that isn't a `Commit`")

        if self.date == other.date:
            return 0
        elif self.date < other.date:
            return 1
        else:
            return -1

    def checkout_and_get_data(self, directory: str):
        """
            Moves into `directory` (which is the same of `--dir` flag), checkouts to `self.commit` and gets the data calculated by cloc

            Sets `self.langData` and `self.aggregated` to the values calculated
        """
        os.chdir(directory)
        subprocess.Popen(['git', 'checkout', '--quiet', self.commitHash],
                         stdout=subprocess.DEVNULL)
        self.langData, self.aggregated = get_cloc_data('.')
        os.chdir("..")

    def to_string(self):
        return f"Commit {self.commitHash} done on {self.date}"

    def as_map(self) -> map:
        """
            Returns a map that represents this object
        """
        return {
            'hash': self.commitHash,
            'date': f"{self.date.year}-{self.date.month}-{self.date.day}",
            'aggregated': self.aggregated.as_map(),
            'fileData': [item.as_map() for item in self.langData]
        }


def parse_commit(data: map) -> Commit:
    commit = Commit(f"{data['hash']} {data['date']}")
    commit.__set_aggregated_data__(data['aggregated'])
    fileData = [FileData(item) for item in data['fileData']]
    commit.__set_file_data__(fileData)
    return commit
