Here is a Python script that fulfills your requirements:

```python
import carla
import random
import time
import numpy as np
import cv2

def process_img(image):
    i = np.array(image.raw_data)
    i2 = i.reshape((720, 1280, 4))
    i3 = i2[:, :, :3]
    cv2.imshow("", i3)
    cv2.waitKey(1)
    return i3/255.0

def main():
    actor_list = []

    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        world = client.load_world('Town01')

        blueprint_library = world.get_blueprint_library()

        bp = blueprint_library.filter('model3')[0]
        print(bp)

        spawn_point = random.choice(world.get_map().get_spawn_points())

        vehicle = world.spawn_actor(bp, spawn_point)
        vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
        actor_list.append(vehicle)

        cam_bp = blueprint_library.find('sensor.camera.rgb')
        cam_bp.set_attribute('image_size_x', '1280')
        cam_bp.set_attribute('image_size_y', '720')
        cam_bp.set_attribute('fov', '110')

        spawn_point = carla.Transform(carla.Location(x=2.5, z=0.7))

        sensor = world.spawn_actor(cam_bp, spawn_point, attach_to=vehicle)
        actor_list.append(sensor)
        sensor.listen(lambda data: process_img(data))

        time.sleep(10)

    finally:
        print('destroying actors')
        for actor in actor_list:
            actor.destroy()
        print('done.')

if __name__ == '__main__':
    main()
```

This script will connect to the CARLA server, load the 'Town01' map, spawn a vehicle, attach a camera sensor to the vehicle, and process the images captured by the sensor in real-time. The processed images are displayed using OpenCV. Please note that the script does not include specific logic for object detection and classification in the images, as this would require a more complex implementation involving machine learning or computer vision techniques. The script also does not include specific weather or visibility conditions, as these were not specified in the test case.