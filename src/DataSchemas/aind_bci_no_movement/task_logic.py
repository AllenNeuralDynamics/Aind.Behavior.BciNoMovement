from typing import Optional

from aind_behavior_services.task_logic import AindBehaviorTaskLogicModel
from aind_data_schema.base import AindModel
from pydantic import BaseModel, Field


class Point3d(AindModel):
    x: float = Field(default=0, description="X coordinate")
    y: float = Field(default=0, description="Y coordinate")
    z: float = Field(default=0, description="Z coordinate")


class Control(AindModel):
    baseline_threshold: float = Field(
        default=0,
        ge=0,
        description="The threshold to be applied to the signal to define baseline",
    )
    gain: float = Field(default=1, description="The gain to be applied to the signal")
    low_pass_cut_off: Optional[float] = Field(default=None, description="Low pass cut off frequency(Hz)")
    high_pass_cut_off: Optional[float] = Field(default=None, description="High pass cut off frequency(Hz)")


class BciNoMovementTaskLogic(AindBehaviorTaskLogicModel):
    valve_open_time: float = Field(default=0.010, ge=0, description="Time valve remains open (s)")
    wait_microscope_time: float = Field(
        default=0,
        ge=0,
        description="Interval (s) after the animal successfully exists the quiescence period.",
    )
    low_activity_time: float = Field(
        default=1,
        ge=0,
        description="Duration (s) BCI activity must stay low before starting a new trial.",
    )
    lick_response_time: float = Field(
        default=2,
        ge=0,
        description="Interval (s) for the animal to collect reward. Only applies if waitForLick is true.",
    )
    wait_for_lick: bool = Field(
        default=True,
        description="Determines whether the animal must lick to trigger reward delivery. If false, reward is immediately delivered.",
    )
    enable_sound_on_reward_zone_entry: bool = Field(
        default=True, description="Enables audio feedback on reward zone entry."
    )
    no_movement_time_before_trial: float = Field(
        default=0,
        ge=0,
        description="Interval (s) subjects must not move for to start a new trial.",
    )
    inter_trial_interval: float = Field(default=0, ge=0, description="Interval (s) between trials.")
    reward_consume_time: float = Field(default=2, ge=0, description="Duration (s) for the animal to consume reward.")
    max_trial_duration: float = Field(default=20, ge=0, description="Maximum duration (s) of a trial.")
    far_position_offset: float = Field(
        default=8,
        ge=0,
        description="Offset (mm) from the close position to the far position.",
    )
    manipulator_reset_position: Point3d = Field(
        default=Point3d(), description="Position (mm) to reset the manipulator to."
    )
    bci_passive_control: Control = Field(default=Control(), description="BCI control parameters", validate_default=True)
    no_movement_passive_control: Control = Field(
        default=Control(), description="No movement control parameters", validate_default=True
    )
    bci_active_control: Control = Field(
        default=Control(), description="BCI active control parameters", validate_default=True
    )
    skip_2p_handshake: bool = Field(default=False, description="Skip 2p handshake")
    punish_on_movement_duration: float = Field(
        default=0,
        ge=0,
        description="The duration (s) that the spout will stop updating if the animal moves during the trial.",
    )


def schema() -> BaseModel:
    return BciNoMovementTaskLogic
