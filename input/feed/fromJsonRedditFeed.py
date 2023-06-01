import json

import pandas as pd
from tqdm import tqdm


class FromJsonRedditFeed(object):
    def __init__(self, from_file):
        with open(from_file, 'r') as f:
            loaded_json = json.load(f)

        loaded_json['post_id'] = loaded_json.pop('_id')

        json_keys = loaded_json.keys()

        columns = [k for k in json_keys]

        entry_list = []
        for i, identifier in tqdm(loaded_json['post_id'].items()):
            entry_list.append(
                [
                    loaded_json[c][i]  # For each column, get the corresponding value
                    for c in columns
                ]
            )

        self.df = pd.DataFrame(data=entry_list, columns=columns)

    def get_max_length(self):
        return len(self.df.index) - 1

    def __iter__(self):
        return self.df.iterrows()
