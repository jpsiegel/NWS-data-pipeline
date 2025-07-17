from typing import Union, List, Optional, Dict
from app.utils.logging import get_logger
from typing import List, Dict, Optional
from datetime import datetime
import requests

logger = get_logger()

BASE_URL = "https://api.weather.gov"
USER_AGENT = "NWS-data-pipeline (https://github.com/jpsiegel/NWS-data-pipeline, jpsiegel@gmail.com)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/geo+json"
}


def format_datetime_utc(dt: datetime) -> str:
    """Format a datetime object as an ISO 8601 UTC string for the API."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def handle_json_response(
    response: requests.Response,
    expected_keys: Union[str, List[str]]
) -> Optional[Dict]:
    """
    Handle a JSON API response with structured error reporting.

    Args:
        response (requests.Response): The HTTP response object.
        expected_keys (str or list): One or more top-level keys to extract.

    Returns:
        Optional[dict]: A dict with the extracted keys and values, or None if error.
    """
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(expected_keys, str):
                expected_keys = [expected_keys]
            result = {}
            for key in expected_keys:
                if key not in data:
                    logger.warning(f"Response is missing expected key '{key}'.")
                    continue
                result[key] = data[key]
            if not result:
                return None
            return result
        except Exception as e:
            logger.error(f"Failed to parse successful JSON response: {e}")
            return None
    else:
        try:
            error_data = response.json()
            logger.error(
                f"API request failed with status {response.status_code}: {error_data.get('title')}, detail: {error_data.get('detail')}, {error_data.get('type')}"
            )
        except Exception:
            logger.error(f"API request failed with status {response.status_code}, and response could not be parsed as JSON.")
        return None


def validate_station(station_id: str) -> Optional[dict]:
    """
    Check if a station ID exists in the NWS API and retrieve its metadata.

    Args:
        station_id (str): The ID of the station to validate (e.g., '000SE').

    Returns:
        Optional[dict]: The 'properties' metadata of the station if valid, else None.
    """
    url = f"{BASE_URL}/stations/{station_id}"
    logger.info(f"Validating station ID: {station_id} by requesting its metadata")

    # Call endpoint
    response = requests.get(url, headers=HEADERS)
    station_data = handle_json_response(response, expected_keys=["properties", "geometry"])

    if not station_data:
        logger.error(f"Station '{station_id}' could not be found in NWS API.")
        return None

    # Handle properties
    props = station_data.get("properties", {})
    geometry = station_data.get("geometry", {})
    coords = geometry.get("coordinates", [None, None])
    lon, lat = coords
    props["longitude"] = lon
    props["latitude"] = lat

    logger.info(f"Station '{station_id}' found: {props.get('name', 'Unknown')}")
    return props


def fetch_observations(
    station_id: str,
    start: datetime,
    end: datetime,
    limit: int = 500
) -> Optional[List[Dict]]:
    """
    Fetch weather observations for a station within a time range.

    Args:
        station_id (str): The ID of the station (e.g., '0112W').
        start (datetime): Start of the observation range (UTC).
        end (datetime): End of the observation range (UTC).
        limit (int): Max number of results (default 500).

    Returns:
        Optional[List[dict]]: List of GeoJSON Feature objects with weather data, or None if failed.
    """
    url = f"{BASE_URL}/stations/{station_id}/observations"
    params = {
        "start": format_datetime_utc(start),
        "end": format_datetime_utc(end),
        "limit": limit
    }

    logger.info(f"Requesting observations from {params.get('start')} to {params.get('end')} at {url}")

    # Call endpoint
    response = requests.get(url, headers=HEADERS, params=params)
    result = handle_json_response(response, expected_keys="features")
    features = result.get("features")

    return features


def parse_observation(obs: dict) -> dict:
    """
    Extract and round relevant weather fields from a raw NWS observation feature.

    Args:
        obs (dict): A single GeoJSON Feature from the /observations endpoint.

    Returns:
        dict: Cleaned and rounded weather data with keys matching database fields.
    """
    props = obs.get("properties", {})

    def extract_value(field: str) -> Optional[float]:
        val = props.get(field, {}).get("value")
        if isinstance(val, (int, float)):
            return round(val, 2)
        return None

    return {
        "timestamp": props.get("timestamp"),
        "temperature": extract_value("temperature"),
        "humidity": extract_value("relativeHumidity"),
        "wind_speed": extract_value("windSpeed"),
        "wind_direction": extract_value("windDirection"),
        "pressure": extract_value("barometricPressure"),
        "dewpoint": extract_value("dewpoint"),
        "visibility": extract_value("visibility"),
    }
