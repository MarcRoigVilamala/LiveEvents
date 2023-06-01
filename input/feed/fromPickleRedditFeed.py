import pandas as pd
import praw


class FromPickleRedditFeed(object):
    def __init__(self, from_pickle, max_comments=None):
        self.df = pd.read_pickle(from_pickle)

        if max_comments:
            self.df = self.df[:max_comments]
            # self.df = self.df.loc[[2, 23, 24, 33]]

    def get_max_length(self):
        return len(self.df.index) - 1

    def __iter__(self):
        return self.df.iterrows()
