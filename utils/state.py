import cPickle


def load(statefile):

    fd = open(statefile, "rb")
    data = cPickle.load(fd)
    fd.close()
    
    return data
    
    
def save(statefile, *args):

    try:
        fd = open(statefile, "wb")
    except:
        return
    try:
        cPickle.dump(args, fd, 2)
    finally:
        fd.close()

