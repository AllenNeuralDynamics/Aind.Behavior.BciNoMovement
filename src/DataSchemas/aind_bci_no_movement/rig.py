from enum import Enum
from typing import List, Optional

import aind_behavior_services.rig as rig
from aind_behavior_services.rig import AindBehaviorRigModel
from aind_data_schema.base import AindModel
from pydantic import BaseModel, Field


class Axis(str, Enum):
    X = 1
    Y = 2
    Z = 3
    NONE = 0


class ZaberGenericCommand(AindModel):
    command: str
    axis: int = Field(default=0, description="Motor to send the instruction to.")
    device: int = Field(default=None, ge=0, description="Device number.")


class ZaberAxis(AindModel):
    device_index: int = Field(ge=0, description="Device number.")
    axis_index: int = Field(ge=0, description="Motor to send the instruction to.")


class ZaberManipulator(AindModel):
    com_port: str = Field(default="COM1", description="COM port of the manipulator.")
    generic_commands: List[ZaberGenericCommand] = Field(
        [], description="List of generic commands to send to the manipulator."
    )
    spout_axis: Axis = Field(default=Axis.X, description="Axis of the spout.")
    velocity: float = Field(default=10, ge=0, description="Maximum speed of the manipulator.")
    acceleration: float = Field(default=1299.63, ge=0, description="Acceleration of the manipulator.")
    x_axis: ZaberAxis = Field(description="X-axis mapping.")
    y_axis: ZaberAxis = Field(description="Y-axis mapping.")
    z_axis: ZaberAxis = Field(description="Z-axis mapping.")


class ZmqConnection(AindModel):
    connection_string: str = Field(default="@tcp://localhost:5556")
    topic: str = Field(default="")


class Networking(AindModel):
    zmq_publisher: ZmqConnection = Field(
        default=ZmqConnection(connection_string="@tcp://localhost:5556", topic="bci-no-movement")
    )
    zmq_subscriber: ZmqConnection = Field(
        default=ZmqConnection(connection_string="@tcp://localhost:5557", topic="bci-no-movement")
    )


class Operation(AindModel):
    load_cell_offset: List[int] = Field(
        default=[0, 0, 0, 0, 0, 0, 0, 0],
        min_items=8,
        max_items=8,
        description="Bias offset of a specific loadcell channel.",
    )
    load_cell_index: int = Field(
        default=0,
        ge=0,
        le=7,
        description="Index of the loadcell channel to use.",
    )


class BciNoMovementRig(AindBehaviorRigModel):
    harp_behavior: rig.HarpBehavior = Field(..., description="Harp behavior")
    harp_load_cell: rig.HarpLoadCells = Field(..., description="Harp load cells")
    harp_clock: rig.HarpClockSynchronizer = Field(..., description="Harp clock synchronizer")
    camera_0: rig.SpinnakerCamera = Field(..., description="Required spinnaker camera")
    camera_1: Optional[rig.SpinnakerCamera] = Field(default=None, description="Optional spinnaker camera")
    zaber_manipulator: ZaberManipulator = Field(..., description="Zaber manipulator")
    networking: Networking = Field(default=Networking(), validate_default=True)
    operation: Operation = Field(default=Operation(), validate_default=True)


def schema() -> BaseModel:
    return BciNoMovementRig
