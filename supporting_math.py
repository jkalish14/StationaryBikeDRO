import math

# Calculate the degrees the magenet occupies
mounting_radius = 3     # in
magenet_height = 0.75   #in
magnet_arc = 2*math.atan2(magenet_height, (2.*mounting_radius))*(180/math.pi)
print(f"Magnet Arc: {magnet_arc} deg")

# Calculate the time between magenet passes
max_cadence = 150   # rpm
gear_ratio = 4      

wheel_speed_rps = max_cadence*gear_ratio/60.
wheel_speed_spr = 1./wheel_speed_rps

time_between_passes = wheel_speed_spr*(magnet_arc/360.)
print(f"Time between magnet passes at a cadence of {max_cadence} rpm: {time_between_passes*1000.0:.2f}ms")


