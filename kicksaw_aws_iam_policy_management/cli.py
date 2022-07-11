import click

from kicksaw_aws_iam_policy_management.dupe import duplicate_stage
from kicksaw_aws_iam_policy_management.script import sync_iam


@click.group("iam-mgmt", chain=True)
def iam_mgmt(**kwargs):
    pass


@iam_mgmt.command("sync")
def sync():
    sync_iam()


@iam_mgmt.command("dupe")
@click.argument("source")
@click.argument("target")
def dupe(source, target):
    duplicate_stage(source, target)
