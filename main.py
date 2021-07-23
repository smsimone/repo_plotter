import json
import os
from absl import app
from absl import flags
import shutil
import typing
import subprocess
import datetime


FLAGS = flags.FLAGS

flags.DEFINE_string(
    'repository', None, 'The repository to execute this script on')
flags.DEFINE_string(
    'branch', None, 'Select a custom branch of the repository')
flags.DEFINE_bool('offline', False,
                  'Specify if it should use the current repository in .repo folder of it has to clone a new repository')


class FileData(object):
    """
        Class that contains the data for the single language calculated by `cloc`
    """

    def __init__(self, lang: str, data: map):
        self.lang = lang
        self.numFiles = data['nFiles']
        self.blank = data['blank']
        self.comment = data['comment']
        self.code = data['code']

    def to_string(self):
        return f"Language {self.lang} has {self.code} lines of code"


class AggregatedData(object):
    """
        Class that contains the aggregated data calculated by `cloc`
    """

    def __init__(self, data: map):
        self.blank = data['blank']
        self.comment = data['comment']
        self.code = data['code']
        self.nFiles = data['nFiles']

    def to_string(self):
        return f"Total lines of code: {self.code}"


class Commit(object):
    """
        Class that contains the info regarding a single commit

        It contains the `hash` of the commit, its date and the `cloc` data
    """

    def __init__(self, data: str):
        commit, date = data.replace('"', '').split(" ")
        self.commitHash = commit
        year, month, day = date.split("-")
        self.date = datetime.datetime(
            year=int(year), month=int(month), day=int(day))

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

    def to_string(self):
        return f"Commit {self.commitHash} done on {self.date}"


def command_exists(command_name: str) -> bool:
    """
    Checks if `command_name` is a command present in this env
    """
    from shutil import which
    return which(command_name) is not None


def get_commits(folder='.repo') -> typing.List[str]:
    """
        Gets all the commits done on the repository's branch `FLAGS.branch` contained in `folder`

        At each commit it runs the `cloc` utility to retrieve all data
    """
    os.chdir(".repo")
    command = r'git.--no-pager.log.--pretty=format:"%H %ad".--date=format:"%F"'
    p = subprocess.Popen(command.split("."),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.chdir("..")

    lines = p.stdout.readlines()
    commits = []
    for line in lines:
        commit = line.decode('utf-8').strip()
        commits.append(Commit(commit))
    return commits


def get_data(folder='.repo') -> typing.Tuple[typing.List[FileData], AggregatedData]:
    """
        Get the data of `folder` using the `cloc` utility

        Returns the list of languages contained in the repository
    """
    p = subprocess.Popen(['cloc', folder, '--json'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_lines = p.stdout.readlines()
    output = ""
    for line in output_lines:
        output += line.decode('utf-8')
    output = json.loads(output)
    languages = [lang for lang in output if lang != 'header']
    data = []
    aggregated = None
    for lang in languages:
        if lang == 'SUM':
            aggregated = AggregatedData(output[lang])
        else:
            data.append(FileData(lang, output[lang]))
    return (data, aggregated)


def main(args):
    repository = FLAGS.repository

    if repository is None:
        print("Missing `--repository` flag")
        print("Run `python3 main.py --help` to get a list of flags")
        exit(-1)

    if not FLAGS.offline:
        if os.path.exists('.repo') and os.path.isdir('.repo'):
            shutil.rmtree('.repo')

        os.mkdir('.repo')
        try:
            subprocess.call(['git', 'clone', repository, '.repo'])
        except:
            print("Failed to clone repository")
            exit(-2)

    if FLAGS.branch is not None:
        os.chdir(".repo")
        p = subprocess.Popen(['git', 'checkout', FLAGS.branch],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        error = list(p.stderr.readlines())
        if len(error) > 0:
            print("ERROR:", error[0].decode('utf-8').strip())
            print("Continuing anyway...")
        else:
            print(f"Changed branch to {FLAGS.branch}")
        os.chdir('..')

    commits = get_commits()

    languages, aggregated = get_data()
    print(f"There are {len(languages)} possible languages to pick:")
    count = 0
    for lang in languages:
        print(f"- {count}: {lang.lang.lower()}")
        count += 1
    print(f"- {count}: the sum of all them")

    retry = True
    while retry:
        retry = False
        languages_to_plot = input(
            "Which one you want to pick?\n(you can select how many languages you want, just comma-separated '1,2,3')\n").split(",")

        for item in languages_to_plot:
            if int(item) > count:
                print(f"item {item} is not valid")
                retry = True

    print(f"Should plot {languages_to_plot}")


if __name__ == '__main__':
    if not command_exists('git'):
        print("Missing `git`")
        exit(-1)

    if not command_exists('cloc'):
        print("Missing `cloc` utility")
        exit(-1)

    app.run(main)
