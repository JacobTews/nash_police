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


def disposition_code_clean(row):
    
    # The three variables calculated here must all be strings for the function to work.
    
    # First test for nan (the disposition code or tencode is a float if it is nan, otherwise it's a str).
    if isinstance(row['Disposition Code'], float):
        return row
    else:
        disp_code_letter = str(row['Disposition Code'])[-1:]
        disp_code_number = str(row['Disposition Code'])[:-1]

    if isinstance(row['Tencode Suffix'], float):
        tencode_suffix = ''
    else:
        tencode_suffix = str(row['Tencode Suffix'])
    
    if disp_code_letter.isnumeric():
        return row
    elif disp_code_letter not in ['A', 'C', 'O', 'P']:
        if disp_code_letter not in tencode_suffix:
            row['Tencode Suffix'] = tencode_suffix + disp_code_letter
        else:
            return row    
    else:
        if disp_code_letter == 'A':
            if disp_code_number in ['1', '4', '5', '7', '8', '9', '10', '11', '13', '14', '15']:
                if disp_code_letter not in tencode_suffix:
                    row['Tencode Suffix'] = tencode_suffix + disp_code_letter
                    row['Disposition Code'] = disp_code_number
                else:
                    row['Disposition Code'] = disp_code_number
            else:
                return row
        elif disp_code_letter in ['C', 'O', 'P']:
            if disp_code_letter not in tencode_suffix:
                row['Tencode Suffix'] = tencode_suffix + disp_code_letter
            else:
                return row
    
    # After all the above processing, if there is still nothing in the tencode suffix column, return it to nan
    if row['Tencode Suffix'] == '':
        row['Tencode Suffix'] = np.nan
    
    return row


def preprocess():
    pass
    
    # drop unneeded columns
    df = df.drop(['Tencode Description', 'Tencode Suffix Description'], axis=1)
    
    # after all preprocessing done, save the file to a feather
    df.to_feather('/data/calls.feather')
    print('Feather successfully created')
    

if __name__ == '__main__':
    preprocess()