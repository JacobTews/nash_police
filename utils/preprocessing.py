import numpy as np
import pandas as pd
from datetime import datetime


# *******
# Preprocessing Functions

def complaint_number_clean(num):
    if np.isnan(num):
        return 0
    else:
        return 1

    
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


def event_number_clean(num):
    """
    Removes 'PD' from the beginning of each event number and recasts as int

    Meant to be apply()ed to the 'Event Number' column of dataframe.

    :param num: str, the original event number in the dataset

    :return: int, the cleaned event number
    """

    return int(num[2:])


def import_data():
    
    t0 = datetime.now()
    
    # import dataset
    df = pd.read_csv('data/Metro_Nashville_Police_Department_Calls_for_Service.csv',
                      parse_dates=['Call Received'],
                     dtype={'Event Number': str,
                            'Complaint Number': float,
                            'Call Received': str,
                            'Tencode': str,
                            'Tencode Description': str,
                            'Tencode Suffix': str,
                            'Tencode Suffix Description': str,
                            'Disposition Code': str,
                            'Disposition Description': str,
                            'Block': float,
                            'Street Name': str,
                            'Unit Dispatched': str,
                            'Shift': str,
                            'Sector': str,
                            'Zone': str,
                            'RPA': float,
                            'Latitude': float,
                            'Longitude': float,
                            'Mapped Location': str
                           }
                    )
    
    import_t = datetime.now()
    print(f'Data imported successfully.\n'
          f'Import time: {import_t - t0}\n'
          f'Total elapsed time: {import_t - t0}\n\n\n')
    
    return df

    
