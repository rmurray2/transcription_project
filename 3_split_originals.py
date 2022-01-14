from PIL import Image
import numpy as np
import cv2 as cv
import joblib
import os
import itertools

od = joblib.load("island_dump")
root = '/run/media/rm/Samsung_T5/transcription_project/'

def find_points(img):
    combos = []
    for i in itertools.product(range(0, 70, 5), range(0, 70, 5)):
        combos.append(i)

    src = cv.GaussianBlur(img,(5,5),0)
    for thresh1, thresh2 in combos:
        edges = cv.Canny(src, thresh1, thresh2)

        #cv.imwrite('eroded2.jpg',edges)
        linesP = cv.HoughLinesP(edges, 1, np.pi / 180, 100, None, 225, 250)
    #                    print (len(linesP))
    #                    print (linesP)
        lines_cleaned = []

        print (src.shape, "find points")
        y_size, x_size, chan = src.shape
        target_min = x_size/2 - 75
        target_max = x_size/2 + 75
    #                    print (target_min, target_max)
        mins = []
        maxes = []
        lines_cleaned = []
        for i in linesP:
            line = i[0]
            if line[0] > target_min and (line[0] < target_max) and (line[2] > target_min) and (line[2] < target_max):
    #                            print (i, '****')
                the_min = min(line[0], line[2])
                the_max = max(line[0], line[2])
                mins.append(the_min)
                maxes.append(the_max)

            
        try:
            x_min_image = min(mins)
            x_max_image = max(maxes)
            return x_min_image, x_max_image
        except:
            continue

def find_crop_area(original, path, dilate=True):

    orig_fn = path + original

    src = cv.imread(orig_fn)
#    src = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

    lab= cv.cvtColor(src, cv.COLOR_BGR2LAB)
    l, a, b = cv.split(lab)
    clahe = cv.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv.merge((cl,a,b))
    contrasted = cv.cvtColor(limg, cv.COLOR_LAB2BGR)

    #src = cv.resize(src, (1000, 500))

    if dilate == True:
        kernel = np.ones((4, 4),np.uint8)
        contrasted = cv.dilate(contrasted,kernel,iterations = 4)
    #cv.imwrite('dilated2.jpg',dilation)
    #exit()
    blurred = cv.GaussianBlur(contrasted,(5,5),0)
    edges = cv.Canny(blurred, 61, 28)

    #cv.imwrite('eroded2.jpg',edges)
    linesP = cv.HoughLinesP(edges, 1, np.pi / 180, 100, None, 225, 250)
#                    print (len(linesP))
#                    print (linesP)
    lines_cleaned = []

#                    print (src.shape)
    print (src.shape, 'find crop area')
    y_size, x_size, chan = src.shape

    target_min = x_size/2 - 75
    target_max = x_size/2 + 75
#                    print (target_min, target_max)
    mins = []
    maxes = []
    lines_cleaned = []
    for i in linesP:
        line = i[0]
        if line[0] > target_min and (line[0] < target_max) and (line[2] > target_min) and (line[2] < target_max):
#                            print (i, '****')
            the_min = min(line[0], line[2])
            the_max = max(line[0], line[2])
            mins.append(the_min)
            maxes.append(the_max)

#                            print ("")
        
    try:
        x_min_image = min(mins)
        x_max_image = max(maxes)
    except:
        x_min_image, x_max_image = find_points(blurred)

    return x_min_image, x_max_image, y_size, x_size


for island,i in od.items():
    if island != 'Flores': continue

    for concelho,j in od[island].items():
        print (concelho)

        for f, k in od[island][concelho].items():
            print ('\t', f)

            for period, z in od[island][concelho][f].items():
                print ('\t\t', period)

                path = root + island + '/' + concelho + '/' + f + '/' + period + '/original/'


                if not os.path.exists(root + island + '/' + concelho + '/' + f + '/' + period + '/split_center'):
                    os.mkdir(root + island + '/' + concelho + '/' + f + '/' + period + '/split_center')

                new_path = root + island + '/' + concelho + '/' + f + '/' + period + '/split_center/'

                originals = os.listdir(path)
                originals.sort()

                for index, original in enumerate(originals):
                    print (index)
                    orig_fn = path + original
                    
                    try:
                        x_min_image, x_max_image, y_size, x_size = find_crop_area(original, path)
                    except:
                        print ("FAILED with dilation, trying without")
                        try:
                            x_min_image, x_max_image, y_size, x_size = find_crop_area(original, path, dilate=False)
                        except:
                            with open("img_fail_list", 'a') as outfile:
                                outfile.write(path + ',' + original + '\n')
                            print ("SECOND FAIL ********")
                            continue

#                    print (x_min_image, x_max_image)

                    original_img = Image.open(orig_fn)
                    left_side_cropped = original_img.crop((0, 0, x_max_image, y_size))
                    #left_side_cropped.show()
                    left_side_cropped.save('left_side.jpg')

                    right_side_cropped = original_img.crop((x_min_image, 1, x_size, y_size))
                    right_side_cropped.save('right_side.jpg')
                    #right_side_cropped.show()

                    right_side = cv.imread('right_side.jpg')
                    left_side = cv.imread('left_side.jpg')

                    
                    def vconcat_resize_min(im_list, interpolation=cv.INTER_CUBIC):
                        w_min = min(im.shape[1] for im in im_list)
                        im_list_resize = [cv.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation) for im in im_list]
                        return cv.vconcat(im_list_resize)
                    im_v = vconcat_resize_min([left_side, right_side])


                    cv.imwrite(new_path + original, im_v)
                    os.remove('left_side.jpg')
                    os.remove('right_side.jpg')

#if linesP is not None:
#    for i in range(0, len(linesP)):
#        l = linesP[i][0]
#        cv.line(dilation, (l[0], l[1]), (l[2], l[3]), (0,0,255), 1, cv.LINE_AA)
#cv.imwrite('lines.jpg',dilation)
#cv.imshow('canny', dilation)
#cv.waitKey(0)
