# No autotools madness here. Just a simple Makefile to satisfy dpkg-buildpackage


NAME=mediabox
ICON_FILE=maemo-data/mediabox-mc.png
DESKTOP_FILE=maemo-data/mediabox-mc.desktop
SERVICE_FILE=maemo-data/de.pycage.mediabox.service

# installation destination
LIBDIR=/usr/lib/${NAME}

# files to copy into destination
COPY_FILES=com      \
	   components \
	   idtags   \
	   io       \
	   mediabox \
	   mediaplayer \
	   storage  \
	   theme    \
 	   ui       \
	   upnp     \
	   utils    \
	   mimetypes.mapping \
	   MediaBox.py
	  
EXEC_FILE=MediaBox.py



_LIBDIR=${DESTDIR}${LIBDIR}
_DESKTOPDIR=${DESTDIR}/usr/share/applications/hildon
_SERVICEDIR=${DESTDIR}/usr/share/dbus-1/services
_ICONDIR=${DESTDIR}/usr/share/icons/hicolor/scalable/apps


clean:
	find . -name "*.pyc" -exec rm "{}" \;
	find . -name "*~" -exec rm "{}" \;
	@true

all:
	@true
    
    
install-lib:
	mkdir -p ${_LIBDIR}
	cp -r ${COPY_FILES} ${_LIBDIR}
	find ${_LIBDIR} -name ".svn" -exec rm -rf "{}" \; ; true
	find ${_LIBDIR} -name "*~" -exec rm -f "{}" \; ; true
	find ${_LIBDIR} -name "*.pyc" -exec rm -f "{}" \; ; true
	find ${_LIBDIR} -name "*.xcf" -exec rm -f "{}" \; ; true
	chmod a+x ${_LIBDIR}/${EXEC_FILE}
	
install-maemo:
	mkdir -p ${_ICONDIR} ${_SERVICEDIR} ${_DESKTOPDIR}
	cp ${ICON_FILE} ${_ICONDIR}
	cp ${SERVICE_FILE} ${_SERVICEDIR}
	cp ${DESKTOP_FILE} ${_DESKTOPDIR}

install: install-lib install-maemo
	@true

doc:
	epydoc -n ${NAME} --parse-only -o ../www/apidoc -v \
	       --no-sourcecode --show-private --inheritance=included \
	       --parse-only \
	       com io mediaplayer storage theme ui upnp utils \
	       components/vkb/__messages__.py \
           components/mediascanner/__messages__.py \
           components/core/__messages__.py \
           components/input/__messages__.py \
           components/playlist_viewer/__messages__.py \
           components/ssdp_monitor/__messages__.py \
           components/dialog/__messages__.py \
           components/system/__messages__.py # idtags io mediabox storage theme ui

