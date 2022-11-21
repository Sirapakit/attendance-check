import cv2

name = input('name: ')
camera = cv2.VideoCapture(0)

while True:
	
    ret, frame = camera.read()
    frame = cv2.flip(frame,1)
    font = cv2.FONT_HERSHEY_TRIPLEX
    cv2.putText(frame, 'Front Face', (50, 50), font, 1, (255, 255, 255), 1, cv2.LINE_4)
    cv2.putText(frame, 'press c for capture', (50, 80), font, 0.5, (255, 255, 255), 1, cv2.LINE_4)
    cv2.imshow('camera', frame)

    key = cv2.waitKey(1)
    if key == ord('c'):
        cv2.imwrite(filename=name+'.jpg', img=frame)
        print('completely captured image..')
        break
    elif key == ord('q'):
        print('non captured image')
        break
    
camera.release()
cv2.destroyAllWindows()
