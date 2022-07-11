import json
import os

from moto import mock_iam

from kicksaw_aws_iam_policy_management.dupe import duplicate_stage
from kicksaw_aws_iam_policy_management.script import sync_iam

USER_ARN = "arn:aws:iam::123456789012:user/example-project-cicd"
POLICY_ARN = "arn:aws:iam::123456789012:policy/example-project-deploy"

STAGE = os.getenv("STAGE")
TARGET_STAGE = "production"


@mock_iam
def test_sync_iam():
    # first-time run should create arn
    sync_iam()

    with open("config-iam.json") as file:
        data = json.load(file)

    assert data["stages"][STAGE]["arn"] == USER_ARN
    assert data["policies"][0]["stages"][STAGE]["arn"] == POLICY_ARN

    # then just make sure it runs again
    sync_iam()

    # and check the stage duplication stuff works
    duplicate_stage(STAGE, "production")

    with open("config-iam.json") as file:
        data = json.load(file)

    # check the original is still there
    assert data["stages"][STAGE]["arn"] == USER_ARN
    assert data["policies"][0]["stages"][STAGE]["arn"] == POLICY_ARN
    # check the target got copied
    assert data["stages"][TARGET_STAGE]["arn"] == USER_ARN
    assert data["policies"][0]["stages"][TARGET_STAGE]["arn"] == POLICY_ARN
