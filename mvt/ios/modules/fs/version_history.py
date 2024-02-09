# Mobile Verification Toolkit (MVT)
# Copyright (c) 2021-2023 The MVT Authors.
# Use of this software is governed by the MVT License 1.1 that can be found at
#   https://license.mvt.re/1.1/

import datetime
import json
import logging
from typing import Optional, Union

from mvt.common.utils import convert_datetime_to_iso

from ..base import IOSExtraction

IOS_ANALYTICS_JOURNAL_PATHS = [
    "private/var/db/analyticsd/Analytics-Journal-*.ips",
]


class IOSVersionHistory(IOSExtraction):
    """This module extracts iOS update history from Analytics Journal log files."""

    def __init__(
        self,
        file_path: Optional[str] = None,
        target_path: Optional[str] = None,
        results_path: Optional[str] = None,
        module_options: Optional[dict] = None,
        log: logging.Logger = logging.getLogger(__name__),
        results: Optional[list] = None,
        """This function initializes the class with optional parameters for file path, target path, results path, module options, logger, and results list.
        Parameters:
            - file_path (str): Path to the file to be processed.
            - target_path (str): Path to the target directory for the processed file.
            - results_path (str): Path to the directory where results will be saved.
            - module_options (dict): Optional dictionary of module options.
            - log (logging.Logger): Optional logger for logging messages.
            - results (list): Optional list to store results.
        Returns:
            - None: This function does not return anything.
        Processing Logic:
            - Initialize class with optional parameters.
            - Set default values for optional parameters if not provided.
            - Use logger to log messages.
            - Store results in results list if provided."""
        
    ) -> None:
        super().__init__(
            file_path=file_path,
            target_path=target_path,
            results_path=results_path,
            module_options=module_options,
            log=log,
            results=results,
        )

    def serialize(self, record: dict) -> Union[dict, list]:
        """Function: Serialize record into a dictionary with timestamp, module, event, and data.
        Parameters:
            - record (dict): Dictionary containing record data.
        Returns:
            - Union[dict, list]: Dictionary with timestamp, module, event, and data.
        Processing Logic:
            - Serialize record into dictionary.
            - Record timestamp as "isodate".
            - Record module as class name.
            - Record event as "ios_version".
            - Record data as "Recorded iOS version" + record['os_version'].
        Example:
            record = {"isodate": "2021-07-12", "os_version": "14.6"}
            serialize(record) -> {"timestamp": "2021-07-12", "module": "serialize", "event": "ios_version", "data": "Recorded iOS version 14.6"}"""
        
        return {
            "timestamp": record["isodate"],
            "module": self.__class__.__name__,
            "event": "ios_version",
            "data": f"Recorded iOS version {record['os_version']}",
        }

    def run(self) -> None:
        for found_path in self._get_fs_files_from_patterns(IOS_ANALYTICS_JOURNAL_PATHS):
        """"""
        
            with open(found_path, "r", encoding="utf-8") as analytics_log:
                log_line = json.loads(analytics_log.readline(5_000_000).strip())

                timestamp = datetime.datetime.strptime(
                    log_line["timestamp"], "%Y-%m-%d %H:%M:%S.%f %z"
                )
                timestamp_utc = timestamp.astimezone(datetime.timezone.utc)
                self.results.append(
                    {
                        "isodate": convert_datetime_to_iso(timestamp_utc),
                        "os_version": log_line["os_version"],
                    }
                )

        self.results = sorted(self.results, key=lambda entry: entry["isodate"])
