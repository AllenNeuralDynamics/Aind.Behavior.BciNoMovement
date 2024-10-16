from enum import IntEnum
from typing import List, Literal, Optional

import aind_behavior_services.rig as rig
from aind_behavior_services.calibration import load_cells as lc
from pydantic import BaseModel, Field

__version__ = "0.0.1"


class Axis(IntEnum):
    X = 1
    Y = 2
    Z = 3
    NONE = 0


class ZaberGenericCommand(BaseModel):
    command: str = Field(..., description="Command to send to the manipulator.")
    axis: Optional[int] = Field(default=None, ge=0, description="Motor to send the instruction to.")
    device: Optional[int] = Field(default=None, ge=0, description="Device number.")


class ZaberAxis(BaseModel):
    device_index: int = Field(..., ge=0, description="Device number.")
    axis_index: int = Field(..., ge=0, description="Motor to send the instruction to.")
    acceleration: Optional[float] = Field(default=None, ge=0, description="Acceleration of the manipulator (mm/s2).")
    velocity: Optional[float] = Field(default=None, ge=0, description="Maximum speed of the manipulator (mm/s).")
    lower_limit: Optional[float] = Field(default=None, description="Lower limit of the manipulator (mm).")
    upper_limit: Optional[float] = Field(default=None, description="Upper limit of the manipulator (mm).")


class ZaberManipulator(BaseModel):
    com_port: str = Field(..., description="COM port of the manipulator.")
    generic_commands: List[ZaberGenericCommand] = Field(
        default=[], description="List of generic commands to send to the manipulator."
    )
    spout_axis: Axis = Field(default=Axis.X, description="Axis of the spout.")
    x_axis: ZaberAxis = Field(..., description="X-axis mapping.")
    y_axis: ZaberAxis = Field(..., description="Y-axis mapping.")
    z_axis: ZaberAxis = Field(..., description="Z-axis mapping.")


class ZmqConnection(BaseModel):
    connection_string: str = Field(default="@tcp://localhost:5556", description="Connection string.")
    topic: str = Field(default="", description="Topic to subscribe to.")


class Networking(BaseModel):
    zmq_publisher: ZmqConnection = Field(
        default=ZmqConnection(connection_string="@tcp://localhost:5556", topic="bci-no-movement"), validate_default=True
    )
    zmq_subscriber: ZmqConnection = Field(
        default=ZmqConnection(connection_string="@tcp://localhost:5557", topic="bci-no-movement"), validate_default=True
    )


class Operation(BaseModel):
    load_cell_index: lc.LoadCellChannel = Field(
        default=0,
        description="Index of the load cell channel to use.",
    )


class BciNoMovementRig(rig.AindBehaviorRigModel):
    version: Literal[__version__] = __version__
    harp_behavior: rig.HarpBehavior = Field(..., description="Harp behavior")
    harp_load_cells: lc.LoadCells = Field(..., description="Harp load cells")
    harp_clock_generator: rig.HarpClockGenerator = Field(..., description="Harp clock timestamp generator gen 3")
    triggered_camera_controller: rig.CameraController[rig.SpinnakerCamera] = Field(
        ..., description="Required camera controller to triggered cameras."
    )
    monitoring_camera_controller: Optional[rig.CameraController[rig.WebCamera]] = Field(
        default=None, description="Optional camera controller for monitoring cameras."
    )
    manipulator: ZaberManipulator = Field(..., description="Zaber manipulator")
    networking: Networking = Field(default=Networking(), validate_default=True)
    operation: Operation = Field(default=Operation(), validate_default=True)
