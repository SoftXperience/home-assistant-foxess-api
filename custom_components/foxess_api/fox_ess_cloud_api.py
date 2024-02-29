import hashlib
import json
import time
from datetime import datetime
from homeassistant.components.rest.data import RestData

from .const import BASE_URL, LOGGER, API_VERSION
from .sensor_descriptions import SENSORS


class FoxEssCloudApi:
    def __init__(self, hass, api_key, serial):
        self._hass = hass
        self._api_key = api_key
        self._serial = serial
        self.allData = {
            "realtime": {},
            "report": {},
            "last_update": None
        }

    @staticmethod
    def md5c(text="", _type="lower"):
        res = hashlib.md5(text.encode(encoding='UTF-8')).hexdigest()
        if _type.__eq__("lower"):
            return res
        else:
            return res.upper()

    async def request_data(self, method, path, query_params, request_body):
        try:
            LOGGER.debug("Requesting data from %s, with %s", path, request_body)

            timestamp = round(time.time() * 1000)
            signature_src = fr'{path}\r\n{self._api_key}\r\n{timestamp}'
            signature = self.md5c(text=signature_src)
            url = "{}{}".format(
                BASE_URL,
                path
            )
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "HA-Integration/1.0.0",
                "token": self._api_key,
                "timestamp": str(timestamp),
                "signature": signature,
                "lang": "en"
            }

            client = RestData(self._hass,
                              method, url,
                              "UTF-8",
                              None,
                              headers,
                              query_params,
                              request_body,
                              False,
                              "python_default")
            await client.async_update()

            response = client.data
            if response is not None:
                return json.loads(response)
            else:
                LOGGER.warning("Got no response from %s", path)

        except Exception as e:
            LOGGER.error("Failed to get and parse data from %s, %s", path, e)

        return None

    async def get_device_detail(self):
        path = '/op/v0/device/detail'
        query = {
            "sn": self._serial
        }
        # TODO improve error handling
        response = await self.request_data("GET", path, query, None)

        if response is not None:
            errno = response["errno"]
            if errno != 0:
                msg = response["msg"]
                LOGGER.error("Unexpected API response: %s, %s", errno, msg)
            else:
                return response["result"]
        else:
            LOGGER.warning("Got no response from %s", path)

    async def update_realtime_data(self):
        # TODO abort without serial
        path = '/op/v0/device/real/query'

        variables = list(
            map(lambda sensor: sensor.variable,
                filter(lambda sensor: sensor.variable is not None and sensor.realtime, SENSORS))
        )
        if len(variables) == 0:
            LOGGER.info("No realtime-data sensors, skipping update")
            return

        request_body_dict = {
            "sn": self._serial,
            "variables": variables
        }

        request_body = json.dumps(request_body_dict)
        response = await self.request_data("POST", path, None, request_body)

        if response is not None:
            errno = response["errno"]
            if errno != 0:
                msg = response["msg"]
                LOGGER.error("Unexpected API response: %s, %s", errno, msg)
            else:
                for device in response["result"]:
                    try:
                        date_str = device["time"]
                        timestamp = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %Z%z")
                        self.allData["last_update"] = timestamp
                    except ValueError:
                        LOGGER.warning("Could not parse last_update. If this error persists, check API for changes. "
                                       "(Current version is %s)", API_VERSION)
                    except KeyError:
                        LOGGER.warning("Could not get last_update. If this error persists, check API for changes. "
                                       "(Current version is %s)", API_VERSION)

                    for dataset in device["datas"]:
                        try:
                            variable = dataset["variable"]
                            if "value" in dataset:
                                value = dataset["value"]
                            else:
                                value = None
                            self.allData["realtime"][variable] = value
                        except KeyError:
                            LOGGER.warning(
                                "Could not parse dataset data. If this error persists, check API for changes. "
                                "(Current version is %s)", API_VERSION)

        else:
            LOGGER.warning(f"Got no data for realtime update. Check if API at {BASE_URL} is available and reachable.")

    async def update_report_data(self):
        # TODO abort without serial
        path = '/op/v0/device/report/query'
        today = datetime.now()
        year = today.year
        month = today.month
        day = today.day

        variables = list(
            map(lambda sensor: sensor.variable,
                filter(lambda sensor: sensor.variable is not None and sensor.realtime == False, SENSORS))
        )
        if len(variables) == 0:
            LOGGER.info("No report-data sensors, skipping update")
            return

        request_body_dict = {
            "sn": self._serial,
            "year": year,
            "month": month,
            "day": day,
            "dimension": "day",
            "variables": variables
        }
        request_body = json.dumps(request_body_dict)
        response = await self.request_data("POST", path, None, request_body)

        if response is not None:
            errno = response["errno"]
            if errno != 0:
                msg = response["msg"]
                LOGGER.error("Unexpected API response: %s, %s", errno, msg)
            else:
                for dataset in response["result"]:
                    try:
                        variable = dataset["variable"]
                        value_sum = 0.0
                        for value in dataset["values"]:
                            if value is not None:
                                value_sum += float(value)
                        self.allData["report"][variable] = round(value_sum, 3)
                    except KeyError:
                        LOGGER.warning("Could not parse dataset data. If this error persists, check API for changes. "
                                       "(Current version is %s)", API_VERSION)
        else:
            LOGGER.warning(f"Got no data for report update. Check if API at {BASE_URL} is available and reachable.")

    async def update_data(self):
        await self.update_realtime_data()
        await self.update_report_data()
        return self.allData
