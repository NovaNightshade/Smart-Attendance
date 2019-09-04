import cv2
class VideoCamera(object):
	def __init__(self):
		self.video=cv2.VideoCapture(0)
		self.video.set(3,240)
		self.video.set(4,300)
	def __del__(self):
		self.video.release()
	def get_frame(self):
		success,image=self.video.read()
		return image
