
from pyharmony import client as harmony_client
from pyharmony import discovery as harmony_discovery
import argparse
import json
import logging
import asyncio
import sys
import time

logger = logging.getLogger(__name__)

activities_by_name = {}
activities_by_id = {}
devices = {}

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
    func = harmony_client.create_and_connect_client(ip, port, activity_change)
    return run_in_loop_now('get_client', func)

def get_config(client):
    """Connects to the Harmony and generates a dictionary containing all activites and commands programmed to hub.

    Args:
        ip (str): Harmony hub IP address
        port (str): Harmony hub port

    Returns:
        Dictionary containing Harmony device configuration
    """
    func = client.get_config()
    config = run_in_loop_now('get_config', func)

    a = {}
    b = {}
    for i in config['activity']:
        a[i['label']] = i['id']
        b[i['id']] = i['label']
    activities_by_name = a
    activities_by_id = b
    d = {}
    for device in config['device']:
        device_cmds = []
        for grp in device['controlGroup']:
            for fnc in grp['function']:
                device_cmds.append(json.loads(fnc['action'])['command'])
        d[device['label']] = {"id": device['id'],
                              "cmds": device_cmds}
    devices = d
    return config

def get_current_activity(client):
    """Connects to the Harmony and gets current activity.
    String is returned

    Args:
        client (obj): Harmony client object

    Returns:
        String containing activity label
    """
    func = client.get_current_activity()
    activity_id = run_in_loop_now('get_current_activity', func)
    label = activities_by_id[str(activity_id)]
    return label

def set_current_activity(client, activity_label):
    """Connects to the Harmony and sets current activity.

    Args:
        client (obj): Harmony client object

    Returns:
        String containing activity label
    """

    id = activities_by_name[activity_label]
    func = client.start_activity(id)
    status = run_in_loop_now('start_activity', func)
    return status

def send_command(client, device_label, device_command, device_hold_secs=0):
    """Connects to the Harmony and send a simple command.

    Args:
        args (argparse): Argparse object containing required variables from command line

    """
    device_id = devices[device_label]['id']
    func = client.send_command(device_id, device_command, device_hold_secs)
    run_in_loop_now('send_command', func)
    print("Sent: " + device_command + " to " + device_label)
    return

def activity_change(activity_id):
    """Handles callback from pyharmony

    Args:
        activity_id - ID of current activity

    """
    print("Callback:" + str(activity_id))

