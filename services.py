from datetime import date, timedelta

def business_days_between(start_date: date, end_date: date) -> int:
    """
    Cuenta días hábiles entre start_date y end_date (incluyendo ambos).
    Excluye sábados y domingos.
    """
    if end_date < start_date:
        return 0
    day_count = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            day_count += 1
        current += timedelta(days=1)
    return day_count
