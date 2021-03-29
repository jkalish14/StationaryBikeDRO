import math
import matplotlib.pyplot as plt

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


## LED Positions
center = [132.08, 43.18]
keep_out_angle = 120

led1 = [i*3 + 1 for i in range(0,8)]
led2 = list(reversed([i*3 + 2 for i in range(0,8)]))
led3 = [i*3 + 3 for i in range(0,8)]

leds = led1 + led2 + led3

leds = ["D" + str(leds[i]) for i in range(0, len(leds))]
leds = list(reversed(leds))

print(leds)


radius = center[0]-102.87

start_angle = 270 + keep_out_angle/2
deg_per_idx = (360 - keep_out_angle) /len(leds)
for idx, rd in enumerate(leds):
    # part = pcb.FindModuleByReference(rd)
    angle = (deg_per_idx * idx +  start_angle) % 360
    xmils = center[0] + math.cos(math.radians(angle)) * radius
    ymils = center[1] - math.sin(math.radians(angle)) * radius

    print(f"{rd}, {angle} deg ({xmils:6.3f},{ymils:6.3f})")

# print(led)
print(radius)

# # For pasting into that terminal...
# leds = ['D24', 'D21', 'D18', 'D15', 'D12', 'D9', 'D6', 'D3', 'D2', 'D5', 'D8', 'D11', 'D14', 'D17', 'D20', 'D23', 'D22', 'D19', 'D16', 'D13', 'D10', 'D7', 'D4', 'D1']

# center = (132.08, 43.18)
# radius = 29.2100
# keep_out = 120
# starting = -30
# import placement_helpers
# placement_helpers.place_partial_circle(leds, starting, center, radius, keep_out)


## Calculate the relationship between theta and lead-screw position
initial_angle = 45      # deg
wheel_radius = 0.353    # in
tps_min = 300
tps_max = 3300
initial_x = wheel_radius * math.sin(math.radians(initial_angle))

tps_scale_factor = initial_angle/tps_min
output = []
tps = list(range(tps_min, tps_max,50))
for tps_position in tps:
    output.append(wheel_radius * math.sin(math.radians(tps_scale_factor*tps_position)) - initial_x)

plt.plot(tps, output)
plt.show()
print(output)