"""
Script Name: tweet_process.py
Description: This script demonstrates how to process a twitter file for each worker.
Authors:
    Ze Pang (955698) 
"""

import io
import re

from typing import (
    List,
    Dict,
)



# define regular expression patterns
ID_PATTERN = rb'"id":"(\d{19})","key":'
TEXT_PATTERN = rb'"value":{"text":"(.*?)"},"doc":{"'
TIME_PATTERN = rb'"created_at":"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.[\d]+Z)"'
LANG_PATTERN = rb'"lang":"(.*?)"'

GEO_PATTERN = rb'"bbox":\[(.*?),(.*?),(.*?),(.*?)\]'
# SENT_PATTERN = rb'"sentiment":(-?\d+\.?\d*)'
COMB_PATTERN = re.compile(b"|".join([ID_PATTERN,TEXT_PATTERN, TIME_PATTERN,LANG_PATTERN, GEO_PATTERN]))


def bin2str(data: bytes) -> str:
    """
    Convert data from bytes to string.

    Args:
        data (bytes): Input bytes data

    Returns:
        str: Outputs as a string 
    """
    return data.decode('utf-8')


class TweetProcess:
    """
    TweetProcess is a class used to read and process the twitter file.
    """
    def __init__(
            self,
            filepath: str,
            min_search_pos: int,
            max_search_pos: int
            ) -> None:
        """
        Initialize the class

        Args:
            filepath (str): twitter file path
            min_search_pos (int): minimum search position for a worker
            max_search_pos (int): maximum search position for a worker
        """
        # every time each workder reads and processes 2**30 bytes of file
        self.batch_size = 2**30
        self.filepath = filepath
        self.min_search_pos = min_search_pos
        self.max_search_pos = max_search_pos
        # initialize result dictionaries
        self.dict_list = []



    def process_chunk(self, chunk: bytes) -> None:
        """
        After reading file with binary mode, then process with chunks. 
        Apply regular expression to find time and sentiment information.
        Then add these information to result dictionaries.

        Args:
            chunk (bytes): Input bytes chunk of twitter file

        Raises:
            Exception: when matched tuple is not valid
        """
        # update 4 dictionaries using the searched data
        searched_data_list = COMB_PATTERN.findall(chunk)
        
        for i in range(len(searched_data_list)):
            if searched_data_list[i][4]:
                try:
                    self.dict_list.append({
                        "id":searched_data_list[i-4][0].decode('utf-8'),
                        "text":searched_data_list[i-3][1].decode('utf-8'),
                        "time":searched_data_list[i-2][2].decode('utf-8'),
                        "lang":searched_data_list[i-1][3].decode('utf-8'),
                        "p1":searched_data_list[i][4].decode('utf-8'),
                        "p2":searched_data_list[i][5].decode('utf-8'),
                        "p3":searched_data_list[i][6].decode('utf-8'),
                        "p4":searched_data_list[i][7].decode('utf-8'),
                    })
                except:
                    continue
        return
    
    

    def process(self) -> List[Dict]:
        """
        Read the twitter file as binary mode, find the minimum search position for each worker.
        Then batched the data and process it with process_chunk() function

        Returns:
            List[Dict]: The result dictionaries.
        """
        # read file in binary mode, different workers read different segments of file
        with io.open(self.filepath, 'rb') as file:
            file.seek(self.min_search_pos)
            # iteratively read and process each segment by chunks
            while file.tell() < self.max_search_pos:
                chunk = file.read(min(self.batch_size, self.max_search_pos - file.tell()))
                self.process_chunk(chunk)
        return self.dict_list