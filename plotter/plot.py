import matplotlib.pyplot as plt

from .model.src.repo_history import RepoHistory


class Plotter(object):
    def __init__(self, repo_history):
        if not isinstance(repo_history, RepoHistory):
            raise Exception(
                "Plotter class must be initialized with a RepoHistory object")
        if not repo_history.preprocessed:
            repo_history.preprocess_commits()
        self.repo_history = repo_history

    def plot(self, languages=[]):
        """
            Plots the `RepoHistory` object

            if `languages` is empty, it will plot the aggregated data
        """
        x_values = [
            f"{date.day}/{date.month}/{date.year}" for date in self.repo_history.get_commit_dates()]
        y_values = self.repo_history.get_commit_data(languages)

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

        plt.show()
