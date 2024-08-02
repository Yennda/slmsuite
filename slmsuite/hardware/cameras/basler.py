"""
Template for writing a subclass for camera hardware control in :mod:`slmsuite`.
Outlines which camera superclass functions must be implemented.
"""
from slmsuite.hardware.cameras.camera import Camera

from pypylon import pylon


class Basler(Camera):
    """
    Template for adding a new camera to :mod:`slmsuite`. Replace :class:`Template`
    with the desired subclass name. :class:`~slmsuite.hardware.cameras.camera.Camera` is the
    superclass that sets the requirements for :class:`Template`.

    Attributes
    ----------
    sdk : object
        Many cameras have a singleton SDK class which handles all the connected cameras
        of a certain brand. This is generally implemented as a class variable.
    cam : object
        Most cameras will wrap some handle which connects to the the hardware.
    """

    # Class variable (same for all instances of Template) pointing to a singleton SDK.
    sdk = None

    def __init__(
            self,
            serial="",
            pitch_um=None,
            verbose=True,
            **kwargs
    ):
        """
        Initialize camera and attributes.

        Parameters
        ----------
        serial : str
            TODO: Most SDKs identify different cameras by some serial number or string.
        pitch_um : (float, float) OR None
            Fill in extra information about the pixel pitch in ``(dx_um, dy_um)`` form
            to use additional calibrations.
            TODO: See if the SDK can pull this information directly from the camera.
        verbose : bool
            Whether or not to print extra information.
        **kwargs
            See :meth:`.Camera.__init__` for permissible options.
        """
        # TODO: Insert code here to initialize the camera hardware, load properties, etc.

        # Mandatory functions:
        # - Opening a connection to the device
        tlFactory = pylon.TlFactory.GetInstance()
        self.devices = tlFactory.EnumerateDevices()
        # selection of the camera with the specific id=serial
        id = int(serial)
        self.cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(self.devices[id]))
        self.cam.Open()

        # Other possibilities to consider:
        # - Loading a connection to the SDK, if applicable.
        # - Gathering parameters such a width, height, and bitdepth.

        # Finally, use the superclass constructor to initialize other required variables.
        super().__init__(
            (self.cam.Width.Value, self.cam.Height.Value),
            bitdepth=self.cam.PixelFormat.IntValue,
            pitch_um=pitch_um,
            name=serial,
            **kwargs
        )

        # ... Other setup.

    def close(self):
        """See :meth:`.Camera.close`."""
        self.cam.Close()  # TODO: Fill in proper function.
        del self.cam

    @staticmethod
    def info(verbose=True):
        """
        Discovers all cameras detected by the SDK.
        Useful for a user to identify the correct serial numbers / etc.

        Parameters
        ----------
        verbose : bool
            Whether to print the discovered information.

        Returns
        --------
        list of str
            List of serial numbers or identifiers.
        """
        if verbose:
            tlFactory = pylon.TlFactory.GetInstance()
            devices = tlFactory.EnumerateDevices()
            cameras = pylon.InstantCameraArray(min(len(devices), len(devices)))
            print("Number of available cameras: ", len(devices))

            # prints the list of available cameras
            for i, cam in enumerate(cameras):
                cam.Attach(tlFactory.CreateDevice(devices[i]))
                print(i, ". Device ", cam.GetDeviceInfo().GetModelName())
                print("\tGetDeviceGUID ", cam.GetDeviceInfo().GetDeviceGUID())
                cam.Close()

        serial_list = devices  # TODO: Fill in proper function.
        return serial_list

    ### Property Configuration ###

    def get_exposure(self):
        """See :meth:`.Camera.get_exposure`."""
        return self.cam.ExposureTime.GetValue() / 1e6

    def set_exposure(self, exposure_s):
        """See :meth:`.Camera.set_exposure`."""
        self.cam.ExposureTime.SetValue(1e6 * exposure_s)

    def set_woi(self, woi=None):
        """See :meth:`.Camera.set_woi`."""
        raise NotImplementedError()
        # Use self.cam to crop the window of interest.

    def _get_image_hw(self, timeout_s=1):
        """See :meth:`.Camera._get_image_hw`."""
        # The core method: grabs an image from the camera.
        # Note: the camera superclass' get_image function performs follow-on processing
        # (similar to how the SLM superclass' write method pairs with _write_hw methods
        # for each subclass) -- frame averaging, transformations, and so on -- so this
        # method should be limited to camera-interface specific functions.
        return self.cam.GrabOne(int(timeout_s * 1e6)).Array  # TODO: Fill in proper function.

    def _get_images_hw(self, timeout_s=1):
        """See :meth:`.Camera._get_images_hw`."""
        raise NotImplementedError()
        # Similar to the core method but for a batch of images.
        # This should be used if the camera has a hardware-specific method of grabbing
        # frame batches. If not defined, the superclass captures and averages sequential
        # _get_image_hw images.
        return self.cam.get_images_function()  # TODO: Fill in proper function.

    def flush(self):
        """See :meth:`.Camera.flush`."""
        pass
        # raise NotImplementedError()
        # Clears ungrabbed images from the queue
    def close(self):
        self.cam.Close()

if __name__ == "__main__":
    Basler.info()
