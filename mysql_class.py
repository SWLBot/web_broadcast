import os.path
import pymysql

class mysqll:
	def __init__(self, db=None, cursor=None):
		self.db = db;
		self.cursor = cursor;
		
	def __enter__(self):
		return self
	
	#file dir where file store host\n user\n password\n dbname\n
	def connectt(self, file_name):
		if not os.path.isfile(file_name) :
			return -1
		
		filee = open(file_name,"r")
		hostt = filee.readline().rstrip('\n').strip(' ')
		userr = filee.readline().rstrip('\n').strip(' ')
		tokenn = filee.readline().rstrip('\n').strip(' ')
		dbname = filee.readline().rstrip('\n').strip(' ')
		filee.close()
		
		try:
			self.db = pymysql.connect(hostt, userr, tokenn, dbname, use_unicode=True, charset="utf8")
			self.cursor = self.db.cursor()
			#cursor.execute('SET NAMES utf8;') 
			#cursor.execute('SET CHARACTER SET utf8;')
			#cursor.execute('SET character_set_connection=utf8;')
		except:
			return -1
		
		return 1
	
	#drop old table if exist!! be careful when using it!! 
	def create_table(self, sql):
		try:
			self.cursor.execute("DROP TABLE IF EXISTS EMPLOYEE")
			self.cursor.execute(sql)
		except:
			return -1
		return 1
	
	#insert, update, delete query
	def cmdd(self, sql):
		try:
			self.cursor.execute(sql)
			self.db.commit()
		except:
			self.db.rollback()
			return -1
		return 1
	
	#find query
	def queryy(self, sql):
		try:
			self.cursor.execute(sql)
			result = self.cursor.fetchall()
		except:
			result = -1
		return result

	def closee(self):
		self.db.close()
		
	def __exit__(self, exc_type, exc_value, traceback):
		self.db.close()
		
		