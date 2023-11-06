import js
import io
import cv2
import base64
import numpy as np
from PIL import Image


class cam():
    def __init__(self, canvas):
        self.start = [0, 0]
        self.end = [0, 0]
        self.draw = False
        self.ctx = canvas.getContext("2d")
        self.ctx.font = "12px Arial"
        self.canvas = canvas
        self.raw_image = None
        self.image_data_url = None

    # Take in base64 string and return PIL image
    def stringToImage(self, base64_string):
        imgdata = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(imgdata))

    # convert PIL Image to an RGB image( technically a numpy array ) that's compatible with opencv
    def toRGB_cv2(self, image):
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGRA)

    def toPil(self, cv2image):
        return Image.fromarray(cv2.cvtColor(cv2image, cv2.COLOR_BGRA2RGBA))

    def snap(self, e=None):
        self.ctx.drawImage(video, 0, 20, video.width, video.height)
        self.image_data_url = self.canvas.toDataURL('image/jpeg')
        self.raw_image = self.stringToImage(self.image_data_url.split('base64,')[
                                            1]).crop((0, 20, 320, 260))
        self.showPIL(self.raw_image, img)
        return self.findBlob(self.raw_image)

    def show(self, cv2image, loc=img2):
        self.showPIL(self.toPil(cv2image), loc)

    def showPIL(self, PILimage, field):
        imgByteArr = io.BytesIO()
        PILimage.save(imgByteArr, format='png')
        imgByteArr = imgByteArr.getvalue()
        data = base64.b64encode(imgByteArr).decode('utf-8')
        src = f"data:image/png;base64,{data}"
        field.setAttribute('src', src)

    def startBox(self, info):
        # startImg = canvas.toDataURL('image/jpeg')
        self.start = [info.offsetX, info.offsetY]
        self.draw = True

    def endBox(self, info):
        self.end = [info.offsetX, info.offsetY]
        self.draw = False

    def readPixel(self, info):
        self.ctx.clearRect(0, 0, 320, 20)
        pixelValue = self.ctx.getImageData(info.offsetX, info.offsetY, 1, 1)
        self.ctx.fillText('x: %d y: %d  (%d, %d, %d)' % (
            info.offsetX, info.offsetY-20, pixelValue.data[0], pixelValue.data[1], pixelValue.data[2]), 1, 15)
        if self.draw:

            self.ctx.drawImage(img, 0, 20, 320, 240)
            # self.showPIL(self.raw_image,canvas)
            self.ctx.fillText('x: %d y: %d   x: %d y: %d' % (
                self.start[0], self.start[1]-20, info.offsetX, info.offsetY-20), 170, 15)
            self.ctx.beginPath()
            self.ctx.moveTo(self.start[0], self.start[1])
            self.ctx.lineTo(self.start[0], info.offsetY)
            self.ctx.lineTo(info.offsetX, info.offsetY)
            self.ctx.lineTo(info.offsetX, self.start[1])
            self.ctx.lineTo(self.start[0], self.start[1])
            self.ctx.stroke()
        elif self.start[0]:  # you have drawn in the past
            self.ctx.fillText('x: %d y: %d   x: %d y: %d' % (
                self.start[0], self.start[1]-20, self.end[0], self.end[1]-20), 170, 15)
        else:
            pass

    def findBlob(self, image):
        cv2_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        grey = cv2.cvtColor(cv2_image, cv2.COLOR_BGRA2GRAY)
        # shows any cv2 image in the same spot on the webpage (third image)
        self.show(grey)
        blurred = cv2.GaussianBlur(grey, (5, 5), 0)
        thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)[1]
        cnts = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.show(thresh)

        self.info = []
        for c in cnts[0]:  # if len(cnts)==2 else cnts[1]):
            # compute the center of the contour
            M = cv2.moments(c)
            area = cv2.contourArea(c)
            if area > 1000:
                if M["m00"] != 0:
                    cX = int(M['m10']/M['m00'])
                    cY = int(M['m01']/M['m00'])
                else:
                    cX, cY = 0, 0
                self.info.append([area, cX, cY])
                cv2.drawContours(
                    cv2_image, [c], -1, (0, 255, 0), thickness=cv2.FILLED)
                cv2.circle(cv2_image, (cX, cY), 7, (255, 0, 0), -1)
                cv2.putText(cv2_image, "center", (cX - 20, cY - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        self.show(cv2_image, blobs)

        # areas = np.array(self.info)[:,0]
        areas = [row[0] for row in self.info]
        self.order = np.flip(np.argsort(areas))  # sort by area
        if len(self.order > 0):
            [big, x, y] = self.info[self.order[0]]
            textBox.innerText = 'Found %d blobs. Biggest area (%d) at x = %d' % (
                len(self.order), int(big), int(x))
        return int(x)

    def live(self, e=None):
        for i in range(100):
            self.snap()
