MAPPING = { "APIC": "PICTURE",
            "COMM": "COMMENT",
            "TCOP": "COPYRIGHT",
            "TDOR": "DATE",
            "TIT2": "TITLE",
            "TLEN": "LENGTH",
            "TPE1": "ARTIST",
            "TALB": "ALBUM",
            "TOAL": "ALBUM",
            "TCON": "GENRE",
            "TRCK": "TRACKNUMBER",
             
            "COM":  "COMMENT",
            "PIC":  "PICTURE",
            "TAL":  "ALBUM",
            "TP1":  "ARTIST",
            "TT2":  "TITLE",
            "TRK":  "TRACKNUMBER",
            "TYE":  "YEAR",
            "TCO":  "GENRE",
            
            # Tracker mapping
            "Audio:Title": "TITLE",
            "Audio:Artist": "ARTIST",
            "Audio:Album": "ALBUM",
            "Audio:Genre": "GENRE",
            "Audio:Duration": "LENGTH",
            "Audio:ReleaseDate": "DATE",
            "Audio:TrackNo": "TRACKNUMBER",
            "Audio:Comment": "COMMENT",
            "File:Copyright": "COPYRIGHT" }

STRINGS = ( "COMMENT", "COPYRIGHT", "TITLE", "ARTIST", "ALBUM", "TRACKNUMBER" )

# the official weird, unsorted, incomplete list of genres for ID3 tags
GENRES = [
  "Blues", 
  "Classic Rock",
  "Country",
  "Dance",
  "Disco",
  "Funk",
  "Grunge",
  "Hip-Hop",
  "Jazz",
  "Metal",
  "New Age",
  "Oldies",
  "Other",  # probably the most important entry in this list
  "Pop",
  "R&B",
  "Rap",
  "Reggae",
  "Rock",
  "Techno",
  "Industrial",
  
  "Alternative",
  "Ska",
  "Death Metal",
  "Pranks",
  "Soundtrack",
  "Euro-Techno",
  "Ambient",
  "Trip-Hop",
  "Vocal",
  "Jazz + Funk",
  "Fusion",
  "Trance",
  "Classical",
  "Instrumental",
  "Acid",
  "House",
  "Game",
  "Sound Clip",
  "Gospel",
  "Noise",
  
  "Alt Rock",
  "Bass",
  "Soul",
  "Punk",
  "Space",
  "Meditative",
  "Instrumental Pop",
  "Instrumental Rock",
  "Ethnic",
  "Gothic",
  "Darkwave",
  "Techno-Industrial",
  "Electronic",
  "Pop-Folk",
  "Eurodance",
  "Dream",
  "Southern Rock",
  "Comedy",
  "Cult",
  "Gangsta Rap",
  
  "Top 40",
  "Christian Rap",
  "Pop / Funk",
  "Jungle",
  "Native American",
  "Cabaret",
  "New Wave",
  "Psychedelic",
  "Rave",
  "Showtunes",
  "Trailer",
  "Lo-Fi",
  "Tribal",
  "Acid Punk",
  "Acid Jazz",
  "Polka",
  "Retro",
  "Musical",
  "Rock'n Roll",
  "Hard Rock",
  
  "Folk",
  "Folk / Rock",
  "National Folk",
  "Swing",
  "Fast-Fusion",
  "Bebop",
  "Latin",
  "Revival",
  "Celtic",
  "Bluegrass",
  "Avantgarde",
  "Gothic Rock",
  "Progressive Rock",
  "Psychedelic Rock",
  "Symphonic Rock",
  "Slow Rock",
  "Big Band",
  "Chorus",
  "Easy Listening",
  "Acoustic",
  
  "Humour",
  "Speech",
  "Chanson",
  "Opera",
  "Chamber Music",
  "Sonata",
  "Symphony",
  "Booty Bass",
  "Primus",
  "Porn Groove",
  "Satire",
  "Slow Jam",
  "Club",
  "Tango",
  "Samba",
  "Folklore",
  "Ballad",
  "Power Ballad",
  "Rhythmic Soul",
  "Freestyle",
  
  "Duet",
  "Punk Rock",
  "Drum Solo",
  "A Capella",
  "Euro-House",
  "Dance Hall",
  "Goa",
  "Drum & Bass",
  "Club-House",
  "Hardcore",
  "Terror",
  "Indie",
  "BritPop",
  "Negerpunk",
  "Polsk Punk",
  "Beat",
  "Christian Gangsta Rap",
  "Heavy Metal",
  "Black Metal",
  "Crossover",
  
  "Contemporary Christian",
  "Christian Rock",
  "Merengue",
  "Salsa",
  "Thrash Metal",
  "Anime",
  "JPop",
  "Synthpop"
] + ["Unknown"] * 108



def resolve_genre(value):

    if (value.isdigit()):
        try:
            genre = GENRES[int(value)]
        except:
            genre = value

    elif ("(" in value and ")" in value):
        idx1 = value.find("(")
        idx2 = value.find(")")
        try:
            genre = GENRES[int(value[idx1 + 1:idx2])]
        except:
            genre = value

    else:
        genre = value
        
    return genre

