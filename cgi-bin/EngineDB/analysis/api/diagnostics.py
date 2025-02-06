#!../../cgi_runner.sh

import abc
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

import pandas as pd
from pydantic import BaseModel, TypeAdapter

base_url = "http://cmslab1.spa.umn.edu/Factory/EngineDB/analysis/api/board_report.py"
args = {
    "subtypes": ["EL10W1", "EL10E1"],
    "include_attach": ["ADC funcctionality", "Eye Opening", "Current Draw", "X_PWR"],
}


class ParsedResult(BaseModel):
    primary_category: str
    secondary_category: str = None
    data: Any = None


result_adapter = TypeAdapter(dict[str, list[ParsedResult]])


class Analyzer(abc.ABC):
    test_name = None

    @abc.abstractmethod
    def run(self, comment, data=None):
        pass

    def __call__(self, test_states):
        if test_states[self.test_name]["test_state"] == "FAILED":
            comment = test_states[self.test_name]["test_comment"]
            return self.run(comment)
        else:
            return None


ALL_CHECKS = defaultdict(list)


def register(rank):
    def inner(cls):
        ALL_CHECKS[rank].append(cls())

    return inner


def makeExceptionTest(test_name, primary_category):
    def run(self, comment):
        if "exception" in comment:
            return ParsedResult(
                primary_category=primary_category,
                secondary_category="EXCEPTION",
                data=None,
            )

    return register(3)(
        type(
            f"CheckException{primary_category}",
            (Analyzer,),
            {"run": run, "test_name": test_name},
        )
    )


@register(3)
class ADCResistance(Analyzer):
    test_name = "ADC functionality"

    def run(self, comment):
        reasons = {}
        for m in re.finditer(r"incorrect resistance (\w+)=([+\-]?\d+\.?\d*)", comment):
            reasons[m[1]] = float(m[2])
        if not reasons:
            return
        return ParsedResult(
            primary_category="ADC_FUNCTIONALITY",
            secondary_category="BAD_RESISTANCE",
            data=reasons,
        )


@register(3)
class ADCLinearity(Analyzer):
    test_name = "ADC functionality"

    def run(self, comment):
        if "linearity" not in comment:
            return
        return ParsedResult(
            primary_category="ADC_FUNCTIONALITY",
            secondary_category="BAD_LINEARITY",
            data=None,
        )


@register(3)
class ADCInternal(Analyzer):
    test_name = "ADC functionality"

    def run(self, comment):
        reasons = {}
        for m in re.finditer(
            r"Internal voltage (\w+) failed with value (\d+\.\d+)", comment
        ):
            reasons[m[1]] = float(m[2])
        if not reasons:
            return
        return ParsedResult(
            primary_category="ADC_FUNCTIONALITY",
            secondary_category="BAD_INTERNAL",
            data=reasons,
        )


@register(3)
class ADCTemperature(Analyzer):
    test_name = "ADC functionality"

    def run(self, comment):
        reasons = {}
        for m in re.finditer(r"Failed temperature (\w+) = ([+\-]?\d+\.\d+)C", comment):
            reasons[m[1]] = float(m[2])
        if not reasons:
            return
        return ParsedResult(
            primary_category="ADC_FUNCTIONALITY",
            secondary_category="BAD_TEMPERATURE",
            data=reasons,
        )


@register(3)
class CheckEyeArea(Analyzer):
    test_name = "Eye Opening"

    def run(self, comment):
        reasons = {}
        for m in re.finditer(
            r"Bad eye opening area (\d+\.?\d*) on LPGBT (\w+)", comment
        ):
            reasons[m[2]] = float(m[1])
        if not reasons:
            return ParsedResult(
                primary_category="EYE_OPENING", secondary_category="GENERAL", data=None
            )
        return ParsedResult(
            primary_category="EYE_OPENING", secondary_category="BAD_AREA", data=reasons
        )


@register(3)
class CheckThermal(Analyzer):
    test_name = "Thermal Cycle"

    def run(self, comment):
        return ParsedResult(
            primary_category="THERMAL_FAILED",
            secondary_category="THERMAL_FAILED",
            data=None,
        )


@register(1)
class CheckXPWRCurrent(Analyzer):
    test_name = "X_PWR"

    def run(self, comment):
        reasons = {}
        for m in re.finditer(r"Measured bad (\w+) current (\d+\.\d+)", comment):
            reasons[m[1]] = float(m[2])
        if not reasons:
            return
        return ParsedResult(
            primary_category="BAD_PRE_POWER",
            secondary_category="BAD_CURRENT",
            data=reasons,
        )


@register(3)
class CheckI2CCount(Analyzer):
    test_name = "I2C"

    def run(self, comment):
        reasons = {}
        for m in re.finditer(r"Nonzero error count on lpgbt (\w+), bus (\d+)", comment):
            reasons[(m[1], int(m[2]))] = {}
        if not reasons:
            return
        return ParsedResult(
            primary_category="I2C_FUNCTIONALITY",
            secondary_category="BAD_I2C_ERROR",
            data=reasons,
        )


@register(2)
class CheckSetup(Analyzer):
    test_name = "lpGBT setup"

    def run(self, comment):
        return ParsedResult(
            primary_category="SETUP_FAILED",
            secondary_category="SETUP_FAILED",
            data=None,
        )


def deduceFailure(board):
    test_states = board["test_status"]
    rank_checks = sorted(list(ALL_CHECKS.items()), key=lambda x: x[0])
    for rank, checks in rank_checks:
        results = [check(test_states) for check in checks]
        results = [x for x in results if x is not None]
        if results:
            return results


save_path = "output.json"


makeExceptionTest("ADC functionality", "ADC_FUNCTIONALITY")
makeExceptionTest("I2C", "I2C_FUNCTIONALITY")


def main():
    print("Content-Type: application/json\n\n")
    # p = Path(save_path)
    # if not p.exists():
    #     js = data.text
    #     with open(p, "w") as f:
    #         f.write(js)
    #
    # with open(p, "r") as f:
    #     data = json.load(f)
    data = requests.get(base_url, params=args).json()

    ret = {}
    # data = {x: y for x, y in data.items() if x not in DROP_BOARDS}
    for fid, board_data in data.items():
        board_data["qc_states"]
        if any(x["test_state"] == "FAILED" for x in board_data["test_status"].values()):
            ret[fid] = deduceFailure(board_data)

    print(result_adapter.dump_json(ret).decode("utf-8"))


if __name__ == "__main__":
    main()
