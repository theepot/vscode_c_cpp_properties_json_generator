#!/usr/bin/env python3

import sys
import os
import argparse
import json
import shlex
from typing import Dict, List


PROGRAM_DESCRIPTION = """
TODO program description :(
"""


def main():
    # parse args.
    args = parse_args()

    # load exists tasks (if any).
    tasks = try_update_tasks(args)
    if tasks is not None:
        print(f"Updating existing tasks file.")
    else:
        print(f"Creating new tasks file.")
        tasks = [ generate_task_json(args)]  

    # overwrite existing file.
    create_tasks_file(args, tasks)


def parse_args():
    argParser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)

    # argument descriptions
    argParser.add_argument("--file", help="Path to new or existing tasks file.")
    argParser.add_argument("--label", help="Label of the tasks. If a task with the same label exists, it will be overwritten.")
    argParser.add_argument("--make_cmd", help="Path to make command.")

    # parse
    args =  argParser.parse_args()

    # some checking
    def mandatory(cmd):
        if vars(args)[cmd] is None:
            eprint(f"Error: {cmd} is manfatory.")
            exit(1)

    mandatory("file")
    mandatory("label")
    mandatory("make_cmd")

    # return
    return args


def try_update_tasks(args):
    if not os.path.exists(args.file.strip()):
        print(f"DEBUG: path {args.file} does not exist")
        return None

    try:    
        with open(args.file, "r") as f:
            json_root = json.load(f)

            # calid tasks file should contain a 'tasks' attribute.        
            if "tasks" not in json_root:
                eprint(f"ERROR: expected 'tasks' attribute in {args.file}")
                exit(1)
            tasks = json_root["tasks"]

            # generate actual task JSON.
            task = generate_task_json(args)
            # if a task exists with our label, replace it.
            task_index = find_task_index_by_label(tasks, args.label)
            if task_index is None:
                tasks.append(task)
            else:
                tasks[task_index] = task
            
            # return with success.
            return tasks

    except IOError as ex:
        eprint(f"Unexpected error when updating tasks file {args.file},")
        eprint(f"namely: {ex}.")
        exit(1)


def create_tasks_file(args, tasks):
    try:
        json_root = {
            "version": "2.0.0",
            "tasks": tasks
        }

        with open(args.file, "w") as f:    
            json.dump(json_root, f, indent=4)

    except IOError as ex:
        eprint(f"Unexpected error when updating tasks file {args.file},")
        eprint(f"namely: {ex}.")
        exit(1)


def generate_task_json(args):
    return {
        "type": "shell",
        "label": args.label,
        "command": args.make_cmd,
        "args": ["all"],
        # TODO should maybe add `options` thing.
        "problemMatcher": ["$gcc"],
        "group": {
            "kind": "build",
            "isDefault": True
        }
    }


def find_task_index_by_label(tasks : List[Dict], target_label : str):
    for i in range(len(tasks)):
        if "label" in tasks[i] and tasks[i]["label"] == target_label:
            return i
    return None

def eprint(s):
    print(s, file=sys.stderr)


if __name__ == "__main__":
    main()
