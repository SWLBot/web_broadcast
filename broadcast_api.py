from mysql_class import mysqll
from random import sample
from datetime import date
from datetime import datetime
from datetime import timedelta
import os.path

#The API connect mysql and arrange the schedule and write it to the schedule.txt
def img_schedule(schedule_dir, modee):
	
	update_fall = False
	find_fall = False
	ans = []
	
	file_name = "sql_token"
	
	#connect to mysql
	db = mysqll()
	if db.connectt(file_name) == -1:
		return -1
	
	#update expire data berfore query
	sql = ("UPDATE image_data " \
			+"SET img_is_expire=1 " \
			+"WHERE TO_DAYS(NOW())-TO_DAYS(img_end_date)>0 " \
			+"or (TO_DAYS(NOW())-TO_DAYS(img_end_date)=0 and TIME_TO_SEC(DATE_FORMAT(NOW(), '%H:%i:%s'))-TIME_TO_SEC(img_end_time)>0)")
	
	if db.cmdd(sql) == -1:
		update_fall = True
	
	#find images that may be schedule
	sql = "SELECT a0.img_id, a0.img_system_name, a0.img_display_time, a1.type_dir, a0.img_end_time FROM " \
			+" (SELECT img_id, type_id, img_system_name, img_display_time, img_end_time " \
			+" FROM image_data " \
			+" WHERE img_is_expire=0 and TO_DAYS(NOW())-TO_DAYS(img_start_date)>=0 " \
			+" and TIME_TO_SEC(DATE_FORMAT(NOW(), '%H:%i:%s')) between TIME_TO_SEC(img_start_time) and TIME_TO_SEC(img_end_time)) a0 " \
			+" LEFT JOIN (SELECT type_id, type_dir FROM image_type) a1 on a0.type_id=a1.type_id "
	#print(sql)
	
	resultt = db.queryy(sql)
	if resultt==-1:
		find_fall = True
	else:
		#restruct results of query
		for roww in resultt:
			ans.append([roww[0], (roww[3] + roww[1]), roww[2], roww[4]])
			#           img_id,  dir and file name, display time, end time
     
	#display in loop or random display
	if modee == 1:
		"DO NOTHING"
	elif modee == 2:
		if len(ans)>20:
			ans = sample(ans, 20)
	
	#update img display count and write to schedule
	date_now = date.today()
	schedule_file = ("broad_" + str(date_now.year) + "_" + str(date_now.month) + "_" + str(date_now.day) + ".txt")
	schedule_file = os.path.join(schedule_dir,("static/log/"+schedule_file))
	if not os.path.isfile(schedule_file) :
		filee = open(schedule_file, "w")
	else :
		filee = open(schedule_file, "a")
	add_num = 0
	if len(ans)>0:
		for tt in range(len(ans)):
			sql = "UPDATE image_data SET img_display_count=img_display_count+1 WHERE img_id='"+ans[tt][0]+"'"
			if db.cmdd(sql) == -1:
				update_fall = True
			else :
				int_str1 = str(ans[tt][2])
				int_str2 = str(ans[tt][3])
				write_str = ("0 " + ans[tt][0] + " " + ans[tt][1] + " " + int_str1 + " " + int_str2 + " \n")
				#                   image_id,           img_dir,        display time,     expire_time
				filee.write(write_str)
				add_num+=1
	filee.close()
	
	return add_num


#The API load schedule.txt and find out the first image which has not print and the time limit still allow
def load_schedule(schedule_dir):

	date_now = date.today()
	schedule_file = ("broad_" + str(date_now.year) + "_" + str(date_now.month) + "_" + str(date_now.day) + ".txt")
	new_file = ("new_" + schedule_file)
	old_file = ("old_" + schedule_file)
	schedule_file = os.path.join(schedule_dir,("static/log/"+schedule_file))
	new_file = os.path.join(schedule_dir,("static/log/"+new_file))
	old_file = os.path.join(schedule_dir,("static/log/"+old_file))

	if os.path.isfile(new_file) :
		try:
			if os.path.isfile(old_file) :
				os.remove(old_file)
			os.rename(schedule_file, old_file)
			os.rename(new_file,schedule_file)
		except:
			"Do noting"
	

	try:
		filee = open(schedule_file, "r+")
	except:
		return ["img/0.jpg", 5, 0]
	

	pure_data = ""
	deal_data = ""
	countt = 0
	lock_countt = []
	pass_count = 0
	already_get_target = 0
	check_less_line = 0
	enough_less_line = 0
	for line in filee:
		pure_data = ""
		pure_data = line.rstrip('\n').split(' ')
		if pure_data[0] is '0':
			if already_get_target == 0:
				pass_count+=1
				limit_time = pure_data[4].split(":")
				now_time = datetime.now()
				time1 = timedelta(hours=int(limit_time[0]), minutes=int(limit_time[1]), seconds=int(limit_time[2]))
				time2 = timedelta(hours=now_time.hour, minutes=now_time.minute, seconds=now_time.second)
				time3 = timedelta(hours=0, minutes=0, seconds=0)
				
				if (time1 - time2) > time3:
					lock_countt.append(countt)
					already_get_target = 1
					deal_data = pure_data
				elif (time1 - time2) <= time3:
					lock_countt.append(countt)
			else :
				check_less_line = check_less_line + 1
				if check_less_line > 10:
					enough_less_line = 1
					break
		countt+=(len(line))
	if len(lock_countt) > 0 :
		for seek_num in lock_countt :
			filee.seek(seek_num, 0)
			filee.write('1')
	filee.close()

	try:
		valuee1 = deal_data[2]
		valuee2 = int(deal_data[3])
	except:
		return ["img/0.jpg", 5, 0]

	if enough_less_line==1:
		return [valuee1, valuee2, 1]
	else :
		return [valuee1, valuee2, 0]


#the api can only edit furtre schedule. 
#It can edit schedule not to print image by setting img_check=0 or edit furtre schedule to print new image.
def edit_schedule(schedule_dir, next_img, img_check, img_id, img_dir, img_time, img_end_time):
	
	#can not edit scheduling next item
	if next_img <= 1:
		return "error next_img <= 1"
	date_now = date.today()
	schedule_file = ("broad_" + str(date_now.year) + "_" + str(date_now.month) + "_" + str(date_now.day) + ".txt")
	new_file = ("new_" + schedule_file)
	schedule_file = os.path.join(schedule_dir,("static/log/"+schedule_file))
	new_file = os.path.join(schedule_dir,("static/log/"+new_file))
	file1 = open(schedule_file, "r")
	file2 = open(new_file, "w")

	
	pure_data = ""
	deal_data = (str(img_check) + ' ' + img_id + ' ' + img_dir + ' ' + str(img_time) + ' ' + img_end_time + '\n')
	pass_count = 0
	for line in file1:
		pure_data = ""
		pure_data = line.rstrip('\n').split(' ')
		if pure_data[0] is '0':
			pass_count+=1
			if pass_count == next_img:
				file2.write(deal_data)
			else :
				file2.write(line)
		else :
			file2.write(line)
	
	file1.close()
	file2.close()


	return "scuess"








