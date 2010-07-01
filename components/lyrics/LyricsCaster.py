from com import Component, msgs
from utils import logging

import os
import gobject


class LyricsCaster(Component):
    """
    Component for casting lyrics from LRC files. Other components may catch
    the lyrics and display them.
    """

    def __init__(self):
    
        # lyrics as list of (time, text, hilight_from, hilight_to) tuples
        self.__lyrics = []
        
        # time offset
        self.__offset = 0
        
        # current lyrics line
        self.__current_line = ""
        
        self.__position_handler = None
        self.__position = 0
    
        Component.__init__(self)
        
        
    def handle_MEDIA_EV_LOADED(self, v, f):
    
        self.__clear_lyrics()
        self.__find_lyrics(f)


    def handle_MEDIA_EV_PLAY(self):            

        if (self.__lyrics):
            if (self.__position_handler):
                gobject.source_remove(self.__position_handler)
            self.__position_handler = gobject.timeout_add(
                                                    100, self.__check_position)
            self.__position = 0

            
    def handle_MEDIA_EV_PAUSE(self):

        if (self.__position_handler):
            gobject.source_remove(self.__position_handler)


    def handle_MEDIA_EV_EOF(self):

        if (self.__position_handler):
            gobject.source_remove(self.__position_handler)


    def handle_MEDIA_EV_POSITION(self, pos, total):
        
        if (self.__lyrics):
            self.__position = pos * 1000


    def __check_position(self):
        
        self.__cast_lyrics(self.__position)
        self.__position += 100
        return True

            
    def __cast_lyrics(self, pos):
        """
        Finds the lyrics for the given position in milliseconds and casts it if
        it isn't the current one.
        """

        # we go through the whole list of lyric lines every time because
        # otherwise it would be hard to find the right line after a seek back
        # operation
        found = False
        for i in range(len(self.__lyrics)):
            a = self.__lyrics[i]
            if (i + 1 < len(self.__lyrics)):
                b = self.__lyrics[i + 1]
            else:
                b = a

            ts1, words, hi_from, hi_to = a
            ts2 = b[0]
            
            #print ts1, pos - self.__offset, ts2, words
            if (ts1 <= pos - self.__offset < ts2):
                found = True
                if ((words, hi_from, hi_to) != self.__current_line):
                    self.emit_message(msgs.MEDIA_EV_LYRICS,
                                        words, hi_from, hi_to)
                    logging.debug("lyrics: %d: %s", ts1, words)
                    self.__current_line = (words, hi_from, hi_to)
                #end if
                break
            #endif
        #end for
        
        if (not found and self.__current_line != ("", 0, 0)):
            self.__current_line = ("", 0, 0)
            self.emit_message(msgs.MEDIA_EV_LYRICS, "", 0, 0)
        
            
    def __clear_lyrics(self):
        """
        Clears the currently loaded lyrics.
        """
        
        self.__offset = 0
        self.__lyrics = []
        self.__current_line = None
            
            
    def __find_lyrics(self, f):
        """
        Looks for a LRC file for the given media file and loads it if one was
        found.
        """
        
        # only handle local files
        if (f.resource.startswith("/")):
            path, ext = os.path.splitext(f.resource)
            lrc_path = path + ".lrc"
            
            if (os.path.isfile(lrc_path)):
                self.__load_lyrics(lrc_path)
        #end if
        
        
    def __load_lyrics(self, lrc_path):
        """
        Loads the given LRC file.
        """
        
        try:
            data = self.__decode(open(lrc_path).read())
            lines = data.splitlines()
        except:
            logging.error("error loading lyrics file '%s'\n%s",
                          lrc_path, logging.stacktrace())
            lines = []
            
        for line in lines:
            self.__parse_line(line)
        self.__lyrics.sort(lambda a,b:cmp(a[0],b[0]))
        #print self.__lyrics
            
            
    def __parse_line(self, line):
        """
        Parses the given LRC line.
        """
        
        line = line.strip()
        if (line and line[0] == "["):
            idx = line.find("]")
            tag = line[1:idx]
            idx = tag.find(":")
            ttype = tag[:idx]
            tvalue = tag[idx + 1:]
            
            if (ttype == "ti"):
                # song title
                pass
                
            elif (ttype == "ar"):
                # lyrics artist
                pass
                
            elif (ttype == "au"):
                # author
                pass
                
            elif (ttype == "al"):
                # album where the song is from
                pass
                
            elif (ttype == "by"):
                # creator of the LRC file
                pass
                
            elif (ttype == "la"):
                # language of lyrics
                pass
                
            elif (ttype == "re"):
                # player or editor that created the LRC file
                pass
                
            elif (ttype == "sr"):
                # source of lyrics
                pass
                
            elif (ttype == "ve"):
                # version of program
                pass
                
            elif (ttype == "offset"):
                # overall timestamp adjustment in milliseconds
                self.__offset = int(tvalue)

            elif (ttype.isdigit()):
                # lyrics
                timetags, text = self.__parse_timetags(line)
                for t in timetags:
                    timestamp = self.__make_timestamp(t)
                    self.__parse_text(timestamp, text)
                #end for
                
                
    def __parse_timetags(self, line):
        """
        Returns the timetags of the given line. This allows handling of
        multiple timetags per line.
        """
        
        timetags = []
        pos = 0
        text = ""
        while (True):
            idx1 = line.find("[", pos)
            idx2 = line.find("]", idx1)
            
            if (idx1 == -1 or idx2 == -1): break

            tag = line[idx1 + 1:idx2]
            if (self.__is_valid_timetag(tag)):
                timetags.append(tag)
                text = line[idx2 + 1:]
            
            # look for multiple time tags
            if (len(line) > idx2 + 1 and line[idx2 + 1] == "["):
                pos = idx2
            else:
                break
        #end while
        
        return (timetags, text)
                
                
    def __parse_text(self, timestamp, text):
        """
        Parses the given text line, supporting the A2 enhanced format.
        """
    
        # list of (timestamp, words) tuples
        parts = []
        pos = 0
        
        while (True):
            # look for delimiter
            idx = text.find("<", pos)
    
            if (idx == -1):
                words = text[pos:]
                parts.append((timestamp, words))
                break
            else:
                words = text[pos:idx]
                parts.append((timestamp, words))
        
            # read timestamp
            idx2 = text.find(">", idx)
            timestamp = self.__make_timestamp(text[idx + 1:idx2])
            pos = idx2 + 1
        #end while
        #print parts
        
        # build lyrics instructions
        line = "".join(w for (t, w) in parts)
        pos1 = 0
        for timestamp, words in parts:
            pos2 = pos1 + len(words)
            self.__lyrics.append((timestamp, line, pos1, pos2))
            pos1 = pos2
        #end for


    def __is_valid_timetag(self, tag):
        """
        Validates the given time tag and returns whether it is valid or not.
        """
        
        # just a quick inaccurate check
        invalid_chars = [ c for c in tag
                          if not c.isdigit() and not c in (":", ".") ]
        if (invalid_chars):
            return False
        else:
            return True

                
    def __make_timestamp(self, t):
        """
        Takes a time string with format mm:ss.xx or mm:ss and returns a
        timestamp in milliseconds.
        """
        
        idx1 = t.find(":")
        idx2 = t.find(".")
        mm = int(t[:idx1])
        if (idx2 != -1):
            ss = int(t[idx1 + 1:idx2])
            # as discussed on talk.maemo.org, omitting the milliseconds
            # precision gives more accurate results (MAFW doesn't know about
            # milliseconds anyway)
            xx = 0 #int(t[idx2 + 1:])
        else:
            ss = int(t[idx1 + 1:])
            xx = 0
        
        return mm * 60000 + ss * 1000 + xx * 10



    def __decode(self, text):
        """
        Decodes the lyrics text to Unicode.
        """
        
        try:
            # GB2312 is the native format for LRC files since they come
            # from China
            logging.info("trying to decode lyrics as GB2312")
            return text.decode("gb2312")
        except:
            try:
                # BIG5 is for traditional Chinese
                logging.info("trying to decode lyrics as BIG5")
                return text.decode("big5")
            except:
                try:
                    # try ISO-8859-15
                    logging.info("trying to decode lyrics as ISO-8859-15")
                    return text.decode("iso-8859-15")
                except:
                    try:
                        # UTF-8 is common for Unix and Mac
                        logging.info("trying to decode lyrics as UTF-8")
                        return text.decode("utf-8")
                    except:
                        try:
                            # the CP/M descendants from Redmond speak mainly UTF-16
                            # nowadays
                            logging.info("trying to decode lyrics as UTF-16")
                            return text.decode("utf-16")
                        except:
                            # could it be plain ASCII?
                            logging.info("trying to use lyrics without decoding")
                            return text

