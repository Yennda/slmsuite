"""
Hardware control for AlliedVision cameras via the :mod:`vimba` interface.
Install :mod:`vimba` by following the instructions at [1]_. Include the
`numpy-export` flag in the `pip install` command, as the :class:`AlliedVision` class
makes use of these features. See especially the vimba python manual [2]_ for reference.

References
----------
.. [1] https://github.com/alliedvision/VimbaPython
.. [2] https://github.com/alliedvision/VimbaPython/blob/master/Documentation/Vimba%20Python%20Manual.pdf
"""

import time

import numpy as np

from slmsuite.hardware.cameras.camera import Camera

try:
    import vimba
except ImportError:
    print("vimba not installed. Install to use AlliedVision cameras.")


class AlliedVision(Camera):
    r"""
    AlliedVision camera.

    Attributes
    ----------
    sdk : vimba.Vimba
        AlliedVision SDK. Shared among instances of :class:`AlliedVision`.
    cam : vimba.Camera
        Object to talk with the desired camera.

    Caution
    ~~~~~~~~
    The AlliedVision SDK :mod:`vimba` includes protections to maintain camera connectivity:
    specifically, the SDK :class:`vimba.Vimba` and cameras :class:`vimba.Camera` are designed
    to be used in concert with ``with`` statements. Unforunately, this does not mesh with the
    architecture of :mod:`slmsuite`, where notebook-style operation is desired.
    Using ``with`` statements inside :class:`.AlliedVision` methods is likewise not an option,
    as the methods to :meth:`__enter__()` and :meth:`__exit__()` the ``with`` are time-consuming
    due to calls to :meth:`_open()` and :meth:`_close()` the objects, to the point of
    :math:`\mathcal{O}(\text{s})` overhead. :class:`.AlliedVision` disables these protections by
    calling :meth:`__enter__()` and :meth:`__exit__()` directly during :meth:`.__init__()` and
    :meth:`.close()`, instead of inside ``with`` statements.
    """

    sdk = None

    def __init__(self, serial="", verbose=True, **kwargs):
        """
        Initialize camera and attributes.

        Parameters
        ----------
        serial : str
            Serial number of the camera to open. If empty, defaults to the first camera in the list
            returned by `vimba.get_all_cameras()`.
        verbose : bool
            Whether or not to print extra information.
        kwargs
            See :meth:`.Camera.__init__` for permissible options.
        """
        if AlliedVision.sdk is None:
            if verbose:
                print("vimba initializing... ", end="")
            AlliedVision.sdk = vimba.Vimba.get_instance()
            AlliedVision.sdk.__enter__()
            if verbose:
                print("success")

        if verbose:
            print("Looking for cameras... ", end="")
        camera_list = AlliedVision.sdk.get_all_cameras()
        if verbose:
            print("success")

        serial_list = [cam.get_serial() for cam in camera_list]
        if serial == "":
            if len(camera_list) == 0:
                raise RuntimeError("No cameras found by vimba.")
            if len(camera_list) > 1 and verbose:
                print("No serial given... Choosing first of ", serial_list)

            self.cam = camera_list[0]
            serial = self.cam.get_serial()
        else:
            if serial in serial_list:
                self.cam = camera_list[serial_list.index(serial)]
            else:
                raise RuntimeError(
                    "Serial " + serial + " not found by vimba. Availible: ", serial_list
                )

        if verbose:
            print("vimba sn " "{}" " initializing... ".format(serial), end="")
        self.cam.__enter__()
        if verbose:
            print("success")

        super().__init__(
            self.cam.SensorWidth.get(),
            self.cam.SensorHeight.get(),
            bitdepth=int(self.cam.PixelSize.get()),
            dx_um=None,
            dy_um=None,
            **kwargs
        )
        self.name = serial
        self.cam.TriggerSource.set("Software")
        self.cam.TriggerSelector.set("FrameStart")
        self.cam.TriggerMode.set("Off")
        # ('SingleFrame', 0), ('MultiFrame', 1), ('Continuous', 2)
        self.cam.AcquisitionMode.set(2)
        self.cam.BinningHorizontal.set(1)
        self.cam.BinningVertical.set(1)
        # ('Off', 0), ('Once', 1), ('Continuous', 2)
        self.cam.ExposureAuto.set(0)
        # ('Timed', 1), ('TriggerWidth', 2), ('TriggerControlled', 3)
        self.cam.ExposureMode.set(1)
        # ('Off', 0), ('Once', 1), ('Continuous', 2)
        self.cam.GainAuto.set(0)

        # Initialize window variable, then set to max WOI
        self.window = None
        self.set_woi()
        self.default_shape = self.shape

    def close(self, close_sdk=True):
        """
        See :meth:`.Camera.close`

        Parameters
        ----------
        close_sdk : bool
            Whether or not to close the :mod:`vimba` instance.
        """
        self.cam.__exit__(None, None, None)

        if close_sdk:
            self.close_sdk()

    @classmethod
    def close_sdk(cls):
        """
        Close the :mod:`vimba` instance.
        """
        if cls.sdk is not None:
            cls.sdk.__exit__(None, None, None)
            cls.sdk = None

    ### Property Configuration ###

    def get_properties(self, properties=None):
        """
        Print the list of camera properties.

        Parameters
        ----------
        properties : dict or None
            The target camera's property dictionary. If `None`, the property
            dictionary is fetched from the camera associated with the calling instance.
        """
        if properties is None:
            properties = self.cam.__dict__.keys()

        for key in properties:
            try:
                prop = self.cam.__dict__[key]
                print(prop.get_name(), end="\t")
                print(prop.get(), end="\t")
                print(prop.get_unit(), end="\t")
                print(prop.get_description())
            except BaseException as e:
                print("Error accessing property dictionary.\n{}".format(e))

    def set_adc_bitdepth(self, bitdepth):
        """
        Set the digitization bitdepth.

        Parameters
        ----------
        bitdepth : int
            The digitization bitdepth.
        """
        bitdepth = int(bitdepth)

        for entry in self.cam.SensorBitDepth.get_all_entries():
            value = entry.as_tuple()  # (name : str, value : int)
            if str(bitdepth) in value[0]:
                self.cam.SensorBitDepth.set(value[1])
                break
            raise RuntimeError("ADC bitdepth {} not found.".format(bitdepth))

    def get_adc_bitdepth(self):
        """
        Get the digitization bitdepth.

        Returns
        -------
        int
            The digitization bitdepth.
        """
        value = str(self.cam.SensorBitDepth.get())
        bitdepth = int("".join(char for char in value if char.isdigit()))
        return bitdepth

    def get_exposure(self):
        """See :meth:`.Camera.get_exposure`."""
        return float(self.cam.ExposureTime.get()) / 1e6

    def set_exposure(self, exposure_s):
        """See :meth:`.Camera.set_exposure`."""
        self.cam.ExposureTime.set(float(exposure_s * 1e6))

    def set_woi(self, window=None):
        """See :meth:`.Camera.set_woi`."""
        return

    def get_image(self, timeout_s=1):
        """See :meth:`.Camera.get_image`."""
        # Convert timeout_s to ms
        frame = self.cam.get_frame(timeout_ms=int(1e3 * timeout_s))

        return self.transform(np.squeeze(frame.as_numpy_ndarray()))

    def flush(self, timeout_s=1e-3):
        """See :meth:`.Camera.flush`."""
        for _ in range(5):
            self.get_image()
        # TODO: implement full flush @ichr
        # t = time.time()
        # for x in range(10):
        #     print(x, time.time() - t)
        #     try:
        #         self.cam.get_frame(timeout_ms=int(1e3*timeout_s))
        #     except:
        # break   # Frame failed to return, we know we have flushed the buffer.

    def reset(self):
        """See :meth:`.Camera.reset`."""
        raise NotImplementedError()