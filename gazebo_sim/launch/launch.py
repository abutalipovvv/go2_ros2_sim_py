import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    ExecuteProcess,
    RegisterEventHandler,
    TimerAction     # this is for slam integration
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.event_handlers import OnProcessExit
from launch_ros.actions import SetParameter


def generate_launch_description():
    ld = LaunchDescription()

    package_name = 'gazebo_sim'
    pkg_path = get_package_share_directory(package_name)

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    ld.add_action(DeclareLaunchArgument('use_sim_time', default_value='true',
                                       description='Использовать симуляционное время'))

    ld.add_action(SetParameter(name='use_sim_time', value=use_sim_time))


    world_file = os.path.join(pkg_path, 'world', 'cafe.world') 
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r -v4 ', world_file], 'on_exit_shutdown': 'true'}.items()
    )
    ld.add_action(gazebo)

    pause = ExecuteProcess(
        cmd=['sleep', '6'],
        output='screen'
    )
    ld.add_action(pause)

    multi_nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_path, 'launch', 'gazebo_multi_nav2_world.launch.py')
        )
    )

    # for slam
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pkg_path,
                'launch',
                'go2_slam.launch.py'
            )
        )
    )

    launch_after_pause = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=pause,
            on_exit=[
                # launch robot and controllers
                multi_nav2_launch,

                # start slam after allowing robot setup
                TimerAction(
                    period=12.0,
                    actions=[slam_launch]
                )
            ]
        )
    )

    ld.add_action(launch_after_pause)

    return ld
