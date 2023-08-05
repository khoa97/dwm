import subprocess
import re
import time
import requests
def get_temperature_from_sensors():
    try:
        result = subprocess.check_output(['sensors'], universal_newlines=True)
        temp_pattern = re.compile(r'(?P<label>\w+):\s+\+(?P<temp>\d+\.\d+)°C')

        temperatures = {}
        for match in temp_pattern.finditer(result):
            label = match.group('label')
            temp = float(match.group('temp'))
            temperatures[label] = temp

        # Try to return the composite or package temperature
        for key in ['Composite', 'Package id0']:  # You can adjust this list based on your sensor names
            if key in temperatures:
                return temperatures[key]

        # If not found, return the first temperature (or None if no temperatures were found)
        return temperatures[next(iter(temperatures))] if temperatures else None

    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_weather_info(location=""):
    url = f"https://wttr.in/{location}?format=%C|%t"
    response = requests.get(url)
    conditions, temp = response.text.split('|')
    keyword = extract_keyword(conditions.strip())
    icon = get_weather_icon(keyword)
    return f"{icon} {conditions.strip()} {temp.strip()}"

def get_weather_icon(keyword):
    icon_map = {
        'clear': '\uf00d',
        'sunny': '\uf00d',
        'cloudy': '\uf0c2',
        'overcast': '\uf0c2',
        'mist': '\uf0c5',
        'rain': '\uf019',
        'snow': '\uf01b',
        'sleet': '\uf0c2',    # Using cloud as there isn't a direct icon for sleet in FontAwesome 4
        'drizzle': '\uf019',
        'thunder': '\uf01e',
        'blowing': '\uf063',  # Wind icon for blowing snow
        'blizzard': '\uf01b',
        'fog': '\uf014',
        'freezing': '\uf017',  # Using moon for freezing conditions (no direct match)
        'ice': '\uf076',      # Using asterisk for ice pellets
        'shower': '\uf019',
        'torrential': '\uf019',
    }
    return icon_map.get(keyword, '\uf07b')  # Default: FontAwesome 


def extract_keyword(conditions):
    patterns = [
        'clear', 'sunny', 'cloudy', 'overcast', 'mist', 'rain', 'snow', 
        'sleet', 'drizzle', 'thunder', 'blowing', 'blizzard', 'fog',
        'freezing', 'ice', 'shower', 'torrential'
    ]
    for pattern in patterns:
        if re.search(pattern, conditions, re.I):  # re.I makes the search case-insensitive
            return pattern
    return None

def print_statusbar():
    weather_info = get_weather_info()  # Get initial weather info
    elapsed_minutes = 0
    while True:
        current_time_str = getTime()
        cpu_temp = get_temperature_from_sensors()
        weather_info = get_weather_info()
        if elapsed_minutes >= 10:
            weather_info = get_weather_info()
            elapsed_minutes = 0  # Reset the counter

        if cpu_temp is not None:
            set_dwm_status(f"  \uf017  { current_time_str} | \uf2db {cpu_temp}°C | {weather_info}")
      

        sleep_time = 60 - time.localtime().tm_sec
        time.sleep(sleep_time)
        elapsed_minutes += 1  # Increment the counter

def getTime():
    current_time = time.localtime()
    return time.strftime("%I:%M %p", current_time)

def set_dwm_status(status_text):
    """Set the DWM status bar using xsetroot."""
    subprocess.run(['xsetroot', '-name', status_text])
if __name__ == "__main__":
    print_statusbar()
