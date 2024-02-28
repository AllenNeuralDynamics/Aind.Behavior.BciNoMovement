using Bonsai;
using System;
using System.ComponentModel;
using System.Linq;
using System.Reactive.Linq;
using BciNoMovementDataSchema.BciNoMovementTask;

[Combinator]
[Description("")]
[WorkflowElementCategory(ElementCategory.Transform)]
public class ModifyManipulatorResetPosition
{
    public IObservable<BciNoMovementTaskLogic> Process(IObservable<Tuple<BciNoMovementTaskLogic, Point3d>> source)
    {
        return source.Select(value => {
            var taskLogic = value.Item1;
            var point = value.Item2;
            taskLogic.ManipulatorResetPosition = point;
            return taskLogic;
        });
    }

    public IObservable<BciNoMovementTaskLogic> Process(IObservable<Tuple<BciNoMovementTaskLogic, OpenCV.Net.Point3d>> source)
    {
        return source.Select(value => {
            var taskLogic = value.Item1;
            var point = value.Item2;
            Point3d point3d = new Point3d{
                X = point.X,
                Y = point.Y,
                Z = point.Z
            };
            taskLogic.ManipulatorResetPosition = point3d;
            return taskLogic;
        });
    }
}
