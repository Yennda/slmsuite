"""
Template for writing a subclass for SLM hardware control in :mod:`slmsuite`.
Outlines which SLM superclass functions must be implemented.
"""
from .slm import SLM
import EXULUS_COMMAND_LIB as sdk
from thorlabs_fullscreen import send_to_slm
class Thorlabs(SLM):
    """
    Template for implementing a new SLM subclass. Replace :class:`Template`
    with the desired subclass name. :class:`~slmsuite.hardware.slms.slm.SLM` is the
    superclass that sets the requirements for :class:`Template`.
    """

    def __init__(
        self,
        bitdepth=8,
        wav_um=0.633,
        pitch_um=(8,8),
        **kwargs
    ):
        r"""
        Initialize SLM and attributes.

        Parameters
        ----------
        bitdepth : int
            Depth of SLM pixel well in bits. Defaults to 10.
        wav_um : float
            Wavelength of operation in microns. Defaults to 1 um.
        pitch_um : (float, float)
            Pixel pitch in microns. Defaults to 8 micron square pixels.
        **kwargs
            See :meth:`.SLM.__init__` for permissible options.

        Note
        ~~~~
        These arguments, which ultimately are used to instantiate the :class:`.SLM` superclass,
        may be more accurately filled by calling the SLM's SDK functions.
        See the other implemented SLM subclasses for examples.
        """

        width = 1920
        height = 1200

        # Mandatory functions:
        # - Opening a connection to the device.

        devs = sdk.EXULUSListDevices()
        print(devs)
        if (len(devs) <= 0):
            raise('There is no devices connected')
        else:
            EXULUS = devs[0]
            serialNumber = EXULUS[0]

            hdl = sdk.EXULUSOpen(serialNumber, 38400, 3)

            if (hdl < 0):
                print("Connect ", serialNumber, "fail")
                return -1
            else:
                print("Connect ", serialNumber, "successfully")


        # Other possibilities to consider:
        # - Setting the SLM's operating wavelength (wav_um).
        # - Updating the SLM's phase table if necessary, and/or setting the design
        #   wavelength (wav_design_um).
        # - Setting the SLM's default settle time (abstract class SLM uses
        #   settle_time_s=0.3 seconds). This is important for experimental feedback to
        #   allow the SLM to settle before viewing the result on a camera.
        # - Checking for and saving the SLM parameters (height, width, etc).

        # Instantiate the superclass
        super().__init__(
            (width, height),
            bitdepth=bitdepth,
            wav_um=wav_um,
            pitch_um=pitch_um,
            **kwargs
        )

        # Zero the display using the superclass `write()` function.
        self.write(None)

    @staticmethod
    def info(verbose=True):
        """
        Discovers all SLMs detected by an SDK.
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
        raise NotImplementedError()
        serial_list = get_serial_list()     # TODO: Fill in proper function.
        return serial_list

    def _write_hw(self, phase):
        """
        Low-level hardware interface to write ``phase`` data onto the SLM.
        When the user calls the :meth:`.SLM.write` method of
        :class:`.SLM`, ``phase`` is error checked before calling
        :meth:`_write_hw()`. See :meth:`.SLM._write_hw` for further detail.
        """
        send_to_slm(phase)
        # TODO: Insert code here to write raw phase data to the SLM.