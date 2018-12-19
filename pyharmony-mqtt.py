
from pyharmony import client as harmony_client
from pyharmony import discovery as harmony_discovery
import argparse
import json
import logging
import asyncio
import sys
import time

logger = logging.getLogger(__name__)

def run_in_loop_now(name, func):
    # Get current loop, creates loop if none exist.
    loop = asyncio.get_event_loop()

    func_task = asyncio.ensure_future(func)
    if loop.is_running():
        # We're in a loop, task was added and we're good.
        logger.debug("Task %s added to loop", name)
        return func_task

    # We're not in a loop, execute it.
    logger.debug("Executing task %s", name)
    loop.run_until_complete(func_task)
    return func_task.result()

def get_client(ip, port=None, activity_callback=None):
    """Connect to the Harmony and return a Client instance.

    Args:
        harmony_ip (str): Harmony hub IP address
        harmony_port (str): Harmony hub port
        activity_callback (function): Function to call when the current activity has changed.

    Returns:
        object: Authenticated client instance.
    """
    func = harmony_client.create_and_connect_client(ip, port,
                                                    activity_callback)
    return run_in_loop_now('get_client', func)