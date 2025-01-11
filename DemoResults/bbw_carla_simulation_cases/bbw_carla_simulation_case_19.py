```python
import carla
import random
import time
import numpy as np
import cv2

def main():
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)
        world = client.load_world('Town01')

        weather = carla.WeatherParameters(
            cloudyness=0.0,
            precipitation=0.0,
            sun_altitude_angle=70.0)
        world.set_weather(weather)

        blueprint_library = world.get_blueprint_library()
        vehicle_blueprint = random.choice(blueprint_library.filter('vehicle.*'))
        pedestrian_blueprint = random.choice(blueprint_library.filter('walker.pedestrian.*'))

        vehicle_spawn_point = random.choice(world.get_map().get_spawn_points())
        pedestrian_spawn_point = random.choice(world.get_map().get_spawn_points())

        vehicle = world.spawn_actor(vehicle_blueprint, vehicle_spawn_point)
        pedestrian = world.spawn_actor(pedestrian_blueprint, pedestrian_spawn_point)

        vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
        pedestrian.apply_control(carla.WalkerControl())

        time.sleep(5)

    finally:
        print('destroying actors')
        vehicle.destroy()
        pedestrian.destroy()
        print('done.')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('Done with the test.')
```
Please note that this script is a basic example of how to run a CARLA simulation with a vehicle and a pedestrian. The pass criteria, image processing function, and sensor attachment are not specified in the test case, so they are not included in the script.