import json
from pyd_rig import (
    BciNoMovementRig,
    HarpBoard,
    SpinnakerCamera,
    ZaberManipulator,
    ZaberGenericCommand,
    ZaberAxis,
    Axis,
    ColorProcessing,
    Networking,
    ZmqConnection,
    Operation,
)
from pyd_session import BciNoMovementSession, BciNoMovementTaskLogic, Point3d, Control


zaberCommands = [
    ZaberGenericCommand(command='set limit.home.pos 0', device=1, axis=1),
    ZaberGenericCommand(command='set limit.away.pos 1100000', device=1, axis=1),
    ZaberGenericCommand(command='set limit.home.pos 0', device=1, axis=2),
    ZaberGenericCommand(command='set limit.away.pos 1100000', device=1, axis=2),
    ZaberGenericCommand(command='set limit.home.pos 0', device=2, axis=1),
    ZaberGenericCommand(command='set limit.away.pos 150000', device=2, axis=1),
]


rig = BciNoMovementRig(
    schema_version="0.0.1",
    describedBy="https://github.com/AllenNeuralDynamics/aind-bci-no-movement/blob/main/src/DataSchemas/bci-no-movement-rig.json",
    harpBehaviorBoard=HarpBoard(portName="COM8"),
    harpLoadCellsBoard=HarpBoard(portName="COM7"),
    harpTimestampGeneratorGen3=HarpBoard(portName="COM9"),
    camera0=SpinnakerCamera(
        binning=1,
        colorProcessing=ColorProcessing.Default,
        exposure=2000,
        frameRate=200,
        gain=0,
        serialNumber="23381093",
    ),
    zaberManipulator=ZaberManipulator(
        comPort="COM10",
        maxSpeed=12,
        acceleration=1299.63,
        spoutAxis=Axis.Z,
        genericCommands=zaberCommands,
        zaberAxisLookUpTable={
            Axis.X: ZaberAxis(deviceIndex=0, axisIndex=0),
            Axis.Y: ZaberAxis(deviceIndex=0, axisIndex=1),
            Axis.Z: ZaberAxis(deviceIndex=1, axisIndex=1),
        }
    ),
    networking=Networking(
        zmqPublisher=ZmqConnection(
            connectionString="@tcp://localhost:5556", topic="bci-no-movement"
        ),
        zmqSubscriber=ZmqConnection(
            connectionString="@tcp://localhost:5557", topic="bci-no-movement"
        ),
    ),
    operation=Operation(loadCellOffset=[0, 0, 0, 0, 0, 0, 0, 0], loadCellIndex=0),
)


task_logic_settings = BciNoMovementTaskLogic(
    schema_version="0.0.1",
    describedBy="https://github.com/AllenNeuralDynamics/aind-bci-no-movement/blob/main/src/DataSchemas/bci-no-movement-tasklogic.json",
    enableSoundOnRewardZoneEntry=True,
    interTrialInterval=0.5,
    lickResponseTime=2,
    lowActivityTime=1,
    maxTrialDuration=20,
    noMovementTimeBeforeTrial=0.5,
    rewardConsumeTime=2,
    valveOpenTime=0.1,
    waitForLick=True,
    farPositionOffset=30000,
    manipulatorResetPosition=Point3d(x=0, y=0, z=0),
    waitMicroscopeTime=0.5,
    noMovementControl=Control(
        gain=20, baselineThreshold=20000, lowPassCutOff=50, highPassCutOff=0.001
    ),
    bciControl=Control(gain=10, baselineThreshold=1.5),
    skip2pHandshake=True,
    punishOnMovementDuration=0.1,
)

session_info = BciNoMovementSession(
    schema_version="0.0.1",
    describedBy="https://github.com/AllenNeuralDynamics/aind-bci-no-movement/blob/main/src/DataSchemas/bci-no-movement-session.json",
    allowDirty=True,
    experiment="bci-no-movement",
    notes="Test session",
    rootPath="C:/Data/",
    remoteDataPath="C:/DataRemote/",
    subject="test-subject",
    version="0.0.1",
)


BciNoMovementRig.model_validate(rig)
BciNoMovementTaskLogic.model_validate(task_logic_settings)
BciNoMovementSession.model_validate(session_info)


rig.write_standard_file("local/Rigs")
task_logic_settings.write_standard_file("local/TaskLogic")
session_info.write_standard_file("local/Subjects")
