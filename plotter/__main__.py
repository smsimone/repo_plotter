import json
import os
import shutil
import subprocess
import typing

import progressbar
from absl import app, flags

from plotter.model.src.repo_history import RepoHistory, parse_repo_history
from plotter.plot import Plotter

from .model.src.commit import Commit
from .utilities import get_cloc_data

FLAGS = flags.FLAGS

flags.DEFINE_string(
    'repository', None, 'The repository to execute this script on')
flags.DEFINE_string(
    'input_file', None, "Specifies a custom json file to feed the script. It must has been generated during an old execution")
flags.DEFINE_string(
    'branch', None, 'Select a custom branch of the repository')
flags.DEFINE_bool('offline', False,
                  'Specify if it should use the current repository in the folder defined with `--dir` of it has to clone a new repository')
flags.DEFINE_bool('write_output', False,
                  'Specifies wether the script has to write the intermediate results to output')
flags.DEFINE_string('output_folder', None,
                    'Specifies the folder where the script has to write the output files')
flags.DEFINE_string(
    'dir', '.repo', 'Specifies the temporary directory to use to store the repository defined with the flag --repository')


def command_exists(command_name: str) -> bool:
    """
    Checks if `command_name` is a command present in this env
    """
    from shutil import which
    return which(command_name) is not None


def get_commits(folder: str) -> typing.List[str]:
    """
        Gets all the commits done on the repository's branch `FLAGS.branch` contained in `folder`

        At each commit it runs the `cloc` utility to retrieve all data
    """
    os.chdir(folder)
    command = r'git.--no-pager.log.--pretty=format:"%H %ad".--date=format:"%F"'
    p = subprocess.Popen(command.split("."),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    lines = p.stdout.readlines()
    commits = []
    for index in progressbar.progressbar(range(len(lines))):
        line = lines[index]
        commit = Commit(line.decode('utf-8').strip())
        commit.checkout_and_get_data()
        commits.append(commit)

    os.chdir("..")
    return commits


def generate_repo_history(temporary_dir: str) -> RepoHistory:
    """
        Generates a `RepoHistory` object if `FLAGS.input_file` is not specified
    """
    if not FLAGS.offline:
        repository = FLAGS.repository
        if repository is None:
            print("Missing `--repository` flag")
            print("Run `python3 main.py --help` to get a list of flags")
            exit(-1)
        if os.path.exists(temporary_dir) and os.path.isdir(temporary_dir):
            shutil.rmtree(temporary_dir)

        os.mkdir(temporary_dir)
        try:
            print("Cloning repository...")
            subprocess.call(['git', 'clone', repository,
                            temporary_dir, '--quiet'])
        except:
            print("Failed to clone repository")
            exit(-2)
    else:
        if not os.path.exists(temporary_dir):
            print("You can't use --offline flag on a non-existent --dir directory")
            exit(-1)

    if FLAGS.branch is not None:
        os.chdir(temporary_dir)
        p = subprocess.Popen(['git', 'checkout', FLAGS.branch],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        error = list(p.stderr.readlines())
        if len(error) > 0:
            print("ERROR:", error[0].decode('utf-8').strip())
            print("Continuing anyway...")
        else:
            print(f"Changed branch to {FLAGS.branch}")
        os.chdir('..')

    print("Getting commit data")
    commits = get_commits(temporary_dir)
    return RepoHistory(commits)


def plot_data(repo_history: RepoHistory):
    continue_plotting = True
    while continue_plotting:
        languages = repo_history.languages

        print(f"There are {len(languages)} possible languages to pick:")
        count = 0
        langs = {}
        for lang in languages:
            print(f"- {count}: {lang}")
            langs[count] = lang
            count += 1
        langs[count] = 'All'
        print(f"- {count}: the sum of all them")

        retry = True
        while retry:
            retry = False
            try:
                languages_to_plot = [int(index) for index in input(
                    "Which one you want to pick?\n(you can select how many languages you want, just comma-separated '1,2,3')\n").split(",")]
                for item in languages_to_plot:
                    if int(item) > count:
                        print(f"item {item} is not valid")
                        retry = True
            except:
                print(
                    f"The selection must be done with the indexes between 0 and {count}")
                retry = True

        print(f"Should plot {[langs[index] for index in  languages_to_plot]}")

        plotter = Plotter(repo_history)
        plotter.plot([langs[index] for index in languages_to_plot])
        should_plot = input("Plot again? Y/n: ")
        if should_plot.strip() == 'n':
            exit(1)


def main(args):
    temporary_dir = FLAGS.dir
    write_output = FLAGS.write_output
    output_folder = None

    if write_output:
        if FLAGS.output_folder is None:
            print(
                'If you specify --write_output you must specify the ouput folder with --output_folder flag')
            exit(-1)
        output_folder = FLAGS.output_folder
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

    if FLAGS.input_file is not None:
        repo_history = parse_repo_history(FLAGS.input_file)
    else:
        repo_history = generate_repo_history(temporary_dir)
        if write_output:
            with open(f'{output_folder}/repo_history.json', 'w+') as f:
                json.dump(repo_history.as_map(), f)

    print("Preprocessing repository's history")
    repo_history.preprocess_commits()
    if write_output:
        with open(f'{output_folder}/repo_history_preprocessed.json', 'w+') as f:
            json.dump(repo_history.as_map(), f)

    plot_data(repo_history)


if __name__ == '__main__':
    if not command_exists('git'):
        print("Missing `git`")
        exit(-1)

    if not command_exists('cloc'):
        print("Missing `cloc` utility")
        exit(-1)

    app.run(main)
