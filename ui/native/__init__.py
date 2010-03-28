import platforms

if (platforms.MAEMO5):
    from Maemo5Window import Window
    from GtkTextInput import TextInput
    
elif (platforms.MAEMO4):
    from Maemo5Window import Window
    from GtkTextInput import TextInput

else:
    from GtkWindow import Window
    from GtkTextInput import TextInput

