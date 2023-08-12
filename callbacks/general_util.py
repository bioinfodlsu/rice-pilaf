def display_in_sci_notation(number):
    """
    Returns the given number in scientific notation n * 10^m, where n is rounded to 6 decimal places

    Parameters:
    - number: Number whose equivalent in scientific notation is to be returned

    Returns:
    - Number in scientific notation
    """
    return '{:.6e}'.format(number)
