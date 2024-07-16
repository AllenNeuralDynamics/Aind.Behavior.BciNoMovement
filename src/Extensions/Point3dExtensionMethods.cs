using System;
using OpenCV.Net;

namespace BciNoMovementDataSchema.TaskLogic
{
    public partial class Point3d
    {
        public OpenCV.Net.Point3d ToOpenCVPoint3d()
        {
            return new OpenCV.Net.Point3d
            {
                X = X,
                Y = Y,
                Z = Z
            };
        }

        public double this[int axis]
        {
            get
            {
                switch (axis)
                {
                    case 0:
                        return X;
                    case 1:
                        return Y;
                    case 2:
                        return Z;
                    default:
                        throw new IndexOutOfRangeException("Axis is out of bounds.");
                }
            }

            set
            {
                switch (axis)
                {
                    case 0:
                        X = value;
                        break;
                    case 1:
                        Y = value;
                        break;
                    case 2:
                        Z = value;
                        break;
                    default:
                        throw new IndexOutOfRangeException("Axis is out of bounds.");
                }
            }
        }

        public static Point3d operator +(Point3d el1, Point3d el2)
        {
            return new Point3d()
            {
                X = el1.X + el2.X,
                Y = el1.Y + el2.Y,
                Z = el1.Z + el2.Z
            };
        }

        public static Point3d operator -(Point3d el1, Point3d el2)
        {
            return new Point3d()
            {
                X = el1.X - el2.X,
                Y = el1.Y - el2.Y,
                Z = el1.Z - el2.Z
            };
        }

        public static Point3d operator *(Point3d el1, float gain)
        {
            return new Point3d()
            {
                X = el1.X * gain,
                Y = el1.Y * gain,
                Z = el1.Z * gain
            };
        }
        public static Point3d operator *(Point3d el1, Point3d el2)
        {
            return new Point3d()
            {
                X = el1.X * el2.X,
                Y = el1.Y * el2.Y,
                Z = el1.Z * el2.Z
            };

        }

        public static Point3d operator /(Point3d el1, Point3d el2)
        {
            return new Point3d()
            {
                X = el1.X / el2.X,
                Y = el1.Y / el2.Y,
                Z = el1.Z / el2.Z
            };

        }

        public override bool Equals(object obj)
        {
            if (obj is Point3d)
            {
                var other = obj as Point3d;
                return X == other.X && Y == other.Y && Z == other.Z;
            }
            else
            {
                return base.Equals(obj);
            }
        }

        public override int GetHashCode()
        {
            return X.GetHashCode() ^ Y.GetHashCode() ^ Z.GetHashCode();
        }

        public static bool operator ==(Point3d x, Point3d y)
        {
            return Equals(x, y);
        }

        public static bool operator !=(Point3d x, Point3d y)
        {
            return !Equals(x, y);
        }

        public static bool Equals(Point3d el1, Point3d el2)
        {
            return el1.X == el2.X && el1.Y == el2.Y && el1.Z == el2.Z;
        }
    }
}

