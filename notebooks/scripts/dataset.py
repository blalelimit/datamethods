import numpy as np
import pandas as pd
import random as rd


class Food:
    def __init__(self, items, probability, max_items):
        self.items = items
        self.probability = probability
        self._scaled_probability = None
        self.max_items = max_items

    @property
    def scaled_probability(self):
        return [x/sum(self.probability) for x in self.probability]


    def choose_items(self):
        n_items = rd.randint(1, self.max_items)
        return np.random.choice(a=self.items, size=n_items, replace=False, p=self.scaled_probability)


def generate_arr(items, probability, max_items=5, length=10, mode='defined'):
    if mode == 'rand':
        probability = [rd.random() for _ in range(len(items))]
    list_items = list()
    for _ in range(length):
        chosen_items = Food(items, probability, max_items).choose_items()
        list_items.append(list(chosen_items))
    return list_items


def transform_arr(df, items):
    new_df = pd.DataFrame(False, index=np.arange(len(df)), columns=items)
    for x in range(len(new_df)):
        for item in items:
            if item in list(df.iloc[x]):
                new_df.at[x, item] = True
    return new_df