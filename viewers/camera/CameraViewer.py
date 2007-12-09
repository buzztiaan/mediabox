## -*- coding: utf-8 -*-
# Based on media recorder code by INdT
#
# Camera code copyright (c) 2006 INdT - Instituto Nokia de Tecnologia,
# Elvis Pfutzenreuter.
# All rights reserved. This software is released under the LGPL licence.
# Edited by François Cauwe on 27 march 2007

from viewers.Viewer import Viewer
from mediabox import caps
import theme

import gtk
import gobject
import pygst
pygst.require("0.10")
import gst
import os


class CameraViewer(Viewer):

    PATH = os.path.dirname(__file__)
    ICON = theme.viewer_video
    PRIORITY = 100
    CAPS = caps.RECORDING
    IS_EXPERIMENTAL = True    


    def __init__(self):
    
        self.__pipeline = None
        Viewer.__init__(self)
        
        box = gtk.VBox()
               
        self.__screen = gtk.DrawingArea()
        self.__screen.connect("expose-event", self.__on_expose)
        self.__screen.show()
        box.pack_start(self.__screen, True, True, 10)        
    
        self.set_widget(box)

        
    def __setup_pipeline(self):
    
        pipeline = gst.Pipeline("mypipeline")

        # Alternate sources to run outside of Internet Tablet
        #src = gst.element_factory_make("videotestsrc", "src")
        src = gst.element_factory_make("v4l2src", "src")
        pipeline.add(src)

        caps1 = gst.element_factory_make("capsfilter", "caps1")
        # Alternate caps to run outside Internet Tablet (e.g. in a PC with webcam)
        caps1.set_property('caps', gst.caps_from_string("video/x-raw-yuv,"
                           "bpp=24,depth=24,width=320,height=240,"
                           "framerate=15/1"))
        #caps1.set_property('caps', gst.caps_from_string("video/x-raw-rgb,width=640,height=480,bpp=24,depth=24,framerate=15/1"))
        pipeline.add(caps1)

        encoder = gst.element_factory_make("hantro4200enc","encoder")
        pipeline.add(encoder)

        ## audio
        audiosrc = gst.element_factory_make("dsppcmsrc", "audio")
        pipeline.add(audiosrc)
        queue = gst.element_factory_make("queue", "queue")
        pipeline.add(queue)

        #dsppcmsrc ! queue ! audio/x-raw-int,channels=1,rate=8000 !audioconvert ! mux. 
        audiocaps = gst.element_factory_make("capsfilter", "audiocaps")
        audiocaps.set_property('caps',gst.caps_from_string("audio/x-raw-int,channels=1,rate=8000"))
        #audiocaps.set_property('caps',gst.caps_from_string("audio/x-raw-int,channels=1,rate=44100"))

        pipeline.add(audiocaps)
        audioconvert = gst.element_factory_make("audioconvert","audioconvert")
        pipeline.add(audioconvert)

        muxer = gst.element_factory_make("avimux","muxer")
        pipeline.add(muxer)
        #filesink = gst.element_factory_make('filesink', 'filesink')
        #filesink.set_property('location', path)
        #pipeline.add(filesink)

        tee = gst.element_factory_make("tee","tee")
        pipeline.add(tee)

        sink = gst.element_factory_make("xvimagesink", "sink")
        sink.set_xwindow_id(self.__screen.window.xid)
        pipeline.add(sink)

        src.link(caps1)
        caps1.link(tee)
        tee.link(sink)

        tee.link(encoder)
        encoder.link(muxer)

        audiosrc.link(queue)
        queue.link(audiocaps)
        audiocaps.link(audioconvert)
        audioconvert.link(muxer)

        #muxer.link(filesink)
        self.__pipeline = pipeline

        
    def __on_expose(self, src, ev):
    
        if (not self.__pipeline):
            try:
                self.__setup_pipeline()
                self.__pipeline.set_state(gst.STATE_PLAYING)
            except:                
                pass
               

    def is_available(self):
    
        return os.environ.get("MEDIABOX_EXPERIMENTAL")               
                
             
    def show(self):
    
        Viewer.show(self)
        self.update_observer(self.OBS_SET_COLLECTION, [])
                
                
    def hide(self):
    
        if (self.__pipeline):
            self.__pipeline.set_state(gst.STATE_NULL)
        Viewer.hide(self)
        self.__pipeline = None
        
        
