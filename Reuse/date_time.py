from datetime import datetime


def get_current_date_standard_format():
    now = datetime.now()
    formatted_date = now.strftime("%m/%d/%Y")
    return formatted_date


def is_valid_date_standard_format(date_string):
    try:
        datetime.strptime(date_string, '%m/%d/%Y')
        return True
    except ValueError:
        return False
