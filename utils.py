def new_name(old):
    '''Remove ()° and replaces ' ' and '/' by '_'.

    Example:
    >>> old = "Date/Time"
    >>> new_name(old)
    "data_time"
    >>> old = "Temp (°C)"
    >>> new_name(old)
    "temp_c"
    '''

    trans_table = str.maketrans(' /', '__', '()°')
    new = old.translate(trans_table)
    return new.lower()
