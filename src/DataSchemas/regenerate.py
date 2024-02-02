from pathlib import Path

import aind_bci_no_movement.rig
import aind_bci_no_movement.session
import aind_bci_no_movement.task_logic
from aind_behavior_services.utils import convert_pydantic_to_bonsai

SCHEMA_ROOT = Path("./src/DataSchemas/")
EXTENSIONS_ROOT = Path("./src/Extensions/")
NAMESPACE_PREFIX = "BciNoMovementDataSchema"


def main():
    models = {
        "bci_no_movement_task": aind_bci_no_movement.task_logic.schema(),
        "bci_no_movement_session": aind_bci_no_movement.session.schema(),
        "bci_no_movement_rig": aind_bci_no_movement.rig.schema(),
    }
    convert_pydantic_to_bonsai(
        models, schema_path=SCHEMA_ROOT, output_path=EXTENSIONS_ROOT, namespace_prefix=NAMESPACE_PREFIX
    )


if __name__ == "__main__":
    main()
