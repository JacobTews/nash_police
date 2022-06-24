# Preprocessing script
# 
# 

def event_number_clean(num):
    """
    Removes 'PD' from the beginning of each event number and recasts as int

    Meant to be apply()ed to the 'Event Number' column of dataframe.

    :param num: str, the original event number in the dataset

    :return: int, the cleaned event number
    """

    return int(num[2:])

