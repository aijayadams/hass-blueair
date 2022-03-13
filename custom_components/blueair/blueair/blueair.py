"""This module provides the Blueair class to communicate with the Blueair API."""

import base64
import logging
import requests

from typing import Any, Dict, List, Mapping, Union
from typing_extensions import TypedDict

logger = logging.getLogger(__name__)

# The BlueAir API uses a fixed API key.
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJncmFudGVlIjoiYmx1ZWFpciIsImlhdCI6MTQ1MzEyNTYzMiwidmFsaWRpdHkiOi0xLCJqdGkiOiJkNmY3OGE0Yi1iMWNkLTRkZDgtOTA2Yi1kN2JkNzM0MTQ2NzQiLCJwZXJtaXNzaW9ucyI6WyJhbGwiXSwicXVvdGEiOi0xLCJyYXRlTGltaXQiOi0xfQ.CJsfWVzFKKDDA6rWdh-hjVVVE9S3d6Hu9BzXG9htWFw"  # noqa: E501

MeasurementBundle = TypedDict(
    "MeasurementBundle",
    {"sensors": List[str], "datapoints": List[List[Union[int, float]]]},
)

MeasurementList = List[Mapping[str, Union[int, float]]]


def transform_data_points(data: MeasurementBundle) -> MeasurementList:
    """Transform a measurement list response from the Blueair API to a more pythonic data structure."""
    key_mapping = {
        "time": "timestamp",
        "pm": "pm25",
        "pm1": "pm1",
        "pm10": "pm10",
        "tmp": "temperature",
        "hum": "humidity",
        "co2": "co2",
        "voc": "voc",
        "allpollu": "all_pollution",
    }

    keys = [key_mapping[key] for key in data["sensors"]]

    return [dict(zip(keys, values)) for values in data["datapoints"]]


