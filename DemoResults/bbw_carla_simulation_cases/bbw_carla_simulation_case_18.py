```python
import carla
import random
import time
import numpy as np
import cv2

def main():
    try:
        # Connect to the CARLA server
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)

        # Load the 'Town01' map
        world = client.load_world('Town01')

        # Set the environment conditions
        weather = carla.WeatherParameters.ClearNoon
        world.set_weather(weather)

        # Get a random blueprint
        blueprint_library = world.get_blueprint_library()
        vehicle_blueprint = random.choice(blueprint_library.filter('vehicle.*'))

        # Spawn a vehicle
        transform = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_blueprint, transform)

        # Since no sensors or dynamic elements are specified, 
        # no additional setup is necessary.

        # Run the simulation for a bit before ending
        time.sleep(10)

    finally:
        print('Destroying actors.')
        for actor in world.get_actors():
            actor.destroy()
        print('Done.')

if __name__ == '__main__':
    main()
```

Please note that this script does not include any specific logic for image processing or pass criteria evaluation as none was specified in the test case. The script simply connects to the CARLA server, loads a map, sets the weather, spawns a vehicle, and then cleans up by destroying all actors.