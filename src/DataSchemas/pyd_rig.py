from pydantic import Field
from enum import Enum, IntEnum
from typing import List

# Import aind-datas-schema types
from aind_data_schema.base import AindModel, AindCoreModel


class HarpDeviceType(str, Enum):
    CUSTOM = "custom"
    BEHAVIOR = "behavior"
    CLOCKSYNCHRONIZER = "clockSynchronizer"
    TIMESTAMPGENERATORGEN3 = "timestampGeneratorGen3"
    LOADCELLS = "loadCells"


class HarpBoard(AindModel):
    portName: str
    serialNumber: str = None
    deviceName: str = None


class ColorProcessing(str, Enum):
    Default = "Default"
    NoColorProcessing = "NoColorProcessing"


class SpinnakerCamera(AindModel):
    serialNumber: str
    binning: int = Field(default=1, ge=1, description="Binning factor.")
    colorProcessing: ColorProcessing = Field(
        Default=ColorProcessing.Default, description="Color processing."
    )
    exposure: int = Field(default=1000, ge=0, description="Exposure time (us).")
    frameRate: int = Field(default=60, ge=0, description="Frame rate (Hz).")
    gain: float = Field(default=0, ge=0, description="Gain (dB).")


class Axis(IntEnum):
    X = 1
    Y = 2
    Z = 3
    NONE = 0


class ZaberGenericCommand(AindModel):
    command: str
    axis: int = Field(default=0, description="Motor to send the instruction to.")
    device: int = Field(default=None, ge=0, description="Device number.")


class ZaberAxis(AindModel):
    deviceIndex: int = Field(ge=0, description="Device number.")
    axisIndex: int = Field(ge=0, description="Motor to send the instruction to.")


class ZaberManipulator(AindModel):
    comPort: str = Field(default="COM1", description="COM port of the manipulator.")
    genericCommands: List[ZaberGenericCommand] = Field(
        [], description="List of generic commands to send to the manipulator."
    )
    spoutAxis: Axis = Field(default=Axis.X, description="Axis of the spout.")
    maxSpeed: float = Field(
        default=10, ge=0, description="Maximum speed of the manipulator."
    )
    acceleration: float = Field(
        default=1299.63, ge=0, description="Acceleration of the manipulator."
    )
    zaberAxisLookUpTable: dict[Axis, ZaberAxis] = Field(default={}, description="Manipulator axis mapping.")


class ZmqConnection(AindModel):
    connectionString: str = Field(default="@tcp://localhost:5556")
    topic: str = Field(default="")


class Networking(AindModel):
    zmqPublisher: ZmqConnection = Field(
        default=ZmqConnection(
            connectionString="@tcp://localhost:5556", topic="bci-no-movement"
        )
    )
    zmqSubscriber: ZmqConnection = Field(
        default=ZmqConnection(
            connectionString="@tcp://localhost:5557", topic="bci-no-movement"
        )
    )


class Operation(AindModel):
    loadCellOffset: List[int] = Field(
        default=[0, 0, 0, 0, 0, 0, 0, 0],
        min_items=8,
        max_items=8,
        description="Bias offset of a specific loadcell channel.",
    )
    loadCellIndex: int = Field(
        default=0,
        ge=0,
        le=7,
        description="Index of the loadcell channel to use.",
    )


class BciNoMovementRig(AindCoreModel):
    harpBehaviorBoard: HarpBoard
    harpLoadCellsBoard: HarpBoard
    harpTimestampGeneratorGen3: HarpBoard
    camera0: SpinnakerCamera
    camera1: SpinnakerCamera = Field(default=None)
    zaberManipulator: ZaberManipulator
    networking: Networking = Field(default=Networking())
    operation: Operation = Field(default=Operation())
