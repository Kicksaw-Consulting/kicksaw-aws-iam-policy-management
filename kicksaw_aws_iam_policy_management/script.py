import boto3
import json
import os

STAGE = os.getenv("STAGE")


def sync_iam():
    iam = boto3.client("iam")

    with open("config-iam.json") as file:
        json_data = json.load(file)

    namespace = json_data["namespace"]
    policies = json_data["policies"]
    iam_user_purpose = json_data["purpose"]

    stage_exists = bool(json_data.get("stages", {}).get(STAGE))

    if not stage_exists:
        if "stages" not in json_data:
            json_data["stages"] = dict()
        json_data["stages"][STAGE] = dict()

    user_exists = bool(json_data["stages"].get(STAGE, {}).get("arn"))

    policies_to_attach = list()
    policies_to_update = list()

    for policy in policies:
        description = policy.get("description")
        if "stages" not in policy:
            policy["stages"] = dict()
        if STAGE not in policy["stages"]:
            policy["stages"][STAGE] = dict()
        created = bool(policy["stages"][STAGE].get("arn"))

        if not created:
            path_to_policy = policy["path"]
            purpose = policy["purpose"]

            with open(path_to_policy) as file:
                policy_json = file.read()
            response = iam.create_policy(
                PolicyName=f"{namespace}-{purpose}",
                PolicyDocument=policy_json,
                Description=description,
            )
            arn = response["Policy"]["Arn"]
            policy["stages"][STAGE]["arn"] = arn
            policies_to_attach.append(arn)
        else:
            policies_to_update.append(policy)

    username = f"{namespace}-{iam_user_purpose}"

    access_key = None
    if not user_exists:
        response = iam.create_user(
            UserName=username,
        )
        arn = response["User"]["Arn"]
        json_data["stages"][STAGE]["arn"] = arn

        response = iam.create_access_key(UserName=username)
        access_key = response["AccessKey"]

    for policy_arn in policies_to_attach:
        iam.attach_user_policy(UserName=username, PolicyArn=policy_arn)
    for policy in policies_to_update:
        policy_arn = policy["stages"][STAGE]["arn"]
        results = iam.list_policy_versions(PolicyArn=policy_arn)
        versions = results["Versions"]
        for idx, version in enumerate(versions):
            version_id = version["VersionId"]
            if idx == 4:
                iam.delete_policy_version(PolicyArn=policy_arn, VersionId=version_id)

        with open(policy["path"]) as file:
            policy_json = file.read()
        response = iam.create_policy_version(
            PolicyArn=policy_arn, PolicyDocument=policy_json, SetAsDefault=True
        )

    with open("config-iam.json", "w") as file:
        json.dump(json_data, file, indent=2)

    return access_key
