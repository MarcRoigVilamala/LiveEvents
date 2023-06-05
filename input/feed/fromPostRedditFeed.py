import os.path

import pandas as pd
import praw


class FromPostRedditFeed(object):
    def __init__(self, from_post, replace_more_limit=0, praw_name="LiveEvents", max_comments=None):
        self.reddit = praw.Reddit(praw_name, config_interpolation="basic")

        self.submission = self.reddit.submission(url=from_post)

        self.submission.comments.replace_more(limit=replace_more_limit)

        columns = [
            'post_id',
            'subreddit',
            'author',
            'created_utc',
            'score',
            'total_awards_received',
            'body',
        ]
        comments = self.submission.comments.list()
        if max_comments:
            comments = comments[:max_comments]
        entry_list = [
            [
                c.id,                      # 'post_id'
                c.subreddit.display_name,  # 'subreddit'
                c.author.name,             # 'author'
                c.created_utc,             # 'created_utc'
                c.score,                   # 'score'
                c.total_awards_received,   # 'total_awards_received'
                c.body,                    # 'body'
            ]
            for c in comments
            if c.author  # If author is None the comment has been [deleted], and thus is skipped
        ]

        self.df = pd.DataFrame(data=entry_list, columns=columns)

        filepath = "./data/Reddit/{}.pkl".format(from_post[23:].replace('/', '_'))
        if not os.path.exists(filepath):
            self.df.to_pickle(filepath)

    def get_max_length(self):
        return len(self.df.index) - 1

    def __iter__(self):
        return self.df.iterrows()
