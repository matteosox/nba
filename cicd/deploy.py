#! /usr/bin/env python3
"""Deploy app to Vercel"""

import logging
import os
import signal
import time

import requests
import yaml


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(pathname)s:%(funcName)s @ %(lineno)d | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
)
POLLING_PERIOD = 5
TIMEOUT = 45 * 60
ACCOUNT_TOKEN = os.environ["VERCEL_ACCOUNT_TOKEN"]
DEPLOY_HOOK_URL = os.environ["VERCEL_DEPLOY_HOOK_URL"]
PROJECT_ID = "prj_u9E8EAUMVH5JhnXa5S6eX3gQ86aF"


class Timeout:
    """Context manager, raises a TimeoutError after seconds"""

    def __init__(self, duration: int, retry_duration: int = 1):
        self.duration = duration
        self.retry_duration = retry_duration

    def __enter__(self):
        def handler(signal_num, curr_frame):  # pylint: disable=unused-argument
            signal.alarm(self.retry_duration)
            raise TimeoutError("{}s timeout".format(self.duration))

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(self.duration)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)


def main() -> None:
    """Deploy app to Vercel"""
    with Timeout(TIMEOUT):
        creation_timestamp = request_deploy()
        deployment_id = get_deployment_id(creation_timestamp)
        is_deployed(deployment_id)


def request_deploy() -> int:
    """Request a deploy using the deploy hook"""
    response = requests.get(DEPLOY_HOOK_URL)
    if response.status_code != 201:
        raise Exception(f"Received HTTP status code {response.status_code}")
    result = response.json()
    logger.info(
        f"Received the following JSON response from the Vercel deploy hook:\n{yaml.dump(result)}"
    )
    return result["job"]["createdAt"]


def get_deployment_id(timestamp: int) -> str:
    headers = {"Authorization": f"Bearer {ACCOUNT_TOKEN}"}
    params = {"limit": 1, "projectId": PROJECT_ID, "since": timestamp}
    while True:
        response = requests.get(
            "https://api.vercel.com/v6/deployments", params=params, headers=headers
        )
        result = response.json()
        logger.info(
            f"Received the following JSON response from the Vercel deployments API:\n{yaml.dump(result)}"
        )
        deployments = result["deployments"]
        if deployments:
            return deployments[0]["uid"]
        logger.info("No deployment found yet")
        time.sleep(POLLING_PERIOD)


def is_deployed(deployment_id: str) -> None:
    headers = {"Authorization": f"Bearer {ACCOUNT_TOKEN}"}
    while True:
        response = requests.get(
            f"https://api.vercel.com/v13/deployments/{deployment_id}", headers=headers
        )
        result = response.json()
        logger.info(
            f"Received the following JSON response from the Vercel deployment API:\n{yaml.dump(result)}"
        )
        state = result["readyState"]
        if state in {"ERROR", "CANCELED"}:
            raise Exception(f"Deployment failed, state is {state}")
        if state == "READY":
            logger.info("Deployment successful!")
            return
        time.sleep(POLLING_PERIOD)


if __name__ == "__main__":
    main()
