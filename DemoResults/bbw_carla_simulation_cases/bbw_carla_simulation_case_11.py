```python
import carla
import random
import time
import numpy as np
import cv2

def main():
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        world = client.load_world('Town01')

        weather = carla.WeatherParameters(
            cloudiness=0.0,
            precipitation=0.0,
            sun_altitude_angle=70.0
        )
        world.set_weather(weather)

        blueprint_library = world.get_blueprint_library()

        vehicle_blueprint = random.choice(blueprint_library.filter('vehicle.*'))
        vehicle_transform = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_blueprint, vehicle_transform)

        actors = [vehicle]

        print('Simulation started')
        time.sleep(10)

    finally:
        print('Destroying actors')
        for actor in actors:
            actor.destroy()
        print('Done.')

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
```

This script will run a simulation in CARLA for 10 seconds. It connects to the CARLA server, loads the `Town01` map, sets up clear weather, and spawns a random vehicle. At the end of the simulation, it cleans up by destroying all actors. Please note that this script does not include any sensors or dynamic elements as it was not specified in the provided test case. Also, it does not include any image processing or pass criteria evaluation function as it was not specified in the provided test case.