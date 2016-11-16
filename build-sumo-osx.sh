#!/bin/sh

export CPPFLAGS="$CPPFLAGS -I/opt/X11/include/"
export LDFLAGS="-L/opt/X11/lib"
cd sumo/sumo &&
make -f Makefile.cvs &&
./configure --with-xerces=/usr/local --with-proj-gdal=/usr/local &&
make -j8
