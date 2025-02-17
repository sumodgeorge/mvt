# Mobile Verification Toolkit (MVT)
# Copyright (c) 2021-2023 Claudio Guarnieri.
# Use of this software is governed by the MVT License 1.1 that can be found at
#   https://license.mvt.re/1.1/

import logging
from typing import Optional

from mvt.android.parsers import parse_dumpsys_accessibility

from .base import AndroidQFModule


class DumpsysAccessibility(AndroidQFModule):
    """This module analyse dumpsys accessbility"""

    def __init__(
        self,
        file_path: Optional[str] = None,
        target_path: Optional[str] = None,
        results_path: Optional[str] = None,
        fast_mode: bool = False,
        log: logging.Logger = logging.getLogger(__name__),
        results: Optional[list] = None,
    ) -> None:
        super().__init__(
            file_path=file_path,
            target_path=target_path,
            results_path=results_path,
            fast_mode=fast_mode,
            log=log,
            results=results,
        )

    def check_indicators(self) -> None:
        if not self.indicators:
            return

        for result in self.results:
            ioc = self.indicators.check_app_id(result["package_name"])
            if ioc:
                result["matched_indicator"] = ioc
                self.detected.append(result)

    def run(self) -> None:
        dumpsys_file = self._get_files_by_pattern("*/dumpsys.txt")
        if not dumpsys_file:
            return

        lines = []
        in_accessibility = False
        with open(dumpsys_file[0]) as handle:
            for line in handle:
                if line.strip().startswith("DUMP OF SERVICE accessibility:"):
                    in_accessibility = True
                    continue

                if not in_accessibility:
                    continue

                if line.strip().startswith(
                    "-------------------------------------------------------------------------------"
                ):  # pylint: disable=line-too-long
                    break

                lines.append(line.rstrip())

        self.results = parse_dumpsys_accessibility("\n".join(lines))

        for result in self.results:
            self.log.info(
                'Found installed accessibility service "%s"', result.get("service")
            )

        self.log.info(
            "Identified a total of %d accessibility services", len(self.results)
        )
