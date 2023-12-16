import json
import sys
from os import PathLike
from pathlib import Path

from pyd_rig import BciNoMovementRig
from pyd_session import BciNoMovementSession, BciNoMovementTaskLogic


def export(output_dir: PathLike):
    output_dir = Path(output_dir)

    with open(output_dir / "bci-no-movement-tasklogic.json", "w") as f:
        json_model = json.dumps(BciNoMovementTaskLogic.model_json_schema(), indent=3)
        json_model = json_model.replace("$defs", "definitions")
        f.write(json_model)

    with open(output_dir / "bci-no-movement-session.json", "w") as f:
        json_model = json.dumps(BciNoMovementSession.model_json_schema(), indent=3)
        json_model = json_model.replace("$defs", "definitions")
        f.write(json_model)

    with open(output_dir / "bci-no-movement-rig.json", "w") as f:
        json_model = json.dumps(BciNoMovementRig.model_json_schema(), indent=3)
        json_model = json_model.replace("$defs", "definitions")
        f.write(json_model)


if __name__ == "__main__":
    export(output_dir=sys.argv[1])
