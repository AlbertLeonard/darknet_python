#!coding=utf-8
#modified by lyk at 2018.04.26
#function: 1,detect the video captured by webcam 
#          2,you can pass some frames

from ctypes import *
import math
import random
#import module named cv2 to draw
import cv2
import random
import Image

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1

def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]

class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]

class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

    

#lib = CDLL("/home/pjreddie/documents/darknet/libdarknet.so", RTLD_GLOBAL)
lib = CDLL("/home/lyk/darknet/libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

set_gpu = lib.cuda_set_device
set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        res.append((meta.names[i], out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res

def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
    im = load_image(image, 0, 0) 
    num = c_int(0)
    pnum = pointer(num)
    predict_image(net, im)
    dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
    num = pnum[0]
    if (nms): do_nms_obj(dets, num, meta.classes, nms);

    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    free_image(im)
    free_detections(dets, num)
    return res

# 2018.04.25
def showPicResult(image):
    img = cv2.imread(image)
    cv2.imwrite(out_img, img)
    for i in range(len(r)):
        x1=r[i][2][0]-r[i][2][2]/2
        y1=r[i][2][1]-r[i][2][3]/2
	x2=r[i][2][0]+r[i][2][2]/2
	y2=r[i][2][1]+r[i][2][3]/2
	im = cv2.imread(out_img)
	#draw different color rectangle
	'''
	r_color = random.randint(0,255)
	g = random.randint(0,255)
	b = random.randint(0,255)
	cv2.rectangle(im,(int(x1),int(y1)),(int(x2),int(y2)),(r_color,g,b),3)
	'''
	cv2.rectangle(im,(int(x1),int(y1)),(int(x2),int(y2)),(0,255,0),3)
	#putText
	x3 = int(x1+5)
	y3 = int(y1-10)
	font = cv2.FONT_HERSHEY_SIMPLEX
	if ((x3<=im.shape[0]) and (y3>=0)):
	    im2 = cv2.putText(im, str(r[i][0]), (x3,y3), font, 1, (0,255,0) , 2)
	else:
	    im2 = cv2.putText(im, str(r[i][0]), (int(x1),int(y1+6)), font, 1, (0,255,0) , 2)
	#***********

	#if don't want to save out_img /just want to dispaly the final_pic, 
	#then just don't use this loop, list all the object_'num'; but you don't know how many is the 'num'.
	#This is a method that works well. 
	cv2.imwrite(out_img, im)
    cv2.imshow('yolo_image_detector', cv2.imread(out_img))
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    
if __name__ == "__main__":
    #net = load_net("cfg/densenet201.cfg", "/home/pjreddie/trained/densenet201.weights", 0)
    #im = load_image("data/wolf.jpg", 0, 0)
    #meta = load_meta("cfg/imagenet1k.data")
    #r = classify(net, meta, im)
    #print r[:10]
    net = load_net("/home/lyk/darknet/cfg/yolov2-tiny.cfg", "/home/lyk/darknet/weights/yolov2-tiny.weights", 0)
    meta = load_meta("/home/lyk/darknet/cfg/coco.data")
    #origin_img = "/home/lyk/darknet/data/copy_dog.jpg"
    out_img = "/home/lyk/darknet/data/test_result.jpg"
    video_tmp = "/home/lyk/darknet/data/video_tmp.jpg"

    # make a video_object and init the video object
    cap = cv2.VideoCapture(0)
    # define picture to_down' coefficient of ratio
    scaling_factor = 0.5
    count = 0
    # loop until press 'esc' or 'q'
    while True:
        # collect current frame
        ret, frame = cap.read()
	#print ret; if get frame the return ret=True
        # resize the frame
        frame = cv2.resize(frame,None,fx=scaling_factor,fy=scaling_factor,interpolation=cv2.INTER_AREA)
	if ret:
	    count = count + 1
	    #print count
	#detect and show per 50 frames
	if count == 5:
	    count = 0
	    img_arr = Image.fromarray(frame)
            #r = Image.fromarray(image[0]).convert('L') 
            #g = Image.fromarray(image[1]).convert('L') 
            #b = Image.fromarray(image[2]).convert('L') 
            #im = Image.merge("RGB", (r, g, b))
            img_goal = img_arr.save(video_tmp)
            r = detect(net, meta, video_tmp)
            #print r
            for j in range(len(r)):
	        print r[j][0], ' : ', int(100*r[j][1]),"%"
	        print r[j][2]
	    print ''
	    print '#-----------------------------------#'
            #display the rectangle of the objects in window
            showPicResult(video_tmp)
	else:
	    continue
        # wait 1ms per iteration; press Esc to jump out the loop 
        c = cv2.waitKey(1)
        if (c==27) or (0xFF == ord('q')):
            break
    # release and close the display_window
    cap.release()
    #just don't need, or will print error.//Maybe selecting one is OK. 
    #cv2.destoryAllWindows()   


    

