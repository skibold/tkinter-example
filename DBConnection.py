import mysql.connector as mysql
import re
from Logger import *

RC_PK_VIOLATION = "PK_VIOLATION"
RC_FK_VIOLATION = "FK_VIOLATION"
RC_ERROR = "ERROR"
RC_SUCCESS = "SUCCESS"
RC_NO_ROWS = "NO_ROWS"

class DBConnection:
	def __init__(self, db, logfile=None):
		self.dbname = db
		self.logfile = logfile
		self.con = None
		#self.connect()

	def refresh(self):
		try:
			self.close()
			self.connect()
		except Exception as ex:
			return self.handle_ex(ex)

	def connect(self):
		try:
			self.con = mysql.connect(user='root', password='r00t', host='127.0.0.1', database=self.dbname)
		except Exception as ex:
			return self.handle_ex(ex)
		log(self.logfile, "connect", "Connected to %s\n" % self.dbname)

	def close(self):
		self.con.close()
		log(self.logfile, "close", "Closed connection to %s\n" % self.dbname)

	def query(self, q, args): # args must be a tuple, could be empty
		cursor = self.con.cursor(buffered=True, dictionary=True)
		formattedQ = q % args
		log(self.logfile, "query", "%s\n" % formattedQ)
		cursor.execute(formattedQ)
		results=[]
		for row in cursor:
			results.append(row)
		cursor.close()
		log(self.logfile, "query", "Returned %d results\n" % len(results))
		return results

	def insert(self, table, cols, vals):
		sql = "insert into %s (" % table
		for c in cols:
			sql += "%s," % c
		sql = sql[0:-1] + ")" # replace last comma with close paren

		sql += " values ("
		for v in vals:
			sql += "'%s'," % v
		sql = sql[0:-1] + ");" # replace last comma with close paren
		log(self.logfile, "insert", "%s\n" % sql)

		cursor = self.con.cursor()
		try:
			cursor.execute(sql)
		except Exception as ex:
			cursor.close()
			return self.handle_ex(ex)
		count = cursor.rowcount
		self.con.commit()
		cursor.close()
		log(self.logfile, "insert", "Inserted %d rows\n" % count)
		if(count == 0):
			return RC_NO_ROWS
		return RC_SUCCESS

	def update(self, table, cols, vals, where):
		sql = "update %s set " % table
		for i in range(0, len(cols)):
			sql += "%s = '%s'," % (cols[i], vals[i])
		sql = sql[0:-1] # remove last comma

		if(where is not None):
			sql += " where %s" % where
		sql = sql + ";"
		log(self.logfile, "update", "%s\n" % sql)

		cursor = self.con.cursor()
		try:
			cursor.execute(sql)
		except Exception as ex:
			cursor.close()
			return self.handle_ex(ex)
		count = cursor.rowcount
		self.con.commit()
		cursor.close()
		log(self.logfile, "update", "Updated %d rows\n" % count)
		if(count == 0):
			return RC_NO_ROWS
		return RC_SUCCESS

	def handle_ex(self, e):
		msg = "%s\n" % format(e)
		log_and_print(self.logfile, "handle_ex", msg)
		if(len(re.findall(r'.*FOREIGN KEY', format(e)))):
			return RC_FK_VIOLATION
		elif(len(re.findall(r'.*Duplicate', format(e)))):
			return RC_PK_VIOLATION
		else:
			return RC_ERROR