def sector_and_zone_clean(row):
    
    zone_to_sect_dct = {'1': 'W',
                        '2': 'E',
                        '3': 'S',
                        '4': 'C',
                        '5': 'H',
                        '6': 'N',
                        '7': 'M',
                        '8': 'MH'
                       }
    
    # this dict won't catch all typos (with more time, I'd throw some regex at it haha!), but it will help
    typo_dct = {'TE': 'E',
                'PCW': 'W',
                'ECC': 'C',
                'CENTRA': 'C',
                'CW': 'W',
                'HERMIT': 'H',
                'SOUTH': 'S',
                'MADISO': 'M',
                'EAST': 'E',
                'WEST': 'W',
                'NORTH': 'N',
                'MIDTOW': 'MH'
               }
    
    
    # First test for nan (the zone or sector is a float if it is nan, otherwise it's a str).
    if isinstance(row['Sector'], float) and isinstance(row['Zone'], float):
        # both sector and zone are nans
        return row
    elif isinstance(row['Sector'], float):
        # sector is a nan
        sector_letter = ''
        if len(row['Zone']) > 3:
            # zone may include the sector letter(s)
            if row['Zone'][-2].isnumeric() and row['Zone'][-1].isalpha():
                # only the final char is alphabetic
                if row['Zone'][-1] in zone_to_sect_dct.values():
                    sector_letter = row['Zone'][-1]
                    zone_number = ''
                else:
                    zone_number = row['Zone'][:3]
            elif row['Zone'][-2].isalpha():
                # the final two chars are alphabetic
                if row['Zone'][-2:].upper() == 'MH':
                    sector_letter = 'MH'
                
                if row['Zone'][:3].isnumeric():
                    zone_number = row['Zone'][:3]
                else:
                    zone_number = ''
            else:
                # otherwise we assume the zone includes (an) extra digit(s) at the end, and we truncate
                zone_number = row['Zone'][:3]
        elif len(row['Zone']) < 3:
            zone_number = ''
        else:
            # zone is 3 characters, but one of them may be a letter, most likely the final char
            if row['Zone'].isnumeric():
                # zone is all numerals
                zone_number = row['Zone']
            else:
                zone_number = ''
                # zone includes either 1, 2, or 3 letters, in which case we do not have a valid zone number
                for i, char in enumerate(row['Zone'].upper()):
                    if i+1 < len(row['Zone']) and char in zone_to_sect_dct.values():
                        if char == 'M' and row['Zone'][i+1] == 'H':
                            # check if two successive chars are 'MH'
                            sector_letter = 'MH'
                        else:
                            sector_letter = char        
                    else:
                        if char in zone_to_sect_dct.values():
                            # if the final character is a sector code
                            sector_letter = char
        # at this point, the variable zone_number holds a str which is either a 3-digit numeral or empty
        # and the variable sector_letter is likely an empty str (because it was a null) or possibly had a value imputed from the zone
    elif isinstance(row['Zone'], float):
        # zone is a nan
        zone_number = ''
        if row['Sector'].isnumeric():
            if len(row['Sector']) == 3:
                # this would mean the zone was inadvertently placed into the sector column
                zone_number += row['Sector']
                sector_letter = ''
                # otherwise the sector is a number with something other than 3 digits, so needs to be discarded; zone_number is already an empty str
        elif row['Sector'] in zone_to_sect_dct.values():
            # the sector code is a proper code
            sector_letter = row['Sector']
        elif row['Sector'] not in zone_to_sect_dct.values():
            # the code is alphabetic but not a proper sector code
            if row['Sector'].upper() in typo_dct.keys():
                sector_letter = typo_dct[row['Sector'].upper()]
            else:
                sector_letter = ''
        else:
            # in all other cases, since I don't have additional information, I will simply remove the sector code
            sector_letter = ''
    else:
        # both codes are strings
        if row['Sector'].isnumeric():
            if len(row['Sector']) == 3:
                # this would mean the zone was inadvertently placed into the sector column
                zone_number = row['Sector']
                sector_letter = ''
            else:
                # otherwise the sector is a number with something other than 3 digits, so needs to be discarded
                sector_letter = ''
                if len(row['Zone']) > 3:
                    zone_number = row['Zone'][:3]
                elif len(row['Zone']) < 3:
                    zone_number = ''
                else:
                    zone_number = ''
                    # zone is 3 characters, but one of them may be a letter, most likely the final char
                    if row['Zone'].isnumeric():
                        # zone is all numerals
                        zone_number = row['Zone']
        elif row['Sector'] in zone_to_sect_dct.values():
            # the sector code is a proper code
            sector_letter = row['Sector']
            if len(row['Zone']) > 3:
                zone_number = row['Zone'][:3]
            elif len(row['Zone']) < 3:
                zone_number = ''
            else:
                zone_number = ''
                # zone is 3 characters, but one of them may be a letter, most likely the final char
                if row['Zone'].isnumeric():
                    # zone is all numerals
                    zone_number = row['Zone']
        elif row['Sector'] not in zone_to_sect_dct.values():
            # the code is alphabetic but not a proper sector code
            if row['Sector'].upper() in typo_dct.keys():
                sector_letter = typo_dct[row['Sector'].upper()]
                if len(row['Zone']) > 3:
                    zone_number = row['Zone'][:3]
                elif len(row['Zone']) < 3:
                    zone_number = ''
                else:
                    zone_number = ''
                    # zone is 3 characters, but one of them may be a letter, most likely the final char
                    if row['Zone'].isnumeric():
                        # zone is all numerals
                        zone_number = row['Zone']
            else:
                sector_letter = ''
                if len(row['Zone']) > 3:
                    zone_number = row['Zone'][:3]
                elif len(row['Zone']) < 3:
                    zone_number = ''
                else:
                    zone_number = ''
                    # zone is 3 characters, but one of them may be a letter, most likely the final char
                    if row['Zone'].isnumeric():
                        # zone is all numerals
                        zone_number = row['Zone']
        else:
            # in all other cases, since I don't have additional information, I will simply remove the sector code
            sector_letter = ''
            if len(row['Zone']) > 3:
                zone_number = row['Zone'][:3]
            elif len(row['Zone']) < 3:
                zone_number = ''
            else:
                zone_number = ''
                # zone is 3 characters, but one of them may be a letter, most likely the final char
                if row['Zone'].isnumeric():
                    # zone is all numerals
                    zone_number = row['Zone']
            

    # At this point, both sector_letter and zone_number should hold either empty str or useful information.
    # Now we can take the first digit of proper zone_numbers to determine the sector_letter.
    
    if sector_letter == '':
        if zone_number != '':
            # the sector is blank, but the zone is not
            try:
                sector_letter = zone_to_sect_dct[zone_number[0]]
                # the sector can be determined by the first char in the zone
            except:
                # if the first char in the zone is '9', this block will run
                sector_letter = np.nan
                zone_number = np.nan
            # else:
            #     # if the zone number is a proper value, the except block will not run and this will
            #     zone_number = int(zone_number)
        else:
            # sector and zone are both blank
            sector_letter = np.nan
            zone_number = np.nan
    else:
        # sector is not blank
        if zone_number == '':
            # zone is blank
            zone_number = np.nan
        # else:
        #     # otherwise neither sector nor zone is blank, in which case the variable values remain (with zone turned into an int for storage)
        #     zone_number = int(zone_number)
           
    # After all the above processing, we insert the two values into the dataframe
    row['Zone'] = zone_number
    row['Sector'] = sector_letter
    
    return row

