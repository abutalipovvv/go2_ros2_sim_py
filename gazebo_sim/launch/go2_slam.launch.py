
import os

from launch import LaunchDescription
from launch.actions import (
    GroupAction,
    IncludeLaunchDescription,
)
from launch.launch_description_sources import (
    PythonLaunchDescriptionSource,
)
from launch_ros.actions import SetRemap
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # SLAM Toolbox's Python launch file
    slam_launch = os.path.join(
        get_package_share_directory('slam_toolbox'),
        'launch',
        'online_async_launch.py'
    )

    # Our custom SLAM parameters
    slam_config = os.path.join(
        get_package_share_directory('gazebo_sim'),
        'config',
        'slam_params.yaml'
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_launch),
        launch_arguments={
            'use_sim_time': 'true',
            'slam_params_file': slam_config,
        }.items()
    )

    return LaunchDescription([
        GroupAction([
            SetRemap(src='/tf', dst='/robot1/tf'),
            SetRemap(
                src='/tf_static',
                dst='/robot1/tf_static'
            ),
            slam,
        ])
    ])

