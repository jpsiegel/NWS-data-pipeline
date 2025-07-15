import requests
import pprint

BASE_URL = "https://api.weather.gov"
USER_AGENT = "NWS-data-pipeline (https://github.com/jpsiegel/NWS-data-pipeline, jpsiegel@gmail.com)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/geo+json"
}

def list_stations(limit=5):
    url = f"{BASE_URL}/stations?limit={limit}"
    print(f"\n📡 Fetching {limit} stations...")
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    stations = data.get("features", [])
    
    for s in stations:
        props = s["properties"]
        coords = s["geometry"]["coordinates"]
        print(f"- ID: {props['stationIdentifier']}, Name: {props['name']}, Coords: {coords}, Timezone: {props['timeZone']}")
    
    return stations

def get_observations(station_id):
    url = f"{BASE_URL}/stations/{station_id}/observations"
    print(f"\n🌦 Fetching observations for station {station_id}...")
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    obs_data = resp.json()
    return obs_data.get("features", [])

def parse_observation(obs):
    props = obs["properties"]
    def round_val(field):
        val = props.get(field, {}).get("value")
        return round(val, 2) if isinstance(val, (int, float)) else None
    
    return {
        "timestamp": props.get("timestamp"),
        "temperature": round_val("temperature"),
        "humidity": round_val("relativeHumidity"),
        "wind_speed": round_val("windSpeed"),
        "pressure": round_val("barometricPressure")
    }

def main():
    # Part 1: Preview a few stations
    stations = list_stations(limit=5)

    # Part 2: Get observations for sample station
    station_id = "000PG"  # from assignment
    observations = get_observations(station_id)
    print(f"\n📈 Found {len(observations)} observations.")

    if observations:
        for i, obs in enumerate(observations[:5]):  # limit preview to first 5
            parsed = parse_observation(obs)
            print(f"\nObservation #{i+1}")
            pprint.pprint(parsed)
    else:
        print("⚠️  No observations found.")

if __name__ == "__main__":
    main()
