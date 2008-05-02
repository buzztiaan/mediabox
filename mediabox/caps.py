# Viewer Capabilities

# capabilities are a bit pattern, so every value must be a power of 2
NONE             = 0
PLAYING          = 1 << 0
SKIPPING         = 1 << 1
POSITIONING      = 1 << 2
TUNING           = 1 << 3   # same as positioning but looking different
ZOOMING          = 1 << 4
RECORDING        = 1 << 5
ADDING           = 1 << 6
FORCING_SPEAKER  = 1 << 7
PLAYLIST         = 1 << 8
ALBUMS           = 1 << 9
