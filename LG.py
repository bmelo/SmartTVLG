# LG Smart TV Component
# by: Bruno Melo <bruno.raphael@gmail.com>
#
# tested with Python 3.5
# based on: http://developer.lgappstv.com/TV_HELP/index.jsp?topic=%2Flge.tvsdk.references.book%2Fhtml%2FUDAP%2FUDAP%2FLG+UDAP+2+0+Protocol+Specifications.htm

import sys, socket, re, http.client
import xml.etree.ElementTree as etree

class SmartTV:
    ## Constants
    TV_CMD_POWER = 1
    TV_CMD_NUMBER_0 = 2
    TV_CMD_NUMBER_1 = 3
    TV_CMD_NUMBER_2 = 4
    TV_CMD_NUMBER_3 = 5
    TV_CMD_NUMBER_4 = 6
    TV_CMD_NUMBER_5 = 7
    TV_CMD_NUMBER_6 = 8
    TV_CMD_NUMBER_7 = 9
    TV_CMD_NUMBER_8 = 10
    TV_CMD_NUMBER_9 = 11
    TV_CMD_UP = 12
    TV_CMD_DOWN = 13
    TV_CMD_LEFT = 14
    TV_CMD_RIGHT = 15
    TV_CMD_OK = 20
    TV_CMD_HOME_MENU = 21
    TV_CMD_BACK = 23
    TV_CMD_VOLUME_UP = 24
    TV_CMD_VOLUME_DOWN = 25
    TV_CMD_MUTE_TOGGLE = 26
    TV_CMD_CHANNEL_UP = 27
    TV_CMD_CHANNEL_DOWN = 28
    TV_CMD_BLUE = 29
    TV_CMD_GREEN = 30
    TV_CMD_RED = 31
    TV_CMD_YELLOW = 32
    TV_CMD_PLAY = 33
    TV_CMD_PAUSE = 34
    TV_CMD_STOP = 35
    TV_CMD_FAST_FORWARD = 36
    TV_CMD_REWIND = 37
    TV_CMD_SKIP_FORWARD = 38
    TV_CMD_SKIP_BACKWARD = 39
    TV_CMD_RECORD = 40
    TV_CMD_RECORDING_LIST = 41
    TV_CMD_REPEAT = 42
    TV_CMD_LIVE_TV = 43
    TV_CMD_EPG = 44
    TV_CMD_PROGRAM_INFORMATION = 45
    TV_CMD_ASPECT_RATIO = 46
    TV_CMD_EXTERNAL_INPUT = 47
    TV_CMD_PIP_SECONDARY_VIDEO = 48
    TV_CMD_SHOW_SUBTITLE = 49
    TV_CMD_PROGRAM_LIST = 50
    TV_CMD_TELE_TEXT = 51
    TV_CMD_MARK = 52
    TV_CMD_3D_VIDEO = 400
    TV_CMD_3D_LR = 401
    TV_CMD_DASH = 402
    TV_CMD_PREVIOUS_CHANNEL = 403
    TV_CMD_FAVORITE_CHANNEL = 404
    TV_CMD_QUICK_MENU = 405
    TV_CMD_TEXT_OPTION = 406
    TV_CMD_AUDIO_DESCRIPTION = 407
    TV_CMD_ENERGY_SAVING = 409
    TV_CMD_AV_MODE = 410
    TV_CMD_SIMPLINK = 411
    TV_CMD_EXIT = 412
    TV_CMD_RESERVATION_PROGRAM_LIST = 413
    TV_CMD_PIP_CHANNEL_UP = 414
    TV_CMD_PIP_CHANNEL_DOWN = 415
    TV_CMD_SWITCH_VIDEO = 416
    TV_CMD_APPS = 417
    TV_CMD_MOUSE_MOVE = "HandleTouchMove"
    TV_CMD_MOUSE_CLICK = "HandleTouchClick"
    TV_CMD_TOUCH_WHEEL = "HandleTouchWheel"
    TV_CMD_CHANGE_CHANNEL = "HandleChannelChange"
    TV_CMD_SCROLL_UP = "up"
    TV_CMD_SCROLL_DOWN = "down"
    TV_INFO_CURRENT_CHANNEL = "cur_channel"
    TV_INFO_CHANNEL_LIST = "channel_list"
    TV_INFO_CONTEXT_UI = "context_ui"
    TV_INFO_VOLUME = "volume_info"
    TV_INFO_SCREEN = "screen_image"
    TV_INFO_3D = "is_3d"
    TV_LAUNCH_APP = "AppExecute"
    
    headers = {"Content-Type": "text/xml; charset=utf-8", "User-Agent":"UDAP/2.0"}
    pairingKey = "151617"
    
    def __init__(self, ipaddress, responseMSEARCH = None):
        self.ip = ipaddress
        self.responseSearch = responseMSEARCH
    
    def findTV(nTries = 5, debug = False):
        tv = None
        strngtoXmit =   'M-SEARCH * HTTP/1.1' + '\r\n' + \
                        'HOST: 239.255.255.250:1900'  + '\r\n' + \
                        'MAN: "ssdp:discover"'  + '\r\n' + \
                        'MX: 3'  + '\r\n' + \
                        'ST: urn:schemas-udap:service:smartText:1'  + '\r\n' \
                        'USER-AGENT: UDAP/2.0'  + '\r\n\r\n'

        bytestoXmit = strngtoXmit.encode()
        sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        sock.settimeout(3)
        found = False
        gotstr = 'notyet'
        i = 0
        sock.sendto( bytestoXmit,  ('239.255.255.250', 1900 ) )
        while i <= nTries and gotstr == 'notyet':
            try:
                gotbytes, addressport = sock.recvfrom(512)
                gotstr = gotbytes.decode()
            except:
                i += 1
                sock.sendto( bytestoXmit, ( '239.255.255.250', 1900 ) )
            if debug: print(gotstr)
            if re.search('LOCATION', gotstr):
                ipaddress, _ = addressport
                tvs.append( SmartTV(ipaddress, gotstr) )
                found = True
            else:
                gotstr = 'notyet'
            i += 1
        sock.close()
        return tv

    def __execRequest( self, reqType, reqUrl, reqKey, port=8080 ):
        conn = http.client.HTTPConnection( self.ip, port=8080)
        conn.request(reqType, reqUrl, reqKey, headers=SmartTV.headers)
        httpResponse = conn.getresponse()
        return httpResponse

    def _envelope( apiType, params ):
        paramsStr = ""
        for name, value in params.items():
            paramsStr += "<{0}>{1}</{0}>".format(name, value)
        return "<?xml version=\"1.0\" encoding=\"utf-8\"?>"\
               "<envelope><api type=\"%s\">%s</api></envelope>" % (apiType, paramsStr)

    def displayKey( self ):
        reqKey = SmartTV._envelope("pairing", { "name":"showKey" })
        return self.__execRequest("POST", "/udap/api/pairing", reqKey)

    def requestPairing( self, code):
        reqKey = SmartTV._envelope("pairing", { "name":"hello", "value":code, "port":8080 })
        return self.__execRequest("POST", "/udap/api/pairing", reqKey)

    def endPairing( self):
        reqKey = SmartTV._envelope("pairing", { "name":"byebye", "port":8080 })
        return self.__execRequest("POST", "/udap/api/pairing", reqKey)

    def sendCommand( self, value ):
        reqKey = SmartTV._envelope("command", { "name":"HandleKeyInput", "value":value })
        return self.__execRequest("POST", "/udap/api/command", reqKey)

    
