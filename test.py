import cv2

cap=cv2.VideoCapture(0)
while True:
    ret,frame=cap.read()
    cv2.rectangle(frame,(100,50),(375,100),(0,255,0),5)
    cv2.imshow('frames',frame)
    if cv2.waitKey(1) & 0xFF == ord('r'):
        image = frame.copy()
        crop_img = image[50:100, 100:375]
        cv2.imshow("crop_img", crop_img)
    if cv2.waitKey(2) & 0xFF==ord('q'):
        break

cv2.waitKey(0)
cap.release()
cv2.destroyAllWindows()
