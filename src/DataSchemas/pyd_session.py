# Import core types
import json
from pydantic import Field

# Import aind-datas-schema types
from aind_data_schema.base import AindModel, AindCoreModel


class BciNoMovementSession(AindCoreModel):
    experiment: str = Field(..., description="Name of the experiment")
    rootPath: str = Field(..., description="Root path of the experiment")
    subject: str = Field(..., description="Name of the subject")
    version: str = Field(..., description="Version of the experiment")
    allowDirty: bool = Field(
        False, description="Allow code to run from dirty repository"
    )
    remoteDataPath: str = Field(
        default="",
        description="Path to remote data. If empty, no attempt to copy data will be made",
    )
    rngSeed: int = Field(
        0,
        description="Seed of the random number generator. If 0 it will be randomized.",
    )
    notes: str = Field(None, description="Notes about the experiment")
    commitHash: str = Field(None, description="Commit hash of the repository")


class Point3d(AindModel):
    x: float = Field(default=0, description="X coordinate")
    y: float = Field(default=0, description="Y coordinate")
    z: float = Field(default=0, description="Z coordinate")


class BciNoMovementTaskLogic(AindCoreModel):
    valveOpenTime: float = Field(
        default=0.010, ge=0, description="Time valve remains open (s)"
    )
    waitMicroscopeTime: float = Field(
        default=0,
        ge=0,
        description="Interval (s) after the animal successfully exists the quiescence period.",
    )
    lowActivityTime: float = Field(
        default=1,
        ge=0,
        description="Duration (s) BCI activity must stay low before starting a new trial.",
    )
    lickResponseTime: float = Field(
        default=2,
        ge=0,
        description="Interval (s) for the animal to collect reward. Only applies if waitForLick is true.",
    )
    waitForLick: bool = Field(
        default=True,
        description="Determines whether the animal must lick to trigger reward delivery. If false, reward is immediately delivered.",
    )
    enableSoundOnRewardZoneEntry: bool = Field(
        default=True, description="Enables audio feedback on reward zone entry."
    )
    noMovementTimeBeforeTrial: float = Field(
        default=0,
        ge=0,
        description="Interval (s) subjects must not move for to start a new trial.",
    )
    interTrialInterval: float = Field(
        default=0, ge=0, description="Interval (s) between trials."
    )
    rewardConsumeTime: float = Field(
        default=2, ge=0, description="Duration (s) for the animal to consume reward."
    )
    maxTrialDuration: float = Field(
        default=20, ge=0, description="Maximum duration (s) of a trial."
    )
    closePosition: float = Field(
        default=19, ge=0, description="Position (mm) of the close position."
    )
    farPositionOffset: float = Field(
        default=8,
        ge=0,
        description="Offset (mm) from the close position to the far position.",
    )
    manipulatorResetPosition: Point3d = Field(
        default=Point3d(), description="Position (mm) to reset the manipulator to."
    )
    bciBaselineThreshold: float = Field(
        default=0,
        ge=0,
        description="Bci Activity threshold applied during the baseline period.",
    )
    movementBaselineThreshold: float = Field(
        default=0,
        ge=0,
        description="Bci Activity threshold applied during the baseline period.",
    )
    passiveGain: float = Field(
        default=1, description="Passive gain applied to the movement of the spout."
    )
    bciGain: float = Field(
        default=1, description="BCI gain applied to the movement of the spout."
    )
