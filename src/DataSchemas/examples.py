import json

from pyd_rig import (
    Axis,
    BciNoMovementRig,
    ColorProcessing,
    HarpBoard,
    Networking,
    Operation,
    SpinnakerCamera,
    ZaberAxis,
    ZaberGenericCommand,
    ZaberManipulator,
    ZmqConnection,
)
from pyd_session import BciNoMovementSession, BciNoMovementTaskLogic, Control, Point3d

zaberCommands = []


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
        velocity=9999999,
        acceleration=9999999,
        spoutAxis=Axis.X,
        genericCommands=zaberCommands,
        xAxis=ZaberAxis(deviceIndex=0, axisIndex=1),
        yAxis=ZaberAxis(deviceIndex=0, axisIndex=2),
        zAxis=ZaberAxis(deviceIndex=1, axisIndex=1),
    ),
    networking=Networking(
        zmqPublisher=ZmqConnection(connectionString="@tcp://localhost:5556", topic="bci-no-movement"),
        zmqSubscriber=ZmqConnection(connectionString="@tcp://localhost:5557", topic="bci-no-movement"),
    ),
    operation=Operation(loadCellOffset=[0, 0, 0, 0, 0, 0, 0, 0], loadCellIndex=0),
)


task_logic_settings = BciNoMovementTaskLogic(
    schema_version="0.0.1",
    describedBy="https://github.com/AllenNeuralDynamics/aind-bci-no-movement/blob/main/src/DataSchemas/bci-no-movement-tasklogic.json",
    enableSoundOnRewardZoneEntry=True,
    interTrialInterval=0.5,
    lickResponseTime=2,
    maxTrialDuration=20,
    noMovementTimeBeforeTrial=0.5,
    rewardConsumeTime=2,
    valveOpenTime=0.1,
    waitForLick=True,
    farPositionOffset=30,
    manipulatorResetPosition=Point3d(x=43, y=-2, z=0.26),
    waitMicroscopeTime=0.5,
    bciPassiveControl=Control(gain=0.002, baselineThreshold=5000),
    noMovementPassiveControl=Control(gain=0.002, baselineThreshold=5000, lowPassCutOff=50, highPassCutOff=0.001),
    bciActiveControl=Control(gain=0.001, baselineThreshold=1.5),
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
    subject="test-subject_number_2",
    version="0.0.1",
)


BciNoMovementRig.model_validate(rig)
BciNoMovementTaskLogic.model_validate(task_logic_settings)
BciNoMovementSession.model_validate(session_info)


rig.write_standard_file("local/Rigs")
task_logic_settings.write_standard_file("local/TaskLogic")
session_info.write_standard_file("local/Subjects")
