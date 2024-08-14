import cv2
import screeninfo
import numpy as np
import threading

class SlmScreen(object):
    """
    Class for handling the full screen projection of an image. It controls the window in a separate thread.
    """
    def __init__(self, screen_id):
        """
        Initialization of the class. It creates the thread and sends it the method show_image.

        Parameters
        ----------
        screen_id : int
            id of the screen
        """
        self.screen_id = screen_id

        self.screen = screeninfo.get_monitors()[self.screen_id]
        width, height = self.screen.width, self.screen.height
        self.img = np.zeros([width, height])

        self.window_name = 'Projector'
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.show_image, daemon=True)
        self.thread.start()

    def show_image(self):
        """
        Method creating the sindow and showing an image.

        """
        while True:
            if self.img is not None:
                with self.lock:
                    cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
                    cv2.moveWindow(self.window_name, self.screen.x - 1, self.screen.y - 1)
                    cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN,
                                          cv2.WINDOW_FULLSCREEN)
                    cv2.imshow(self.window_name, self.img)
                    cv2.waitKey(1)

    def send(self, img):
        """
        Sets the new image and displays it.

        Parameters
        ----------
        img : np.array

        """
        with self.lock:
            self.img = img

    def close(self):
        """
        Stops the thread thus closing the window displaying the image.
        Returns
        -------

        """
        if self.lock.locked():
            self.lock.release()
        else:
            self.join()