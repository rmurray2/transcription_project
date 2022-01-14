import streamlit as st
from PIL import Image, ImageDraw
import os
from streamlit_drawable_canvas import st_canvas
import joblib
import cv2 as cv
import pandas as pd
import glob

od = joblib.load("island_dump")


track_dict = {}
root = '/run/media/rm/Samsung_T5/transcription_project/'

scaling_factor = 1.5
def welcome():
    
	#dict of form
	# {island : {concelho : {Freguesia : [Periods...] }}}
	go_button = None
	island_choice = st.sidebar.radio("Island", tuple(od.keys()))
	if island_choice == 'Flores':
		concelho_choice = st.sidebar.radio("Concelho", tuple(od[island_choice].keys()))
		if concelho_choice != '':
			freg_choice = st.sidebar.radio("Freguesia", tuple(od[island_choice][concelho_choice].keys()))
			if freg_choice != '':
				period_choice = st.sidebar.radio("Period", tuple(od[island_choice][concelho_choice][freg_choice]), )

				if period_choice != '':
					period_path = root + island_choice + '/' + concelho_choice + '/' + freg_choice + '/' + period_choice +  '/'
					og_homepage = od[island_choice][concelho_choice][freg_choice][period_choice]
					st.sidebar.write("[Original Images](" + og_homepage + ')')
					if os.path.exists(period_path + 'done'):
						entry_dict = joblib.load(period_path + 'entry_dict')
#						st.write("--- BOOK ALREADY PROCESSED ---")
						images = os.listdir(period_path + 'entries/')
						sorted(images, key=lambda x: int(os.path.splitext(x)[0]))
						images.reverse()
						index = st.sidebar.number_input("Entry Number (" + str(len(images)) + ' Total)', value=1)
						index -=1
						st.write("Original Starting Page Number:")
						st.write(entry_dict[images[int(index)]])
#						if st.button("Next"):
#							index += 1
#						if st.button("Prev"):
#							index -= 1
						image = Image.open(period_path + 'entries/' + images[int(index)])
						st.image(image, use_column_width=True)
						

					else:
						path = root + island_choice + '/' + concelho_choice + '/' + freg_choice + '/' + period_choice + '/split_center/'
						files = os.listdir(path)
						index= st.sidebar.number_input('Image Number (' + str(len(files)) + ' Total)', value=1)
						index -=1
							
						if index+1 == len(files):
							if st.sidebar.button("Split Book"):
								with open(period_path + 'done', 'w') as outfile:
									outfile.write('.')
								import split_entries
								split_entries.split_entries(root + island_choice + '/' + concelho_choice + '/' + freg_choice + '/' + period_choice + '/')
								st.write("Entries split. Refresh page to view")

									
						
						image_num = index + 1
						fn = f"{image_num:04d}" + ".jpg"
						midsection = og_homepage.split('/')[4]
						link = og_homepage.replace('item1', 'master')	
						link = '/'.join(link.split('/')[:-1])
						src = link  + '/' + midsection + '_JPG/' + midsection + '_' + fn 

						st.write("[Original Image](" + src + ')')
							
						
						files.sort()

	#					values = []
						print ('file index', index, files[index])
						img = Image.open(path + files[index])
						if os.path.exists(period_path + 'heights.csv'):
							hdf = pd.read_csv(period_path + 'heights.csv')
							hdf = hdf.astype({'period':str})
							print (hdf)
							retset =  hdf[(hdf.island == island_choice) & (hdf.concelho == concelho_choice) & (hdf.freg == freg_choice) & (hdf.period == period_choice) & (hdf.img == files[index])]
							print (retset)
							if retset.empty != True:
								print ('went into rest empty')
								y_heights = retset.y_height.tolist()
								draw = ImageDraw.Draw(img)
								for height in y_heights:
									draw.line((0, height, img.size[0], height), fill=500, width=5)
								
								
						canvas_result = st_canvas(
							#construct image path
							background_image=img,
							update_streamlit=True,
							height=img.size[1]/scaling_factor,
							width=img.size[0]/scaling_factor,
							drawing_mode='line',
							key=files[index],
						)
						if canvas_result.json_data is not None:
							print (canvas_result.json_data, 'this')
							with open(period_path + 'temp.csv', 'w') as outfile:
								outfile.write('island,concelho,freg,period,img,y_height,img_src\n')
								for i in range(0, len(canvas_result.json_data["objects"])):
									cv.imwrite('testout.jpg', canvas_result.image_data)
									y_height = canvas_result.json_data["objects"][i]['top']
		#							values.append(y_height)
									print (y_height)
									#rewrite to a temp file all the values in the store 
									outfile.write(island_choice + ',' + concelho_choice + ',' + freg_choice + ',' + period_choice + ',' + files[index] + ',' + str(y_height*scaling_factor) + ',' + src + '\n')

	#						for height in values:
	#						print(values)
						else: #this means a new image was loaded
							if os.path.exists(period_path + 'heights.csv'):
								df = pd.read_csv(period_path + 'heights.csv')
							
								temp_df = pd.read_csv(period_path + 'temp.csv')
								temp_df.drop_duplicates(inplace=True)
								new_df = df.append(temp_df, ignore_index=True)
								new_df.to_csv(period_path + 'heights.csv', index=False)
								os.remove(period_path + 'temp.csv')
							else:
	#							df = pd.DataFrame({'island':[island_choice], 'freg':[freg_choice], 'period':[period_choice], 'file':[files[index]], 'y_height':[str(y_height*scaling_factor)]}
	#							temp_df = pd.read_csv(period_path + 'temp.csv')
								try:
									os.rename(period_path + 'temp.csv', period_path + 'heights.csv')
									os.remove(period_path + 'temp.csv')
								except:
									pass
							
						

	


welcome()
