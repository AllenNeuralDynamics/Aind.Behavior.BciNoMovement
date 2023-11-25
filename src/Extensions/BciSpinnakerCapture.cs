using System.ComponentModel;
using Bonsai.Spinnaker;
using SpinnakerNET;
using OpenCV.Net;

[Description("Configures and initializes a Spinnaker camera for triggered acquisition.")]
public class BciSpinnakerCapture : SpinnakerCapture
{
    public BciSpinnakerCapture()
    {
        ExposureTime = 5000;
        Binning = 1;
        Gain = 5;
        Gamma = 0.4;
        ImageSize = new Size(1420, 1080);
    }

    [Description("The duration of each individual exposure, in microseconds. In general, this should be 1 / frameRate - 1 millisecond to prepare for next trigger.")]
    public double ExposureTime { get; set; }

    [Description("The gain of the sensor.")]
    public double Gain { get; set; }

    [Description("The size of the binning area of the sensor, e.g. a binning size of 2 specifies a 2x2 binning region.")]
    public int Binning { get; set; }

    [Description("The gamma calibration value of the sensor.")]
    public double Gamma { get; set; }

    [Description("The gamma calibration value of the sensor.")]
    public Size ImageSize { get; set; }

    protected override void Configure(IManagedCamera camera)
    {
        try { camera.AcquisitionStop.Execute(); }
        catch { }
        camera.GammaEnable.Value = true;
        camera.Gamma.Value = Gamma;
        camera.GainAuto.Value = GainAutoEnums.Off.ToString();
        camera.Gain.Value = Gain;
        camera.ExposureAuto.Value = ExposureAutoEnums.Off.ToString();
        camera.ExposureMode.Value = ExposureModeEnums.Timed.ToString();
        camera.ExposureTime.Value = ExposureTime;
        camera.Height.Value = ImageSize.Height;
        camera.Width.Value = ImageSize.Width;
        camera.OffsetX.Value = 0;
        camera.OffsetY.Value = 0;
        camera.BinningSelector.Value = BinningSelectorEnums.All.ToString();
        camera.BinningHorizontalMode.Value = BinningHorizontalModeEnums.Sum.ToString();
        camera.BinningVerticalMode.Value = BinningVerticalModeEnums.Sum.ToString();
        camera.BinningHorizontal.Value = Binning;
        camera.BinningVertical.Value = Binning;
        camera.AcquisitionFrameRateEnable.Value = false;
        camera.AdcBitDepth.Value = AdcBitDepthEnums.Bit10.ToString();
        camera.PixelFormat.Value = PixelFormatEnums.Mono8.ToString();
        camera.IspEnable.Value = false;
        camera.TriggerMode.Value = TriggerModeEnums.On.ToString();
        camera.TriggerSelector.Value = TriggerSelectorEnums.FrameStart.ToString();
        camera.TriggerSource.Value = TriggerSourceEnums.Line0.ToString();
        camera.TriggerOverlap.Value = TriggerOverlapEnums.ReadOut.ToString();
        camera.TriggerActivation.Value = TriggerActivationEnums.RisingEdge.ToString();
        camera.DeviceLinkThroughputLimit.Value = camera.DeviceLinkThroughputLimit.Max;
        base.Configure(camera);
    }
}
