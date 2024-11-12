from datetime import datetime
import pytz

def get_current_timestamp(zone:str = "Asia/Calcutta") -> str:
    timezone = pytz.timezone(zone)
    current_time = datetime.now(timezone)

    # Format the current time
    formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

    # Adjust the timezone offset to match the format (+03:00)
    # take substring from beginning till two characters before the end
    # add ":" and then add the last two characters
    formatted_time = formatted_time[:-2] + ':' + formatted_time[-2:]

    return formatted_time