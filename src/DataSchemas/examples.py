import json
from pyd_rig import (
    BciNoMovementRig,
    HarpBoard,
    SpinnakerCamera,
    ZaberManipulator,
    ZaberGenericCommand,
    Axis,
    ColorProcessing,
    Networking,
    ZmqConnection,
    Operation,
)
from pyd_session import BciNoMovementSession, BciNoMovementTaskLogic, Point3d

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
        genericCommands=[],
    ),
    networking=Networking(
        zmqPublisher=ZmqConnection(
            connectionString="@tcp://localhost:5556", topic="bci-no-movement"
        ),
        zmqSubscriber=ZmqConnection(
            connectionString="@tcp://localhost:5557", topic="bci-no-movement"
        ),
    ),
    operation=Operation(loadCellOffset=[0, 0, 0, 0, 0, 0, 0, 0]),
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
    farPositionOffset=80000,
    closePosition=100000,
    manipulatorResetPosition=Point3d(x=100000, y=100000, z=200000),
    waitMicroscopeTime=0.5,
    bciBaselineThreshold=0.1,
    movementBaselineThreshold=10000,
    passiveGain=1,
    bciGain=1,
    skip2pHandshake=False,
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
