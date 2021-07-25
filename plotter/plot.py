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
            plt.plot(x_values, y_values[y_value_index],
                     label=languages[y_value_index])
        plt.legend()
        plt.xlabel("Date")
        plt.ylabel("Lines of code")
        plt.show()
