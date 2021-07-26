from datetime import datetime
import matplotlib.pyplot as plt

from .model.src.repo_history import RepoHistory


class Plotter(object):
    def __init__(self, repo_history):
        if not isinstance(repo_history, RepoHistory):
            raise Exception(
                "Plotter class must be initialized with a RepoHistory object")
        self.repo_history = repo_history

    def plot(self, languages=[]):
        """
            Plots the `RepoHistory` object

            if `languages` is empty, it will plot the aggregated data
        """
        x_values = [
            f"{date.day}/{date.month}/{date.year}" if isinstance(date, datetime) else date for date in self.repo_history.get_commit_dates()]

        print("Which field you want to plot?")
        available_fields = [(0, 'code', 'Lines of code'), (1, 'nFiles', 'Number of files'),
                            (2, 'blank', 'Blank lines'), (3, 'comment', 'Comment lines')]
        ok = False
        while not ok:
            ok = True
            for item in available_fields:
                print(f"{item[0]}: {item[2]}")

            field = input("Pick one field to plot: ")
            avals = [aval[0] for aval in available_fields]
            if int(field) not in avals:
                ok = False
                print(f"Field {field} is not available")

        field, for_label = available_fields[int(
            field)][1], available_fields[int(field)][2]

        y_values = self.repo_history.get_commit_data(languages, field=field)

        for y_value_index in range(len(y_values)):
            values = y_values[y_value_index]
            if len(values) == 0:
                value_to_repeat = 0
            else:
                value_to_repeat = values[-1]
            while len(values) != len(x_values):
                values.append(value_to_repeat)

            plt.plot(x_values, values, linestyle='dashed', marker='s',
                     label=languages[y_value_index])

        plt.legend()
        if isinstance(x_values[0], datetime):
            plt.xlabel("Commit dates")
        else:
            plt.xlabel("Commit number")

        plt.ylabel(for_label)

        plt.show()
