import datetime
import aind_behavior_services.rig as srig
import aind_bci_no_movement.rig as rig
import aind_bci_no_movement.session as session
import aind_bci_no_movement.task_logic as task_logic
from aind_bci_no_movement.rig import BciNoMovementRig
from aind_bci_no_movement.session import BciNoMovementSession
from aind_bci_no_movement.task_logic import BciNoMovementTaskLogic
import os

zaberCommands = []


rig_settings = rig.BciNoMovementRig(
    computer_name=os.environ["COMPUTERNAME"],
    rig_name="bci-no-movement-rig",
    schema_version="0.0.1",
    describedBy="https://github.com/AllenNeuralDynamics/aind-bci-no-movement/blob/main/src/DataSchemas/bci-no-movement-rig.json",
    harp_behavior=srig.HarpBehavior(port_name="COM8"),
    harp_load_cell=srig.HarpLoadCells(port_name="COM7"),
    harp_clock=srig.HarpClockSynchronizer(port_name="COM9"),
    camera_0=srig.SpinnakerCamera(
        binning=1,
        exposure=2000,
        frame_rate=200,
        gain=0,
        serial_number="23381093",
    ),
    zaber_manipulator=rig.ZaberManipulator(
        com_port="COM10",
        velocity=9999999,
        acceleration=9999999,
        spout_axis=rig.Axis.X,
        generic_commands=zaberCommands,
        x_axis=rig.ZaberAxis(device_index=0, axis_index=1),
        y_axis=rig.ZaberAxis(device_index=0, axis_index=2),
        z_axis=rig.ZaberAxis(device_index=1, axis_index=1),
    ),
    networking=rig.Networking(
        zmq_publisher=rig.ZmqConnection(connection_string="@tcp://localhost:5556", topic="bci-no-movement"),
        zmq_subscriber=rig.ZmqConnection(connection_string="@tcp://localhost:5557", topic="bci-no-movement"),
    ),
    operation=rig.Operation(load_cell_offset=[0, 0, 0, 0, 0, 0, 0, 0], load_cell_index=0),
)


task_logic_settings = task_logic.BciNoMovementTaskLogic(
    schema_version="0.0.1",
    describedBy="https://github.com/AllenNeuralDynamics/aind-bci-no-movement/blob/main/src/DataSchemas/bci-no-movement-tasklogic.json",
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
    bci_passive_control=task_logic.Control(gain=0.002, baseline_threshold=5000),
    no_movement_passive_control=task_logic.Control(
        gain=0.002, baseline_threshold=5000, low_pass_cut_off=50, high_pass_cut_off=0.001
    ),
    bci_active_control=task_logic.Control(gain=0.001, baseline_threshold=1.5),
    skip_2p_handshake=True,
    punish_on_movement_duration=0.1,
    delay_after_handshake=0.5,
)

session_info = session.BciNoMovementSession(
    describedBy="https://github.com/AllenNeuralDynamics/aind-bci-no-movement/blob/main/src/DataSchemas/bci-no-movement-session.json",
    allow_dirty_repo=True,
    experiment="bci-no-movement",
    notes="Test session",
    root_path="C:/Data/",
    remote_path="C:/DataRemote/",
    subject="test-subject_number_2",
    date=datetime.datetime.now(),
    experiment_version="0.0.0")


BciNoMovementRig.model_validate(rig_settings)
BciNoMovementTaskLogic.model_validate(task_logic_settings)
BciNoMovementSession.model_validate(session_info)


rig_settings.write_standard_file("local/Rigs")
task_logic_settings.write_standard_file("local/TaskLogic")
session_info.write_standard_file("local/Subjects")
