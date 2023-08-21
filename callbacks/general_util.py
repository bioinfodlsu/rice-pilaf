import pandas as pd


def display_in_sci_notation(number):
    """
    Returns given number in scientific notation n * 10^m, where n is rounded to 6 decimal places

    Parameters:
    - number: Number whose equivalent in scientific notation is to be returned

    Returns:
    - Number in scientific notation
    """
    return '{:.6e}'.format(number)


def display_in_fixed_dec_places(number):
    return '{:.6f}'.format(float(number))


def display_cols_in_sci_notation(result, numeric_columns):
    for column in numeric_columns:
        result[column] = result[column].apply(display_in_sci_notation)


def display_cols_in_fixed_dec_places(result, numeric_columns):
    for column in numeric_columns:
        result[column] = result[column].apply(display_in_fixed_dec_places)


def create_empty_df_with_cols(cols):
    cols_dict = {}
    for col in cols:
        cols_dict[col] = ['&hyphen;']

    return pd.DataFrame(cols_dict)


def get_tab_index(tab_id):
    return int(tab_id.split('-')[1])


def get_num_unique_entries(table, column):
    if table[column].iloc[0] == '-' or table[column].iloc[0] == '&hyphen;':
        return 0

    return table[column].nunique()
