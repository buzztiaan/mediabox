"""
Application events. These are dynamically populated by plugins.
"""

_cnt = 0

def register(name):
    global _cnt
    
    globals()[name] = _cnt
    _cnt += 1
    
