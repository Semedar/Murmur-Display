'''
MurmurDisplay.py - Murmur (Mumble) Server Display Script For DOT3k
Semedar@Gmail.com - http://www.Semedar.com/
Copyright (c) 2015, Villa, Victor D. / Semedar@Gmail.com
Version: 1.3 Alpha

Notes:
	Import within loop doesn't 'import'/do it twice.

To Do:
	Don't update/refresh the screen if user count didn't change (Done)
	Add white LED flash when user value changes (Done)
	Add 'favorite' users and display changes to special color

Known Issues:
	If switch from offline to online display, it shows "Onlinee" - clear/refresh display (fixed)
	Display not lighting up red (fixed)
	Pi crashes/freezes after 2 days of this script running (fixed)

Troubleshoot Values:
	print "users.value %i" % (len(users))
	print "uptime.value %.2f" % (float(meta.getUptime())/60/60/24)
	print "chancount.value %.1f" % (len(server.getChannels())/10)
	print "bancount.value %i" % (len(server.getBans()))
	print "usersnotauth.value %i" % (usersnotauth)
'''

#!/usr/bin/env python
import dot3k.lcd as lcd
import dot3k.backlight as backlight
import time

iceslice='/usr/share/Ice/slice/Murmur.ice'
iceincludepath="/usr/share/Ice/slice"
serverport=64738
iceport=6502
icesecret="!QAZ@WSX1qaz2wsx"
messagesizemax="65535"
oldUserCount=-1
prev_hours=''

import Ice, sys
Ice.loadSlice("--all -I%s %s" % (iceincludepath, iceslice))
props = Ice.createProperties([])
props.setProperty("Ice.MessageSizeMax", str(messagesizemax))
props.setProperty("Ice.ImplicitContext", "Shared")
id = Ice.InitializationData()
id.properties = props
ice = Ice.initialize(id)
ice.getImplicitContext().put("secret", icesecret)
import Murmur

while True:
	if (sys.argv[1:]):
	  if (sys.argv[1] == "config"):
		print 'graph_title Murmur (Port %s)' % (serverport)
		print 'graph_vlabel Count'
		print 'users.label Users (All)'
		print 'usersnotauth.label Users (Not authenticated)'
		print 'uptime.label Uptime in days'
		print 'chancount.label Channelcount/10'
		print 'bancount.label Bans on server'
		sys.exit(0)

	meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy("Meta:tcp -h 127.0.0.1 -p %s" % (iceport)))
	try:
		server=meta.getServer(1)
	except Murmur.InvalidSecretException:
		print 'Given icesecreatread password is wrong.'
		ice.shutdown()
		sys.exit(1)

	# Count Users
	usersnotauth=0
	users=server.getUsers()
	for key in users.keys():
	  if (users[key].userid == -1):
		usersnotauth+=1

	# Ping 'Google.com' to see if the Raspberry Pi is online
	import os
	hostname = "Google.com"
	response = os.system("ping -c 1 -w2 " + hostname + " > /dev/null 2>&1")

	# Get uptime in easy to read format
	def uptime():
                global oldUserCount, prev_hours
                # find the latest uptime.
		with open('/proc/uptime', 'r') as f:
			uptime_seconds = float(f.readline().split()[0])
			seconds = str(int(uptime_seconds % 60))
			minutes = str(int(uptime_seconds /60 % 60))
			hours = str(int(uptime_seconds / 60 / 60 % 24))
			days = str(int(uptime_seconds / 60 /60 / 24))
			# Time unit strings
			time_d = ' Days, '
			time_h = ' Hrs'
			time_m = ' min, '
			time_s = ' sec'
		# Check if the users count has changed or hours has changed
		if len(users) != oldUserCount or prev_hours != hours:
                        if len(users) > 0: # If there's anyone in the server
                                lcd.clear()
                                lcd.set_cursor_position(0, 0)
                                lcd.write("Online Users: %i" % (len(users)))
                                backlight.rgb(125,125,175)
                                lcd.set_cursor_position(0, 1)
                                if response == 0: # If pinging Google succeeded
                                  lcd.write("Server: Online")
                                else: # If pinging Google failed
                                  lcd.write("Server: Offline")
                                  backlight.rgb(175,125,125)
                                lcd.set_cursor_position(0, 2)
                                lcd.write(days + time_d + hours + time_h)
                        else: # If there's no one in the server
                                lcd.clear()
                                lcd.set_cursor_position(0, 0)
                                lcd.write("No Online Users")
                                backlight.rgb(0,0,0)
                                lcd.set_cursor_position(0, 1)
                                if response == 0: # If pinging Google succeeded
                                  lcd.write("Server: Online")
                                else: # If pinging Google failed
                                  lcd.write("Server: Offline")
                                  backlight.rgb(175,125,125)
                                lcd.set_cursor_position(0, 2)
                                lcd.write(days + time_d + hours + time_h)
                        # Detect if user count has changed if changed flash the LED
                        if oldUserCount != len(users):
                                backlight.set_bar(0,[148]*9)
                                time.sleep(.1)
                                backlight.set_bar(0,[0]*9)
                                time.sleep(.1)
                                backlight.set_bar(0,[148]*9)
                                time.sleep(.1)
                                backlight.set_bar(0,[0]*9)
                        # Update current user count and current hours 
                        oldUserCount = len(users) 
                        prev_hours = hours
	# call uptime to see if we need any update
	uptime()
	#sleep for some time before getting the user count again.
	time.sleep(7)