class BlueAir(object):
    """This class provides API calls to interact with the Blueair API."""

    def __init__(
        self,
        username: str,
        password: str,
        home_host: str = None,
        auth_token: str = None,
    ) -> None:
        """
        Instantiate a new Blueair client with the provided username and password.

        To optimize multiple instantiatons of this class a server hostname and
        authentication token can be provided. This will cause the client to
        reuse a session from a previously initialized client and saves up to
        two API calls.
        """
        self.username = username
        self.password = password
        self.home_host = home_host
        self.auth_token = auth_token

        if not self.home_host:
            self.home_host = self.get_home_host()

        if not self.auth_token:
            self.auth_token = self.get_auth_token()

    def get_home_host(self) -> str:
        """
        Retrieve the home host for the current username.

        The home host is the server that is used to interact with the Blueair
        device. It can be stored and reused to avoid requesting it again when
        reinitializing the class at a later time.
        """
        logger.info(f"GET https://api.blueair.io/v2/user/{self.username}/homehost/")

        response = requests.get(
            f"https://api.blueair.io/v2/user/{self.username}/homehost/",
            headers={"X-API-KEY-TOKEN": API_KEY},
        )

        return response.text.replace('"', "")

    def get_auth_token(self) -> str:
        """
        Authenticate the user and retrieve the authentication token.

        The authentication token can be reused to prevent an additional network
        request when initializing the client.
        """
        logger.info(f"GET https://{self.home_host}/v2/user/{self.username}/login/")

        response = requests.get(
            f"https://{self.home_host}/v2/user/{self.username}/login/",
            headers={
                "X-API-KEY-TOKEN": API_KEY,
                "Authorization": "Basic "
                + base64.b64encode(
                    (self.username + ":" + self.password).encode()
                ).decode(),
            },
        )

        return response.headers["X-AUTH-TOKEN"]

    def api_call(self, path: str) -> Any:
        """
        Perform a Blueair API call.

        This is a low level function that is used by most of the client API calls.
        """
        logger.info(f"GET https://{self.home_host}/v2/{path}")

        return requests.get(
            f"https://{self.home_host}/v2/{path}",
            headers={"X-API-KEY-TOKEN": API_KEY, "X-AUTH-TOKEN": self.auth_token},
        ).json()

    def get_devices(self) -> List[Dict[str, Any]]:
        """
        Fetch a list of devices.

        Returns a list of dictionaries. Each dictionary will have a UUID key
        (the device identifier), a user ID, MAC address, and device name.

        Example response:

        [{"uuid":"1234567890ABCDEF","userId":12345,"mac":"1234567890AB","name":"My Blueair Device"}]
        """
        return self.api_call(f"owner/{self.username}/device/")

    # Note: refreshes every 5 minutes
    def get_attributes(self, device_uuid: str) -> Dict[str, Any]:
        """
        Fetch a list of attributes for the provided device ID.

        The return value is a dictionary containing key-value pairs for any
        available attributes.

        Note: the data for this API call is only updated once every 5 minutes.
        Calling it more often will return the same respone from the server and
        should be avoided to limit server load.
        """
        attributes = {}
        for item in self.api_call(f"device/{device_uuid}/attributes/"):
            attributes[item["name"]] = item["currentValue"]

        return attributes

    # Note: refreshes every 5 minutes, timestamps are in seconds
    def get_info(self, device_uuid: str) -> Dict[str, Any]:
        """
        Fetch device information for the provided device ID.

        The return value is a dictionary containing key-value pairs for the
        available device information.

        Note: the data for this API call is only updated once every 5 minutes.
        Calling it more often will return the same respone from the server and
        should be avoided to limit server load.
        """
        return self.api_call(f"device/{device_uuid}/info/")

    def set_fan_speed(self, device_uuid, new_speed):
        """
        Set the fan speed per @spikeyGG comment at https://community.home-assistant.io/t/blueair-purifier-addon/154456/14
        """
        res = requests.post(
            f"https://{self.home_host}/v2/device/{device_uuid}/attribute/fanspeed/",
            headers={
                "Content-Type": "application/json",
                "X-API-KEY-TOKEN": API_KEY,
                "X-AUTH-TOKEN": self.auth_token,
            },
            json={
                "currentValue": new_speed,
                "scope": "device",
                "defaultValue": new_speed,
                "name": "fan_speed",
                "uuid": device_uuid,
            },
        )

    def set_fan_mode(self, device_uuid, new_mode):
        """
        Set the fan mode to automatic
        """
        if new_mode == None:
            new_mode="manual"

        res = requests.post(
            f"https://{self.home_host}/v2/device/{device_uuid}/attribute/mode/",
            headers={
                "Content-Type": "application/json",
                "X-API-KEY-TOKEN": API_KEY,
                "X-AUTH-TOKEN": self.auth_token,
            },
            json={
                "currentValue": new_mode,
                "scope": "device",
                "defaultValue": new_mode,
                "name": "mode",
                "uuid": device_uuid,
            },
        )

    # Note: refreshes every 5 minutes
    def get_current_data_point(
        self, device_uuid: str
    ) -> Mapping[str, Union[int, float]]:
        """
        Fetch the most recent data point for the provided device ID.

        Returns a dictionary containing a key-value mapping for the most recent
        measurements.

        Note: the data for this API call is only updated once every 5 minutes.
        Calling it more often will return the same respone from the server and
        should be avoided to limit server load.
        """
        data = self.api_call(f"device/{device_uuid}/datapoint/0/last/0/")

        results = transform_data_points(data)
        return results[-1]

    # Note: refreshes every 5 minutes
    def get_data_points_since(
        self, device_uuid: str, seconds_ago: int = 0, sample_period: int = 0
    ) -> MeasurementList:
        """
        Fetch the list of data points between a relative timestamp (in seconds) and the current time.

        An optional sample period can be provided to group data points
        together. The minimum sample period size is 300 (5 minutes).

        Note: the data for the most recent data point is only updated once
        every 5 minutes.  Calling it more often will return the same respone
        from the server and should be avoided to limit server load.
        """
        data = self.api_call(
            f"device/{device_uuid}/datapoint/{seconds_ago}/last/{sample_period}/"
        )

        results = transform_data_points(data)

        # Remove the last element because it does not have the final timestamp yet
        # TODO: Only remove if it is equal to end_timestamp
        results.pop()

        return results

    # Setting sample_period to a value higher than 300 (the minimum sample
    # period) will cause measurements to be averaged. Leave the sample period
    # to 0 to use the server's default period (300 seconds).  Calling this
    # function more than once per sample period will give the same results, so
    # make sure to throttle these calls to conserve API bandwidth.
    def get_data_points_between(
        self,
        device_uuid: str,
        start_timestamp: int,
        end_timestamp: int,
        sample_period: int = 0,
    ) -> MeasurementList:
        """
        Fetch the list of data points between two timestamps.

        The start and end timestamp are specified in seconds since the Unix
        epoch.

        An optional sample period can be provided to group data points
        together. The minimum sample period size is 300 (5 minutes).

        Note: the data for the most recent data point is only updated once
        every 5 minutes.  Calling it more often will return the same respone
        from the server and should be avoided to limit server load.
        """
        data = self.api_call(
            f"device/{device_uuid}/datapoint/{start_timestamp}/{end_timestamp}/{sample_period}/"
        )

        results = transform_data_points(data)

        # Remove the last element because it does not have the final timestamp yet
        # TODO: Only remove if it is equal to end_timestamp
        results.pop()

        return results
