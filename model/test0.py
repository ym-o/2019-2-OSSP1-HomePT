from stacked_hourglass import HumanPosePredictor, hg2, hg8, hg1
from stacked_hourglass.utils.transforms import shufflelr, crop, color_normalize, fliplr, transform
from PIL import Image
import torch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import collections  as mc
import time, math,os
import PIL.ExifTags as ExifTags
from tqdm import tqdm
import seaborn as sns

# ...load image of a person into a PyTorch tensor...

model = hg8(pretrained=True)
predictor = HumanPosePredictor(model, device='cpu')
root = "/Users/seungyoun/Desktop/DGU/2/공개SW/pytorch-stacked-hourglass-master/dataset"

print("==model loaded==")

RGB_MEAN = torch.as_tensor([0.4404, 0.4440, 0.4327])
RGB_STDDEV = torch.as_tensor([0.2458, 0.2410, 0.2468])
#im = np.asarray(Image.open("./images/test14.jpeg"))
up = os.listdir(root + "/up")
down = os.listdir(root + "/down")
print("up   samples : ",len(up),"\ndown samples : ",len(down))

def predict(path):
    orgImg = Image.open(path)

    try:
        for orientation in ExifTags.TAGS.keys() :
            if ExifTags.TAGS[orientation]=='Orientation' : break
        exif=dict(orgImg._getexif().items())
        if exif[orientation] == 3:
            orgImg=orgImg.rotate(180, expand=True)
        elif exif[orientation] == 6 :
            orgImg=orgImg.rotate(270, expand=True)
        elif exif[orientation] == 8 :
            orgImg=orgImg.rotate(90, expand=True)

    except:
        pass
    im = np.asarray(orgImg)
    img = torch.tensor(im).transpose(0,2)
    img = color_normalize(img, RGB_MEAN, RGB_STDDEV)
    if(img.size(0)==4):
        img = img[:3]

    c,h,w = img.size()
    start = time.time()
    joints = predictor.estimate_joints(img, flip=True)
    end = time.time()
    xs,ys = list(joints[:,0].numpy()), list(joints[:,1].numpy())
    #print("infer time : ",end-start)


    c = np.array([(0, 1, 1, 0.5),
              (0, 1, 1, 0.5),
              (0, 0, 1, 0.5),
              (0, 0, 1, 0.5),
              (0, 0.3, 0.7, 0.5),
              (0, 0.3, 0.7, 0.5),
              (0.1, 0.6, 0.7, 0.5),
              (0.1, 0, 0.2, 0.5),
              (0, 0.5, 0.5, 0.5),
              (0.1, 0.6, 0.2, 0.5),
              (0, 1, 0.15, 0.5),
              (0, 1, 0.15, 0.5),
              (0, 0, 1, 0.5),
              (0, 0, 1, 0.5),
              (0, 0.3, 0.5, 0.5)])
    lines = [[(ys[0], xs[0]), (ys[1], xs[1])],
         [(ys[1], xs[1]), (ys[2], xs[2])],
         [(ys[5], xs[5]), (ys[4], xs[4])],
         [(ys[4], xs[4]), (ys[3], xs[3])],
         [(ys[3], xs[3]), (ys[6], xs[6])],
         [(ys[6], xs[6]), (ys[2], xs[2])],
         [(ys[6], xs[6]), (ys[7], xs[7])],
         [(ys[7], xs[7]), (ys[8], xs[8])],
         [(ys[8], xs[8]), (ys[9], xs[9])],
         [(ys[10], xs[10]), (ys[11], xs[11])],
         [(ys[11], xs[11]), (ys[12], xs[12])],
         [(ys[12], xs[12]), (ys[ 7], xs[ 7])],
         [(ys[ 7], xs[ 7]), (ys[13], xs[13])],
         [(ys[14], xs[14]), (ys[13], xs[13])],
         [(ys[14], xs[14]), (ys[15], xs[15])]]


    left_antebrachial   = np.array([ys[15]-ys[14],xs[15]-xs[14]])
    left_forearm        = np.array([ys[13]-ys[14],xs[13]-xs[14]])
    left_back           = np.array([ys[7]-ys[13], xs[7]-xs[13]])
    left_arm_angle      = np.inner(left_antebrachial, left_forearm)/(np.linalg.norm(left_antebrachial)*np.linalg.norm(left_forearm))
    left_back_angle     = np.inner(left_forearm, left_back)/(np.linalg.norm(left_forearm)*np.linalg.norm(left_back))

    right_antebrachial  = np.array([ys[10]-ys[11],xs[10]-xs[11]])
    right_forearm       = np.array([ys[12]-ys[10],xs[12]-xs[10]])
    right_back          = np.array([ys[7]-ys[12], xs[7]-xs[12]])
    right_arm_angle     = np.inner(right_antebrachial, right_forearm)/(np.linalg.norm(right_antebrachial)*np.linalg.norm(right_forearm))
    right_back_angle    = np.inner(right_back, right_forearm)/(np.linalg.norm(right_back)*np.linalg.norm(right_forearm))

    left_arm_angle   = np.arccos(left_arm_angle)*360/(np.pi*2)
    left_back_angle  = 180-np.arccos(left_back_angle)*360/(np.pi*2)
    right_arm_angle  = np.arccos(right_arm_angle)*360/(np.pi*2)
    right_back_angle = 180-np.arccos(right_back_angle)*360/(np.pi*2)

    return left_arm_angle,left_back_angle,right_arm_angle,right_back_angle

upDist   = list()
downDist = list()

for i in tqdm(up):
    left_arm_angle,left_back_angle,right_arm_angle,right_back_angle = predict(root+"/up/"+i)
    upDist.append([left_arm_angle, left_back_angle, right_arm_angle, right_back_angle])

for i in tqdm(down):
    left_arm_angle,left_back_angle,right_arm_angle,right_back_angle = predict(root+"/down/"+i)
    upDist.append([left_arm_angle, left_back_angle, right_arm_angle, right_back_angle])
