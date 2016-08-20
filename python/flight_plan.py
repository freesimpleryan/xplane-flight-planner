import platform

if platform.system == 'Windows':
	dat_file_path = "..\\data\\"
	save_file_path = "..\\my_plans\\"
else:
	dat_file_path = "../data/"
	save_file_path = "../my_plans/"
earth_nav_file = "%searth_nav.dat"%dat_file_path
earth_fix_file = "%searth_fix.dat"%dat_file_path
earth_nav = {}
earth_fix = {}
cruise_altitude = ""
cruise_speed = ""
climb_speed = ""
asl_or_agl = ''

def do_load(in_file, mem_dict, ignore_flags, index_callsign, gps_index):
	f = open(in_file)
	for line in f:
		if line == "" or line is None:
			continue
		data = line.split()
		if len(data) is 0 or data[0] in ignore_flags:
			continue
		coordinates = "%s %s "%(data[gps_index], data[gps_index + 1])
		callsign = data[index_callsign]
		mem_dict[callsign] = coordinates
	f.close()


def make_output(data_dict):
	fout = []
	fout.append("STARTTIME\n")
	fout.append(data_dict["departure_time"])
	fout.append("\nENDTIME\n")
	fout.append("\nSTARTAIRCRAFT\n")
	fout.append(data_dict["flight_aircraft"])
	fout.append("\nENDAIRCRAFT\n")
	fout.append("\nSTARTCALLSIGN\n")
	fout.append(data_dict["call_sign"])
	fout.append("\nENDCALLSIGN\n")
	fout.append("\nSTARTDAYS\n")
	fout.append(data_dict["days"])
	fout.append("\nENDDAYS\n")
	fout.append("\nSTARTDEPAIRPORT\n")
	fout.append(data_dict["departure_airport"])
	fout.append("\nENDDEPAIRTPORT\n")
	fout.append("\nSTARTDESTAIRPORT\n")
	fout.append(data_dict["destination_airport"])
	fout.append("\nENDDESTAIRPORT\n")
	fout.append("\nSTART_FLY_TO_COMPLETION\n")
	fout.append(data_dict["fly_to_completion"])
	fout.append("\nEND_FLY_TO_COMPLETION\n")
	fout.append("\nSTART_LANDING_LIGHT_ALT\n")
	fout.append(data_dict["landing_light_altitude"])
	fout.append("\nEND_LANDING_LIGHT_ALT\n")
	fout.append("\nSTARTSTEERPOINTS\n")
	for steer_point in data_dict["steer_points"]:
		fout.append(steer_point)
		fout.append("\n")
	fout.append("ENDSTEERPOINTS")
	return "".join(fout)

def make_waypoint(waypoint_input):
	coordinates = ''
	waypoint = []
	if len(waypoint_input) == 3:
		if waypoint_input in earth_nav:
			coordinates = earth_nav[waypoint_input]
		else:
			print "Waypoint %s not found in earth_nav"%waypoint_input
			return ''
	elif len(waypoint_input) == 5:
		if waypoint_input in earth_fix:
			coordinates = earth_fix[waypoint_input]
		else:
			print "Waypoint %s not found in earth_fix"%waypoint_input
			return ''
	else:
		print "%s is not a valid waypoint."%waypoint_input
		return ''
	waypoint.append(''.join(coordinates))
	waypoint.append(' ')
	print "%s found. Coordinates %s added."%(waypoint_input, coordinates)
	altitude = raw_input('Waypoint Altitude: ')
	waypoint.append(altitude)
	if int(altitude) < int(cruise_altitude):
		airspeed = climb_speed
	elif int(altitude) == int(cruise_altitude):
		airspeed = cruise_speed
	else:
		print "Waypoint altitude is higher than cruise altitude!"
		return ''
	print "Airspeed set to %s"%airspeed
	waypoint.append(' %s '%asl_or_agl)
	waypoint.append(' %s '%airspeed)
	max_bank_angle = "25"
	waypoint.append(' %s '%max_bank_angle)
	waypoint.append('-1 -1 1 ')
	waypoint.append(waypoint_input)
	return ''.join(waypoint)

if __name__ == "__main__":
	print "Loading %s..."%earth_fix_file
	do_load(earth_fix_file, earth_fix, ("I", "600", "99"), 2, 0)
	print "Earth fix file loaded"
	print "%s waypoints found"%len(earth_fix)
	print "Loading %s..."%earth_nav_file
	do_load(earth_nav_file, earth_nav, ("I", "810", "99"), 7, 1)
	print "Earth nav file loaded"
	print "%s waypoints found"%len(earth_nav)
	flight_plan = {}
	airline = raw_input("Airline code: ")
	flight_plan["departure_time"] = raw_input('Departure time: ')
	flight_plan["flight_aircraft"] = raw_input('Aircraft: ')
	flight_plan["call_sign"] = raw_input('Call sign: ')
	print "Enter days separated by spaces"
	flight_plan["days"] = raw_input('')
	flight_plan["departure_airport"] = raw_input('ICAO of departure airport: ')
	flight_plan["destination_airport"] = raw_input('ICAO of arrival airport: ')
	print "Fly to completion? 1 = yes, 0 = no"
	flight_plan["fly_to_completion"] = raw_input('')
	if not (flight_plan["fly_to_completion"] == "1" or flight_plan["fly_to_completion"] == "0"):
		print "Defaulting to 1"
		flight_plan["fly_to_completion"] = "1"
	flight_plan["landing_light_altitude"] = raw_input('Landing light altitude: ')
	cruise_altitude = raw_input('Cruise altitude: ')
	cruise_speed = raw_input('Cruise speed: ')
	climb_speed = raw_input('Climb speed: ')
	while not (asl_or_agl == "ASL" or asl_or_agl == "AGL"):
		asl_or_agl = raw_input('ASL or AGL: ')
	print "Chart course. Type 'done' when done."
	waypoint_input = ""
	steer_points = []
	while waypoint_input != "done":
		coordinates = []
		waypoint = []
		waypoint_input = raw_input('Waypoint callsign: ')
		if waypoint_input == "done":
			continue
		string_waypoint = make_waypoint(waypoint_input)
		if string_waypoint == '':
			continue
		steer_points.append(string_waypoint)
		print "WAYPOINT ADDED SUCCESSFULLY"
	flight_plan["steer_points"] = steer_points
	file_name = "%s_%s_to_%s_%s.txt"%(airline, flight_plan["departure_airport"], flight_plan["destination_airport"], flight_plan["departure_time"])
	file_contents = make_output(flight_plan)
	out_file = open(save_file_path+file_name, 'w+')
	out_file.write(file_contents)
	out_file.close()
	print "%s%s created"%(save_file_path, file_name)
