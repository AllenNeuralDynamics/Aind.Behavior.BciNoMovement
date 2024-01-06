# Import core types
import json
from pydantic import Field
from typing import Optional

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


class Control(AindModel):
    baselineThreshold: float = Field(
        default=0,
        ge=0,
        description="The threshold to be applied to the signal to define baseline",
    )
    gain: float = Field(default=1, description="The gain to be applied to the signal")
    lowPassCutOff: float = Field(
        default=-1, description="Low pass cut off frequency(Hz)"
    )
    highPassCutOff: float = Field(
        default=-1, description="High pass cut off frequency(Hz)"
    )


class BciNoMovementTaskLogic(AindCoreModel):
    valveOpenTime: float = Field(
        default=0.010, ge=0, description="Time valve remains open (s)"
    )
    waitMicroscopeTime: float = Field(
        default=0,
        ge=0,
        description="Interval (s) after the animal successfully exists the quiescence period.",
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
    farPositionOffset: float = Field(
        default=8,
        ge=0,
        description="Offset (mm) from the close position to the far position.",
    )
    manipulatorResetPosition: Point3d = Field(
        default=Point3d(), description="Position (mm) to reset the manipulator to."
    )
    bciActiveControl: Control = Field(
        default=Control(), description="BCI mode active component control parameters (Displacement = gain * Volt * Seconds)"
    )
    bciPassiveControl: Control = Field(
        default=Control(), description="BCI mode passive component control parameters (Displacement = gain * Seconds)"
    )
    noMovementPassiveControl: Control = Field(
        default=Control(), description="No movement mode passive control parameters (Displacement = gain * Seconds)"
    )
    skip2pHandshake: bool = Field(default=False, description="Skip 2p handshake")
    punishOnMovementDuration: float = Field(
        default=0,
        ge=0,
        description="The duration (s) that the spout will stop updating if the animal moves during the trial.",
    )
