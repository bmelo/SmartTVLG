from LG import SmartTV as LGTv

IP = ""
CODE = ""

#tv = LGTv.findTV(10, True) #-- not working well
#tv = LGTv( IP )

tv.displayKey()
#resp = tv.requestPairing( CODE )
#resp = tv.endPairing()
resp = tv.sendCommand( LGTv.TV_CMD_VOLUME_UP )
