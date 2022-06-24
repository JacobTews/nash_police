# Preprocessing script
# 
# 

import pandas as pd

def event_number_clean(num):
    """
    Removes 'PD' from the beginning of each event number and recasts as int

    Meant to be apply()ed to the 'Event Number' column of dataframe.

    :param num: str, the original event number in the dataset

    :return: int, the cleaned event number
    """

    return int(num[2:])


def preprocess():
    pass
    
    # drop unneeded columns
    df = df.drop(['Tencode Description', 'Tencode Suffix Description'], axis=1)
    
    # after all preprocessing done, save the file to a feather
    df.to_feather('/data/calls.feather')
    print('Feather successfully created')
    

if __name__ == '__main__':
    preprocess()