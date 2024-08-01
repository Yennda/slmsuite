import cv2
import screeninfo

# adapted from https://pypi.org/project/screeninfo/

def send_to_slm(image, screen_id = 1):
    # get the size of the screen
    screen = screeninfo.get_monitors()[screen_id]
    width, height = screen.width, screen.height

    image = cv2.resize(image, (height, width))

    window_name = 'Projector'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                          cv2.WINDOW_FULLSCREEN)
    cv2.imshow(window_name, image)
    cv2.waitKey()
    cv2.destroyAllWindows()