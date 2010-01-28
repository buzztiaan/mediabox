from com import MediaOutput, msgs
import mediaplayer


class LocalOutput(MediaOutput):
    """
    Media output device for playing on the local device.
    """
    
    TITLE = "Local"
    
    """
    @todo: For now, this just passes stuff through to the mediaplayer modules.
           Eventually, the mediaplayer backends should be integrated into the
           component system and loaded dynamically by this component.
    """


    def __init__(self):
    
        self.__backend = None
        self.__window_id = 0
    
        MediaOutput.__init__(self)


    def __load_backend_for(self, mimetype):
    
        self.__backend = mediaplayer.get_player_for_mimetype(mimetype)
        self.__backend.connect_volume_changed(self.__on_change_volume)
        self.__backend.connect_status_changed(self.__on_change_status)
        self.__backend.connect_position_changed(self.__on_change_position)
        self.__backend.connect_tag_discovered(self.__on_tags)
        self.__backend.connect_error(self.__on_error)
        
        
    def __on_change_status(self, ctx_id, status):
    
        self.emit_event(self.EVENT_STATUS_CHANGED, ctx_id, status)


    def __on_change_volume(self, vol):
    
        self.emit_event(self.EVENT_VOLUME_CHANGED, vol)


    def __on_change_position(self, ctx_id, pos, total):
    
        self.emit_event(self.EVENT_POSITION_CHANGED, ctx_id, pos, total)


    def __on_tags(self, ctx_id, tags):
    
        self.emit_event(self.EVENT_TAG_DISCOVERED, ctx_id, tags)


    def __on_error(self, ctx_id, err):
    
        self.emit_event(self.EVENT_ERROR, ctx_id, err)
        

    def load_audio(self, f):
    
        self.__load_backend_for(f.mimetype)
        return self.__backend.load_audio(f.get_resource())
        
        
    def load_video(self, f):
    
        self.__load_backend_for(f.mimetype)
        self.__backend.set_window(self.__window_id)
        return self.__backend.load_video(f.get_resource())

        
    def play(self):
    
        if (self.__backend):
            self.__backend.play()
        
        
    def pause(self):
    
        if (self.__backend):
            self.__backend.pause()
        
        
    def stop(self):
    
        if (self.__backend):
            self.__backend.stop()
        
        
    def seek(self, pos):
    
        if (self.__backend):
            self.__backend.seek(pos)
        


    def seek_percent(self, percent):
    
        if (self.__backend):
            self.__backend.seek_percent(percent)


    def rewind(self):
    
        if (self.__backend):
            self.__backend.rewind()
       
        
    def forward(self):
    
        if (self.__backend):
            self.__backend.forward()

                
    def set_volume(self, vol):
    
        if (self.__backend):
            self.__backend.set_volume(vol)


    def set_window(self, xid):
    
        self.__window_id = xid

        if (self.__backend):
            self.__backend.set_window(xid)