def preprocess(df):
    """
    Preprocessing script for the Metro Nashville Police Department Calls for Service dataset

    :return: None
    """
    t0 = datetime.now()
    # drop unneeded columns
    df = df.drop(['Tencode Description',
                  'Tencode Suffix Description',
                  'Disposition Description',
                  'Unit Dispatched',
                  'RPA',
                  'Mapped Location'], axis=1)
    drop_t = datetime.now()
    print(f'Columns dropped successfully.\n'
          f'Drop time: {drop_t - t0}\n'
          f'Total elapsed time: {drop_t - t0}\n\n\n')
    
    # strip PD from event numbers
    df['Event Number'] = df['Event Number'].apply(event_number_clean)
    pd_strip_t = datetime.now()
    print(f'Event numbers cleaned successfully.\n'
          f'Event cleaning time: {pd_strip_t - drop_t}\n'
          f'Total elapsed time: {pd_strip_t - t0}\n\n\n')
    
    # create a boolean flag for whether an incident was generated
    df['generated_incident_yn'] = df['Complaint Number'].apply(complaint_number_clean)
    df = df.drop('Complaint Number', axis=1)
    incid_flag_t = datetime.now()
    print(f'Incident flag created successfully.\n'
          f'Flagging time: {incid_flag_t - pd_strip_t}\n'
          f'Total elapsed time: {incid_flag_t - t0}\n\n\n')
    
    # clean the disposition codes
    df = df.apply(disposition_code_clean, axis=1)
    disp_t = datetime.now()
    print(f'Disposition codes cleaned successfully.\n'
          f'Disposition cleaning time: {disp_t - incid_flag_t}\n'
          f'Total elapsed time: {disp_t - t0}\n\n\n')
    
    # update the shift feature to a categorical
    df['Shift'] = df['Shift'].astype('category')
    shift_t = datetime.now()
    print(f'Shift categories created successfully.\n'
          f'Shift categories time: {shift_t - disp_t}\n'
          f'Total elapsed time: {shift_t - t0}\n\n\n')    
    
    # clean the sector and zone features
    df = df.apply(sector_and_zone_clean, axis=1)
    sect_zone_t = datetime.now()
    print(f'Sectors and zones cleaned successfully.\n'
          f'Sector and zone cleaning time: {sect_zone_t - shift_t}\n'
          f'Total elapsed time: {sect_zone_t - t0}\n\n\n')
    
    # after all preprocessing done, reset the index, then return the cleaned df
    df = df.reset_index()
    
    return df

if __name__ == '__main__':
    pass