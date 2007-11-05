# Viewer Capabilities

# capabilities are a bit pattern, so every value must be a power of 2
NONE             = 0
PLAYING          = 1 << 0
POSITIONING      = 1 << 1
TUNING           = 1 << 2   # same as positioning but looking different
ZOOMING          = 1 << 3
RECORDING        = 1 << 4
BOOKMARKING      = 1 << 5
