
import datetime
import os
import subprocess
import typing

from plotter.model.src.aggregated import AggregatedData
from plotter.model.src.filedata import FileData
from plotter.utilities import get_cloc_data_from_commit


class Commit(object):

    """
        Class that contains the info regarding a single commit

        It contains the `hash` of the commit, its date and its `cloc` data
    """

    def __init__(self, data: str):
        commit, date, time = data.replace('"', '').split(" ")
        self.commitHash = commit
        self.squashed_hashes = []
        year, month, day = date.split("-")
        hour, minute, second = time.strip().split(":")
        self.date = datetime.datetime(
            year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute), second=int(second))

    def add_squashed_hash(self, hash: str):
        self.squashed_hashes.append(hash)

    def __set_commit_hash__(self, hash: str):
        self.commitHash = hash

    def get_languages(self) -> typing.List[str]:
        """
            Returns all the languages contained in this commit
        """
        return [item.lang for item in self.langData]

    def __set_date__(self, date: datetime):
        self.date = date

    def __set_file_data__(self, data: typing.List[FileData]):
        self.langData = data

    def __set_aggregated_data__(self, data: AggregatedData):
        self.aggregated = data

    def __get_data_for_lang__(self, lang: str) -> FileData:
        """
            Gets the `FileData` object for the language `lang`

            If it doesn't exists, returns `None`
        """
        for data in self.langData:
            if data.lang == lang:
                return data
        else:
            return None

    def add_commit_data(self, other_commit):
        if not isinstance(other_commit, Commit):
            raise Exception("You can sum only two commits")
        self_languages = [data.lang for data in self.langData]
        other_languages = [data.lang for data in other_commit.langData]

        common_languages = set(self_languages).intersection(other_languages)
        missing_from_other_languages = set(
            other_languages).difference(self_languages)
        missing_from_self_languages = set(
            self_languages).difference(other_languages)

        new_lang_data = []
        for data in self.langData:
            # sums the languages fields that are in common between two commits
            if data.lang in common_languages:
                new_lang_data.append(data.add_other_data(
                    other_commit.__get_data_for_lang__(data.lang), inPlace=False))
            elif data.lang in missing_from_self_languages:
                new_lang_data.append(data)

        # adds the commits that are missing in the initial commit
        for data in other_commit.langData:
            if data.lang in missing_from_other_languages:
                new_lang_data.append(data)

        self.langData = new_lang_data
        self.aggregated.add(other_commit.aggregated)

    def checkout_and_get_data(self):
        """
            Moves into `directory` (which is the same of `--dir` flag), checkouts to `self.commit` and gets the data calculated by cloc

            Sets `self.langData` and `self.aggregated` to the values calculated
        """
        self.langData, self.aggregated = get_cloc_data_from_commit(
            self.commitHash)

    def to_string(self):
        return f"Commit {self.commitHash} done on {self.date}"

    def as_map(self) -> map:
        """
            Returns a map that represents this object
        """
        return {
            'hash': self.commitHash,
            'date': f"{self.date.year}-{self.date.month}-{self.date.day}",
            'time': f"{self.date.hour}:{self.date.minute}:{self.date.second}",
            'aggregated': self.aggregated.as_map(),
            'squashed_hashes': self.squashed_hashes,
            'fileData': [item.as_map() for item in self.langData]
        }


def parse_commit(data: map) -> Commit:
    commit = Commit(f"{data['hash']} {data['date']} {data['time']}")
    commit.__set_aggregated_data__(AggregatedData(data['aggregated']))
    fileData = [FileData(item) for item in data['fileData']]
    commit.__set_file_data__(fileData)
    return commit
