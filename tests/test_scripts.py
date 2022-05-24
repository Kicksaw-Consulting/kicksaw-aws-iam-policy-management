from moto import mock_iam

from kicksaw_aws_iam_policy_management.script import sync_iam


@mock_iam
def test_new():
    sync_iam()
