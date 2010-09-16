from utils.Config import Config

import os


QUALITY_ASK = "ask"
QUALITY_HIGH = "high"
QUALITY_LOW = "low"


_cfg = Config("youtube", [
              ("cache-folder", Config.STRING, "/media/mmc1/.mediabox"),
              ("quality", Config.STRING, QUALITY_ASK),
              #("hi-quality", Config.BOOL, False),
              ("quality-type", Config.INTEGER, 0)
              ])


def set_cache_folder(path):

    _cfg["cache-folder"] = path
    
    
def get_cache_folder():

    return _cfg["cache-folder"]


def set_hi_quality(v):

    _cfg["hi-quality"] = v
    
    
def get_hi_quality():

    return _cfg["hi-quality"]


def set_quality_type(t):

    _cfg["quality-type"] = t
    
    
def get_quality_type():

    return _cfg["quality-type"]


def set_quality(q):

    _cfg["quality"] = q
    

def get_quality():

    return _cfg["quality"]

