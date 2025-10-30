TIME_CONVERTER = {
    '08:00': 0, '09:00': 1, '10:00': 2, '11:00': 3, '12:00': 4, '13:00': 5,
    '14:00': 6, '15:00': 7, '16:00': 8, '17:00': 9, '18:00': 10, '19:00': 11,
    '20:00': 0, '21:00': 1, '22:00': 2, '23:00': 3, '00:00': 4, '01:00': 5,
    '02:00': 6, '03:00': 7, '04:00': 8, '05:00': 9, '06:00': 10, '07:00': 11
}

CONVERTER_DAY = {k: v for k, v in TIME_CONVERTER.items() if k in [
    '08:00', '09:00', '10:00', '11:00', '12:00', '13:00',
    '14:00', '15:00', '16:00', '17:00', '18:00', '19:00']
}

CONVERTER_NIGHT = {k: v for k, v in TIME_CONVERTER.items() if k not in CONVERTER_DAY}

ALL_HOURS = [
    '08:00', '09:00', '10:00', '11:00', '12:00', '13:00',
    '14:00', '15:00', '16:00', '17:00', '18:00', '19:00',
    '20:00', '21:00', '22:00', '23:00', '00:00', '01:00',
    '02:00', '03:00', '04:00', '05:00', '06:00', '07:00'
]

def hour_str_to_index(hour_str):
    '''Convert an hour string (e.g. "08:00") to timetable index (0-11).'''
    return TIME_CONVERTER.get(hour_str)

def index_to_hour_str(index, shift_type='day'):
    '''Convert index back to hour string; shift_type can be 'day' or 'night'.'''
    hours = list(CONVERTER_DAY.keys()) if shift_type == 'day' else list(CONVERTER_NIGHT.keys())
    try:
        return hours[index % 12]
    except IndexError:
        return None

def times_list_to_indices(times_list):
    '''Convert a list of hour strings to timetable indices.'''
    return [TIME_CONVERTER.get(t, 0) for t in times_list if t in TIME_CONVERTER]
