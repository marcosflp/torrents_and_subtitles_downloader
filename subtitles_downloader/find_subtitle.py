import os
import re
import sys
import struct
import mimetypes
import subprocess
import argparse
import time
import urllib2
from xmlrpclib import ServerProxy, Error

# ==== Opensubtitles.org server settings =======================================
# XML-RPC server domain for opensubtitles.org:
osd_server = ServerProxy('http://api.opensubtitles.org/xml-rpc')

# set account
osd_username = 'marcosflp'
osd_password = 'marcos2006'
osd_language = 'pt'


# ==== Main program (execution starts here) ====================================
# ==============================================================================

# ==== Instances dispatcher

try:
    try:
        # Connection to opensubtitles.org server
        session = osd_server.LogIn(osd_username, osd_password, osd_language, 'opensubtitles-download 3.5')
    except Exception:
        # Retry once, it could be a momentary overloaded server?
        time.sleep(3)
        try:
            # Connection to opensubtitles.org server
            session = osd_server.LogIn(osd_username, osd_password, osd_language, 'opensubtitles-download 3.5')
        except Exception: 
            # Failed connection attempts?
            superPrint("error", "Connection error!", "Unable to reach opensubtitles.org servers!\n\nPlease check:\n- Your Internet connection status\n- www.opensubtitles.org availability\n- Your downloads limit (200 subtitles per 24h)\nThe subtitles search and download service is powered by opensubtitles.org. Be sure to donate if you appreciate the service provided!")
            sys.exit(1)

    # Connection refused?
    if session['status'] != '200 OK':
        superPrint("error", "Connection error!", "Opensubtitles.org servers refused the connection: " + session['status'] + ".\n\nPlease check:\n- Your Internet connection status\n- www.opensubtitles.org availability\n- Your 200 downloads per 24h limit")
        sys.exit(1)

    searchLanguage = 0
    searchLanguageResult = 0
    videoTitle = 'Unknown video title'
    videoHash = hashFile(videoPath)
    videoSize = os.path.getsize(videoPath)
    videoFileName = os.path.basename(videoPath)

    # Count languages marked for this search
    for SubLanguageID in opt_languages:
        searchLanguage += len(SubLanguageID.split(','))

    # Search for available subtitles using file hash and size
    for SubLanguageID in opt_languages:
        searchList = []
        searchList.append({'sublanguageid':SubLanguageID, 'moviehash':videoHash, 'moviebytesize':str(videoSize)})
        try:
            subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
        except Exception:
            # Retry once, we are already connected, the server is probably momentary overloaded
            time.sleep(3)
            try:
                subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
            except Exception:
                superPrint("error", "Search error!", "Unable to reach opensubtitles.org servers!\n<b>Search error</b>")

        # No results using search by hash? Retry with filename
        if (not subtitlesList['data']) and (opt_backup_searchbyname == 'on'):
            searchList = []
            searchList.append({'sublanguageid':SubLanguageID, 'query':videoFileName})
            try:
                subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
            except Exception:
                # Retry once, we are already connected, the server is probably momentary overloaded
                time.sleep(3)
                try:
                    subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
                except Exception:
                    superPrint("error", "Search error!", "Unable to reach opensubtitles.org servers!\n<b>Search error</b>")
        else:
            opt_backup_searchbyname = 'off'

        # Parse the results of the XML-RPC query
        if subtitlesList['data']:

            # Mark search as successful
            searchLanguageResult += 1
            subtitlesSelected = ''

            # If there is only one subtitles, which wasn't found by filename, auto-select it
            if (len(subtitlesList['data']) == 1) and (opt_backup_searchbyname == 'off'):
                subtitlesSelected = subtitlesList['data'][0]['SubFileName']

            # Get video title
            videoTitle = subtitlesList['data'][0]['MovieName']

            # Title and filename may need string sanitizing to avoid zenity/kdialog handling errors
            if opt_gui != 'cli':
                videoTitle = videoTitle.replace('"', '\\"')
                videoTitle = videoTitle.replace("'", "\'")
                videoTitle = videoTitle.replace('`', '\`')
                videoTitle = videoTitle.replace("&", "&amp;")
                videoFileName = videoFileName.replace('"', '\\"')
                videoFileName = videoFileName.replace("'", "\'")
                videoFileName = videoFileName.replace('`', '\`')
                videoFileName = videoFileName.replace("&", "&amp;")

            # If there is more than one subtitles and opt_selection_mode != 'auto',
            # then let the user decide which one will be downloaded
            if subtitlesSelected == '':
                # Automatic subtitles selection?
                if opt_selection_mode == 'auto':
                    subtitlesSelected = selectionAuto(subtitlesList)
                else:
                    # Go through the list of subtitles and handle 'auto' settings activation
                    for item in subtitlesList['data']:
                        if opt_selection_language == 'auto':
                            if searchLanguage > 1:
                                opt_selection_language = 'on'
                        if opt_selection_hi == 'auto':
                            if item['SubHearingImpaired'] == '1':
                                opt_selection_hi = 'on'
                        if opt_selection_rating == 'auto':
                            if item['SubRating'] != '0.0':
                                opt_selection_rating = 'on'
                        if opt_selection_count == 'auto':
                            opt_selection_count = 'on'

                    # Spaw selection window
                    if opt_gui == 'gnome':
                        subtitlesSelected = selectionGnome(subtitlesList)
                    elif opt_gui == 'kde':
                        subtitlesSelected = selectionKde(subtitlesList)
                    else: # CLI
                        subtitlesSelected = selectionCLI(subtitlesList)

            # If a subtitles has been selected at this point, download it!
            if subtitlesSelected:
                subIndex = 0
                subIndexTemp = 0

                # Select the subtitles file to download
                for item in subtitlesList['data']:
                    if item['SubFileName'] == subtitlesSelected:
                        subIndex = subIndexTemp
                        break
                    else:
                        subIndexTemp += 1

                subLangId = opt_language_separator  + subtitlesList['data'][subIndex]['ISO639']
                subLangName = subtitlesList['data'][subIndex]['LanguageName']
                subURL = subtitlesList['data'][subIndex]['SubDownloadLink']
                subPath = videoPath.rsplit('.', 1)[0] + '.' + subtitlesList['data'][subIndex]['SubFormat']

                # Write language code into the filename?
                if ((opt_language_suffix == 'on') or
                    (opt_language_suffix == 'auto' and searchLanguageResult > 1)):
                    subPath = videoPath.rsplit('.', 1)[0] + subLangId + '.' + subtitlesList['data'][subIndex]['SubFormat']

                # Escape non-alphanumeric characters from the subtitles path
                subPath = re.escape(subPath)

                # Download and unzip the selected subtitles (with progressbar)
                if opt_gui == 'gnome':
                    process_subtitlesDownload = subprocess.call("(wget -q -O - " + subURL + " | gunzip > " + subPath + ") 2>&1" + ' | (zenity --auto-close --progress --pulsate --title="Downloading subtitles, please wait..." --text="Downloading <b>' + subtitlesList['data'][subIndex]['LanguageName'] + '</b> subtitles for <b>' + videoTitle + '</b>...")', shell=True)
                elif opt_gui == 'kde':
                    process_subtitlesDownload = subprocess.call("(wget -q -O - " + subURL + " | gunzip > " + subPath + ") 2>&1", shell=True)
                else: # CLI
                    print(">> Downloading '" + subtitlesList['data'][subIndex]['LanguageName'] + "' subtitles for '" + videoTitle + "'")
                    process_subtitlesDownload = subprocess.call("wget -nv -O - " + subURL + " | gunzip > " + subPath, shell=True)

                # If an error occur, say so
                if process_subtitlesDownload != 0:
                    superPrint("error", "Subtitling error!", "An error occurred while downloading or writing <b>" + subtitlesList['data'][subIndex]['LanguageName'] + "</b> subtitles for <b>" + videoTitle + "</b>.")
                    osd_server.LogOut(session['token'])
                    sys.exit(1)

    # Print a message if no subtitles have been found, for any of the languages
    if searchLanguageResult == 0:
        superPrint("info", "No subtitles found for: " + videoFileName, '<b>No subtitles found</b> for this video:\n<i>' + videoFileName + '</i>')

    # Disconnect from opensubtitles.org server, then exit
    if session['token']: osd_server.LogOut(session['token'])
    sys.exit(0)

except (RuntimeError, TypeError, NameError, IOError, OSError):

    # Do not warn about remote disconnection # bug/feature of python 3.5
    if "http.client.RemoteDisconnected" in str(sys.exc_info()[0]):
        sys.exit(1)

    # An unknown error occur, let's apologize before exiting
    superPrint("error", "Unknown error!", "OpenSubtitlesDownload encountered an <b>unknown error</b>, sorry about that...\n\n" + \
               "Error: <b>" + str(sys.exc_info()[0]).replace('<', '[').replace('>', ']') + "</b>\n\n" + \
               "Just to be safe, please check:\n- www.opensubtitles.org availability\n- Your downloads limit (200 subtitles per 24h)\n- Your Internet connection status\n- That are using the latest version of this software ;-)")

    # Disconnect from opensubtitles.org server, then exit
    if session['token']: osd_server.LogOut(session['token'])

    sys.exit(1)
