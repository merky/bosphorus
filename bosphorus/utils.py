
def format_date(date, format='%m/%d/%Y'):
    """ filter for date in jinja2 """
    if date is not None:
        return "%02d/%02d/%04d" % (date.month, date.day, date.year)
    else:
        return ''

jinja_filters = [
    ('format_date', format_date)
]
