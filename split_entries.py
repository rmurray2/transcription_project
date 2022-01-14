#TODO
''' add over dict to keep track of where entry images start from government site'''
import os
import pandas as pd
import cv2 as cv
import joblib

def vconcat_resize_min(im_list, interpolation=cv.INTER_CUBIC):
    w_min = min(im.shape[1] for im in im_list)
    im_list_resize = [cv.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation) for im in im_list]
    return cv.vconcat(im_list_resize)
            

def split_entries(root):
	#root = '/run/media/rm/Samsung_T5/transcription_project/Flores/Lajes das Flores/Lajes/1911/'
	hdf = pd.read_csv(root + 'heights.csv')

	hdf.sort_values(['img', 'y_height'], inplace=True)

	img_list, y_height_list = hdf.img.tolist(), hdf.y_height.tolist()

	if not os.path.exists(root + 'entries'):
		os.mkdir(root + 'entries')

	od = {} #keep track of entry images and what the starting images 
	entry_count = 0
	for i, (current_image_name, current_height) in enumerate(zip(img_list, y_height_list)): 
		if i == len(img_list)-1: break
		entry_count += 1
		print ("*******")
		current_height = int(current_height)
		current_image_number = int(current_image_name.split('.')[0])
		end_image_name = img_list[i+1]
		end_image_number = int(end_image_name.split('.')[0])
		end_image_y_height = int(y_height_list[i+1]) 
		if current_image_number == end_image_number:
			print ('equal', current_image_name)
			image = cv.imread(root + 'split_center/' + current_image_name)
			current_image_x_max = image.shape[1]
			crop_img = image[current_height:end_image_y_height, 0:current_image_x_max]
			cv.imwrite(root + 'entries' + '/' + str(entry_count) + '.jpg', crop_img)
			od[str(entry_count) + '.jpg'] = current_image_number
			continue

		elif end_image_number == (current_image_number + 1):# next sequential image IS the end
			print ('next', current_image_name)
			image = cv.imread(root + 'split_center/' + current_image_name)
			current_image_x_max = image.shape[1]
			crop_img = image[current_height:, 0:current_image_x_max]
	#        cv.imwrite('1.jpg', crop_img)

			image2 = cv.imread(root + 'split_center/' + end_image_name)
			end_image_x_max = image2.shape[1]
			crop_img2 = image2[0:end_image_y_height, 0:end_image_x_max]
	#        cv.imwrite('2.jpg', crop_img2)

			im_v = vconcat_resize_min([crop_img, crop_img2])
			cv.imwrite(root + 'entries' + '/' + str(entry_count) + '.jpg', im_v)
			od[str(entry_count) + '.jpg'] = current_image_number
			continue

		else: #next sequential image is NOT the end
			print ('gap', current_image_number)

			temp = []
			image = cv.imread(root + 'split_center/' + current_image_name)
			current_image_x_max = image.shape[1]
			crop_img = image[current_height:, 0:current_image_x_max]
			temp.append(crop_img)

			for k in range(current_image_number+1, end_image_number+1):
				print (k, end_image_number)
				if k != end_image_number:
					fn = f"{k:04d}" + ".jpg"
					print (fn, 'not')
					im = cv.imread(root + 'split_center/' + fn)
					temp.append(im)
				else:
					fn = f"{k:04d}" + ".jpg"
					print (fn, 'is equal')
					print (entry_count)
					image2 = cv.imread(root + 'split_center/' + fn)
					end_image_x_max = image2.shape[1]
					crop_img2 = image2[0:end_image_y_height, 0:end_image_x_max]
					temp.append(crop_img2)

					im_v = vconcat_resize_min(temp)
					od[str(entry_count) + '.jpg'] = current_image_number
					cv.imwrite(root + 'entries' + '/' + str(entry_count) + '.jpg', im_v)
	
	joblib.dump(od, root + 'entry_dict')


#split_entries('/run/media/rm/Samsung_T5/transcription_project/Flores/Lajes das Flores/Lajes/1911/')
#            readimage
#            img_list.append(k)
#        v_concat_resize_min(img_list)





#with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#    print(hdf)

#
#for i, row in hdf.iterrows():
#    print (i, row)
#
#
#files = os.listdir(root)
#im_v = vconcat_resize_min([left_side, right_side])

