import platforms

if (platforms.MAEMO5):
    from Maemo5Window import Window
    
elif (platforms.MAEMO4):
    from Maemo4Window import Window

else:
    from GtkWindow import Window

