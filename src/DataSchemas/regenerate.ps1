& python "src\DataSchemas\pyd_export_models.py" "src\DataSchemas\"
& bonsai.sgen --schema "src\DataSchemas\bci-no-movement-rig.json" --namespace BciNoMovementDataSchema.Rig --root BciNoMovementRig --output "src\Extensions\BciNoMovementRig.cs" --serializer NewtonsoftJson YamlDotNet
& bonsai.sgen --schema "src\DataSchemas\bci-no-movement-session.json" --namespace BciNoMovementDataSchema.Session --root BciNoMovementSession --output "src\Extensions\BciNoMovementSession.cs" --serializer NewtonsoftJson YamlDotNet
& bonsai.sgen --schema "src\DataSchemas\bci-no-movement-tasklogic.json" --namespace BciNoMovementDataSchema.TaskLogic --root BciNoMovementTaskLogic --output "src\Extensions\BciNoMovementTaskLogic.cs" --serializer NewtonsoftJson YamlDotNet
