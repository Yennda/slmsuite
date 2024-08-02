import cv2
import screeninfo
import numpy as np
import threading
# adapted from https://pypi.org/project/screeninfo/

class SlmScreen(object):
    def __init__(self, screen_id=2):
        self.screen_id = screen_id
        print(len(screeninfo.get_monitors()))
        self.screen = screeninfo.get_monitors()[screen_id]
        width, height = self.screen.width, self.screen.height


        self.window_name = 'Projector'
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        # cv2.moveWindow(window_name, self.screen.x - 1, self.screen.y - 1)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)

        image = np.zeros([self.screen.width, self.screen.height])
        image[500:700, 200:400] = 1
        cv2.imshow(self.window_name, image)
        cv2.waitKey()

    def send(self, image):
        cv2.imshow(self.window_name, image)

    def close(self):
        cv2.destroyAllWindows()

    def foo(self):
        return np.average([i**2 for i in range(10)])

class SlmScreen:
    def __init__(self, screen_id):
        self.screen_id = screen_id

        self.screen = screeninfo.get_monitors()[self.screen_id]
        width, height = self.screen.width, self.screen.height
        self.img = np.zeros([width, height])

        self.window_name = 'Projector'
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.show_image, daemon=True)
        self.thread.start()

    def show_image(self):
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
        with self.lock:
            self.img = img

    def close(self):
        if self.lock.locked():
            self.lock.release()
        else:
            self.join()