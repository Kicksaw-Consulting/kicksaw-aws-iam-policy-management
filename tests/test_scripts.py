import json

from moto import mock_iam

from kicksaw_aws_iam_policy_management.script import sync_iam

USER_ARN = "arn:aws:iam::123456789012:user/example-project-cicd"
POLICY_ARN = "arn:aws:iam::123456789012:policy/example-project-deploy"


@mock_iam
def test_sync_iam():
    # first-time run should create arn
    sync_iam()

    with open("config-iam.json") as file:
        data = json.load(file)

    assert data["stages"]["test"]["arn"] == USER_ARN
    assert data["policies"][0]["stages"]["test"]["arn"] == POLICY_ARN

    # then just make sure it runs again
    sync_iam()
