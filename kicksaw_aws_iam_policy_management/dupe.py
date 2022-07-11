import json

from logging import getLogger

logger = getLogger(__name__)


def duplicate_stage(source, target):
    with open("config-iam.json") as file:
        json_data = json.load(file)

    json_data["stages"][target] = json_data["stages"][source]

    for policy in json_data["policies"]:
        if target in policy["stages"]:
            logger.warning(f"{target} already exists. Overwriting")

        policy["stages"][target] = policy["stages"][source]

    with open("config-iam.json", "w") as file:
        json.dump(json_data, file, indent=2)
