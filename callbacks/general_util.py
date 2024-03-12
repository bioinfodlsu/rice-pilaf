import pandas as pd
import regex as re

NULL_PLACEHOLDER = "–"


def display_in_sci_notation(number):
    """
    Returns given number in scientific notation n * 10^m, where n is rounded to 6 decimal places

    Parameters:
    - number: Number whose equivalent in scientific notation is to be returned

    Returns:
    - Number in scientific notation
    """
    return "{:.6e}".format(number)


def display_in_fixed_dec_places(number):
    return "{:.6f}".format(float(number))


def display_cols_in_sci_notation(result, numeric_columns):
    for column in numeric_columns:
        result[column] = result[column].apply(display_in_sci_notation)


def display_cols_in_fixed_dec_places(result, numeric_columns):
    for column in numeric_columns:
        result[column] = result[column].apply(display_in_fixed_dec_places)


def create_empty_df_with_cols(cols):
    cols_dict = {}
    for col in cols:
        cols_dict[col] = [NULL_PLACEHOLDER]

    return pd.DataFrame(cols_dict)


def get_tab_index(tab_id):
    return int(tab_id.split("-")[1])


def get_num_unique_entries(table, column):
    if table[column].iloc[0] == NULL_PLACEHOLDER:
        return 0

    return table[column].nunique()


def get_num_entries(table, column):
    if table[column].iloc[0] == NULL_PLACEHOLDER:
        return 0

    return table[column].count()


def count_non_empty_vals(array):
    ctr = 0
    for elem in array:
        if elem != NULL_PLACEHOLDER:
            ctr += 1

    return ctr


def purge_html_export_table(table):
    for row in table:
        for key in row.keys():
            try:
                row[key] = row[key].replace("&nbsp;", "")
                row[key] = row[key].replace(NULL_PLACEHOLDER, "")
                row[key] = row[key].replace("<br>", ";")
                row[key] = row[key].replace("<li>", ";")
                row[key] = row[key].replace("\n", ";")
                row[key] = re.sub(r"<.+?>", "", row[key])
                row[key] = re.sub(r";+", ";", row[key])
                row[key] = re.sub(r"^;", "", row[key])
            except AttributeError:
                pass

    return table
