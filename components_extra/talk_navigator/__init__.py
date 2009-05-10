import commands


def _have_flite():

    fail, out = commands.getstatusoutput("padsp espeak -h")
    if (fail):
        return False
    else:
        return True
    

def get_classes():

    if (_have_flite()):
        from TalkNavigator import TalkNavigator
        from Prefs import Prefs
        return [TalkNavigator, Prefs]
    else:
        return []



messages = [
    "TALKNAV_ACT_SAY",  # (text)
]
