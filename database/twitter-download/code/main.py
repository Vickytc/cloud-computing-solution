"""
Script Name: main.py
Description: This script demonstrates how to process a twitter file with MPI4PY.
Authors:
    Ze Pang (955698) 
Usage:
    python3 main.py twitter-100gb
"""

import os
import json
import argparse
import datetime
import logging

from collections import Counter


# import typing for readability and maintenance
from typing import (
    DefaultDict,
    Tuple,
    List,
    Dict,
    Union
    )

# import configs
from config import (
    RESULTS_DIR,
    DATA_DIR,
    LOGS_DIR
    )

# import TweetProcess class defined in tweet_process.py
from tweet_process import TweetProcess, bin2str


from mpi4py import MPI


# use logger for debugging and tracking the process
log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
logging.basicConfig(filename=os.path.join(LOGS_DIR, log_filename), 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_twitter_file_info() -> Tuple[str, str, int]:
    """
    Read the input filename and get ready for later process.

    Raises:
        Exception: The input filename should in ["twitter-100gb", "twitter-50mb", "twitter-1mb"]

    Returns:
        Tuple[str, str, int]: A tuple contains filename, filepath and size of file
    """
    # parsing command-line argument "filename" with argparse
    parser = argparse.ArgumentParser(description="the twitter filename")
    parser.add_argument("filename", type=str, help="")
    args = parser.parse_args()
    tw_filename = args.filename

    # check if filename is valid
    if tw_filename not in ["twitter-100gb", "twitter-50mb", "twitter-1mb"]:
        raise Exception("Error: the input filename is not valid!")

    # then obtain the filepath, file_size
    tw_filepath = os.path.join(DATA_DIR, f"{tw_filename}.json")
    tw_file_size = os.stat(tw_filepath).st_size
    return tw_filename, tw_filepath, tw_file_size


def get_search_pos_range(tw_file_size: int,
                         process_size: int,
                         process_rank: int) -> Tuple[int, int]:
    """
    For each worker, find the search range of file. 
    Different workers should process different segments.

    Args:
        tw_file_size (int): file size of twitter file
        process_size (int): MPI number of workers
        process_rank (int): MPI current worker rank

    Returns:
        Tuple[int, int]: A search range tuple
    """
    file_size_per_process= tw_file_size // process_size
    min_search_pos = file_size_per_process * process_rank
    max_search_pos = file_size_per_process * (process_rank + 1)
    # last worker needs to read until end of file
    if process_rank == (process_size - 1):
        max_search_pos = tw_file_size
    return min_search_pos, max_search_pos


def merge_dicts(list_of_dict: List[DefaultDict]) -> Dict[str, Union[int, float]]:
    """
    Merge result dictionaries from different workers and return the key-value pair.

    Args:
        list_of_dict (List[DefaultDict]): A list of dictionaries

    Returns:
        Dict[str, Union[int, float]]: A dictionary with only 1 key-value pair where value is the largest.
    """
    merged_dict = Counter()
    for d in list_of_dict:
        merged_dict.update(d)
    key_w_max_val = max(merged_dict, key=merged_dict.get)
    return {bin2str(key_w_max_val):merged_dict[key_w_max_val]}


def save_dict(tw_filename: str, result_filename: str, final_list: List) -> None:
    """
    Save dictionary to json file.

    Args:
        tw_filename (str): twitter file name 
        result_filename (str): file name of json file
        result_dict (Dict): dictionary object
    """
    with open(os.path.join(RESULTS_DIR, tw_filename, result_filename),
              'w', encoding='utf-8') as json_file:
        for item in final_list:
            json.dump(item, json_file)
            json_file.write("\n")


def main() -> None:
    """
    Main code for reading and processing twitter file with MPI4PY
    """
    # MPI initialization
    comm = MPI.COMM_WORLD
    process_size = comm.Get_size()
    process_rank = comm.Get_rank()

    # get twitter file info
    tw_filename, tw_filepath, tw_file_size = get_twitter_file_info()
    logger.info("the worker=%s has read %s.json (file_size=%s) successfully!", process_rank, tw_filename, tw_file_size)

    # assign jobs to each worker
    min_search_pos, max_search_pos = get_search_pos_range(tw_file_size, process_size, process_rank)
    logger.info("the search range for worker=%s is (%s, %s)", process_rank, min_search_pos, max_search_pos)

    # start processing
    tp = TweetProcess(tw_filepath, min_search_pos, max_search_pos)
    results = tp.process()
    logger.info("the subtask for worker=%s has finished!", process_rank)

    # gather result dictionaries from different workers
    results_list = comm.gather(results, root=0)
    if process_rank == 0:
        logger.info("results gathered to master!")
        final_list = []
        for lst in results_list:
            final_list += lst
        save_dict(tw_filename, "twitter.jsonl", final_list)

        logger.info("results have been saved successfully!")

    # Finalize MPI
    MPI.Finalize()

if __name__=="__main__":
    main()
