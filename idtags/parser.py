import base64

def _read_int(bytes):

    i = 0
    for b in bytes: i = (i << 8) + ord(b)
    return i
    

def parse_metadata_block_picture(data):

    idx = 0

    # skip type
    idx += 4
    
    # MIME type
    mime_len = _read_int(data[idx:idx + 4])
    idx += 4
    mimetype = data[idx:idx + mime_len]
    idx += mime_len
    
    # description
    descr_len = _read_int(data[idx:idx + 4])
    idx += 4
    descr = data[idx:idx + descr_len]
    idx += descr_len
    
    # skip size
    idx += 8
    
    # skip color stuff
    idx += 8
    
    # picture data
    pic_len = _read_int(data[idx:idx + 4])
    idx += 4
    pic_data = data[idx:idx + pic_len]
    
    try:
        return base64.b64decode(pic_data)
    except:
        return ""

    

