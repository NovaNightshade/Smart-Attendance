from flask import Flask,render_template,Response,url_for,request
from camera import VideoCamera
import urllib.request
from pyzbar import pyzbar
import argparse
import datetime
import time
import cv2
import tablib
import os
import pandas as pd
from datetime import date
found=[]
ap = argparse.ArgumentParser()
ap.add_argument("-o","--output",type=str,default="Attendance.csv",help="path")
args = vars(ap.parse_args())
csv = open(args["output"],"w")
app=Flask(__name__)
dataset1 = tablib.Dataset()
dataset2 = tablib.Dataset()
dataset3 = tablib.Dataset()

@app.route('/')
def index():
	with open(os.path.join(os.path.dirname(__file__), 'Details.csv')) as f:
		dataset1.csv = f.read()

	with open(os.path.join(os.path.dirname(__file__), 'Student.csv')) as g:
		dataset2.csv = g.read()

	with open(os.path.join(os.path.dirname(__file__), 'Attendance.csv')) as h:
		dataset3.csv = h.read()
	d1 = dataset1.html
	d2 = dataset2.html
	d3 = dataset3.html
	fn=''
	ln=''
	em=''
	mo=''
	if len(found)!=0:
		id = found[-1]
	else:
		id =None
	if id!=None:
		df1=pd.read_csv('Details.csv')
		for index,row in df1.iterrows():
			if row['Id']==id:
				fn=row['First Name']
				ln=row['Last Name']
				em=row['Email Id']
				mo=row['Mobile No']

	print(found)
	return render_template('index.html', data1=d1, data2=d2, data3=d3,id=id,FName=fn,LName=ln,email=em,mobile=mo)


def gen(camera):
	while True:
		frame=camera.get_frame()
		barcodes = pyzbar.decode(frame)
		for barcode in barcodes:
			(x, y, w, h) = barcode.rect
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
			barcodeData = barcode.data.decode("utf-8")
			barcodeType = barcode.type
			text = "{} ({})".format(barcodeData, barcodeType)
			cv2.putText(frame, text, (x, y - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
			with app.app_context():
				FirstName=''
				LastName=''
				FullName=''
				if barcodeData not in found:
					openFile=pd.read_csv('Details.csv')
					for index,row in openFile.iterrows():
						if row['Id']==barcodeData:
							FirstName = row['First Name']
							LastName = row['Last Name']
							FullName = FirstName +" " + LastName
					csv.write("{},{},{}\n".format(datetime.datetime.now(),barcodeData, FullName))
					csv.flush()
					found.append(barcodeData)
					openAtt = pd.read_csv('Attendees.csv')
					today = date.today()
					today = today.strftime("%d-%m-%Y")
					for index,row in openAtt.iterrows():
						if row['Id']==barcodeData:
							row[today]='P'
		ret,jpeg=cv2.imencode('.jpg',frame)
		jpeg=jpeg.tobytes()
		yield (b'--frame\r\n'b'Content-Type:image/jpeg\r\n\r\n'+jpeg+b'\r\n\r\n')
	csv.close()


@app.route('/response',methods=['POST'])
def response():
	idNo = request.form['ID']
	FName = request.form['First_Name']
	LName = request.form['Last_Name']
	Email = request.form['Email_Id']
	Mobile = request.form['Mobile_Number']
	isThere = False
	df1=pd.read_csv('Details.csv')
	for index,row in df1.iterrows():
		if row['Id']==idNo:

			isThere=True
			return render_template('response.html',msg="Already Exists")
	if isThere!=True:
		df2=pd.DataFrame({'Id':[idNo],'First Name':[FName],'Last Name':[LName],'Email Id':[Email],'Mobile No':[Mobile]})
		dff=df1.append(df2,ignore_index=True,sort=False)
		dff.to_csv(r'./Details.csv',index=False)

		return render_template('response.html',msg="Success")


@app.route('/video_feed')
def video_feed():

	return Response(gen(VideoCamera()),mimetype='multipart/x-mixed-replace;boundary=frame')

if __name__=='__main__':
	app.run(host='0.0.0.0',debug=True)
