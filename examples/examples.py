import datetime
import os
from typing import List

import aind_bci_no_movement.task_logic as task_logic
import aind_behavior_services.rig as rig
from aind_bci_no_movement.rig import (
    Axis,
    BciNoMovementRig,
    LoadCells,
    Networking,
    Operation,
    ZaberAxis,
    ZaberGenericCommand,
    ZaberManipulator,
    ZmqConnection,
)
from aind_bci_no_movement.task_logic import BciNoMovementTaskLogic, BciNoMovementTaskParameters
from aind_behavior_services import db_utils as db
from aind_behavior_services.calibration import load_cells as lc
from aind_behavior_services.session import AindBehaviorSessionModel


def mock_rig() -> BciNoMovementRig:

    video_writer = rig.VideoWriterFfmpeg(
        frame_rate=120, container_extension="mp4", output_arguments="-c:v h264_nvenc -vsync 0 -2pass "
    )

    load_cell_calibration = lc.LoadCellsCalibration(
        input=lc.LoadCellsCalibrationInput(),
        output=lc.LoadCellsCalibrationOutput(
            offset={0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
            baseline={0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
        ),
    )

    zaber_commands: List[ZaberGenericCommand] = []

    return BciNoMovementRig(
        computer_name=os.environ["COMPUTERNAME"],
        rig_name="bci-no-movement-rig",
        triggered_camera_controller=rig.CameraController[rig.SpinnakerCamera](
            frame_rate=120,
            cameras={
                "Camera0": rig.SpinnakerCamera(
                    serial_number="23381093", binning=1, exposure=5000, gain=0, video_writer=video_writer
                ),
            },
        ),
        harp_behavior=rig.HarpBehavior(port_name="COM8"),
        harp_load_cell=LoadCells(port_name="COM7", calibration=load_cell_calibration),
        harp_clock_generator=rig.HarpClockGenerator(port_name="COM9"),
        operation=Operation(load_cell_index=0),
        manipulator=ZaberManipulator(
            com_port="COM10",
            spout_axis=Axis.X,
            generic_commands=zaber_commands,
            x_axis=ZaberAxis(device_index=0, axis_index=1, upper_limit=100, lower_limit=0),
            y_axis=ZaberAxis(device_index=0, axis_index=2),
            z_axis=ZaberAxis(device_index=1, axis_index=1),
        ),
        networking=Networking(
            zmq_publisher=ZmqConnection(connection_string="@tcp://localhost:5556", topic="bci-no-movement"),
            zmq_subscriber=ZmqConnection(connection_string="@tcp://localhost:5557", topic="bci-no-movement"),
        ),
    )


def mock_task_logic() -> BciNoMovementTaskLogic:
    return BciNoMovementTaskLogic(
        name="bci-no-movement",
        stage_name="learning",
        task_parameters=BciNoMovementTaskParameters(
            rng_seed=None,
            enable_sound_on_reward_zone_entry=True,
            inter_trial_interval=0.5,
            lick_response_time=2,
            max_trial_duration=20,
            no_movement_time_before_trial=0.5,
            reward_consume_time=2,
            valve_open_time=0.1,
            wait_for_lick=True,
            far_position_offset=30,
            manipulator_reset_position=task_logic.Point3d(x=43, y=-2, z=0.26),
            wait_microscope_time=0.5,
            bci_passive_control=task_logic.SignalProcessing(gain=0.002, baseline_threshold=5000),
            no_movement_passive_control=task_logic.SignalProcessing(
                gain=0.002, baseline_threshold=5000, low_pass_cut_off=50, high_pass_cut_off=0.001
            ),
            bci_active_control=task_logic.SignalProcessing(gain=0.001, baseline_threshold=1.5),
            skip_2p_handshake=True,
            punish_on_movement_duration=0.1,
            delay_after_handshake=0.5,
        ),
    )


def mock_session() -> AindBehaviorSessionModel:
    """Generates a mock AindBehaviorSessionModel model"""
    return AindBehaviorSessionModel(
        date=datetime.datetime.now(tz=datetime.timezone.utc),
        experiment="BciNoMovement",
        root_path="c://data",
        remote_path=None,
        subject="Mouse007",
        notes="test session",
        experiment_version="",
        allow_dirty_repo=False,
        skip_hardware_validation=False,
        experimenter=["Foo", "Bar"],
    )


def mock_subject_database() -> db.SubjectDataBase:
    """Generates a mock database object"""
    database = db.SubjectDataBase()
    database.add_subject("test", db.SubjectEntry(task_logic_target="stageA"))
    database.add_subject("test2", db.SubjectEntry(task_logic_target="does_not_exist"))
    return database


def main(path_seed: str = "./local/{schema}.json"):

    example_session = mock_session()
    example_rig = mock_rig()
    example_task_logic = mock_task_logic()
    example_database = mock_subject_database()

    os.makedirs(os.path.dirname(path_seed), exist_ok=True)

    models = [example_task_logic, example_session, example_rig, example_database]

    for model in models:
        with open(path_seed.format(schema=model.__class__.__name__), "w", encoding="utf-8") as f:
            f.write(model.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
