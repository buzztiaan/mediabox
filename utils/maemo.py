"""
Module for maemo-specific stuff.
"""


def get_product_code():
    """
    Returns the product code.
    Nokia 770:  SU-18
    Nokia N800: RX-34
    Nokia N810: RX-44
    Unknown:    ?
    """
    
    try:
        lines = open("/proc/component_version", "r").readlines()
    except:
        lines = []
        
    product = "?"
    for line in lines:
        line = line.strip()
        if (line.startswith("product")):
            parts = line.split()
            product = parts[1].strip()
            break
    #end for
    
    return product
