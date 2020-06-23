from DBConnection import *
from datetime import date, datetime, timedelta
import re
from Logger import *

class LibraryDB:
	def __init__(self, logfile=None):
		self.logfile = logfile
		self.db = DBConnection("library", logfile)
		self.db.connect()

	def __exit__(self, exc_type, exc_value, traceback):
		self.db.close()

	def book_search(self, searchStr):
		searchStr = "%" + searchStr.lower() + "%" 
		sql = "select * \
			from full_catalog\
			where lower(isbn) like '%s' or\
			lower(title) like '%s' or\
			lower(author) like '%s';"
		args = (searchStr, searchStr, searchStr)
		return self.db.query(sql, args)

	def num_checkouts(self, borrower):
		sql = "select count(*) as checkouts\
			from book_loans\
			where card_id='%s' and date_in is NULL;"
		args = (borrower)
		checkouts = self.db.query(sql, args)[0]["checkouts"]
		return checkouts

	def book_available(self, isbn):
		sql = "select available from full_catalog where isbn='%s';"
		args = (isbn)
		available = self.db.query(sql, args)
		if(len(available) and available[0]["available"] == 1):
			return True
		else:
			return False		

	def book_checkout(self, isbn, borrower):
		num_co = self.num_checkouts(borrower)
		available = self.book_available(isbn)

		if(num_co >= 3):
			log(self.logfile, "book_checkout", "Failed to checkout %s, borrower %s already has 3 books\n" % (isbn, borrower))
			return "FAIL_MAX_CHECKOUT"

		if(available is False):
			log(self.logfile, "book_checkout", "Failed to checkout %s, it is already out\n" % isbn)
			return "FAIL_BOOK_UNAVAILABLE"

		date_out = datetime.now()
		due_date = date_out + timedelta(days=14)
		table = "book_loans"
		cols = ["isbn", "card_id", "date_out", "due_date"]
		vals = [isbn, borrower, date_out, due_date]		
		result = self.db.insert(table, cols, vals)
		if(result == RC_FK_VIOLATION):
			log(self.logfile, "book_checkout", "Failed to checkout %s, borrower %s is unknown\n" % (isbn, borrower))
			return "FAIL_UNKNOWN_BORROWER"
		else:
			return result	

	def book_checkin(self, loan_id):
		table = "book_loans"
		cols = ["date_in"]
		date_in = datetime.now()
		vals = [date_in]
		where = "loan_id = '%s'" % loan_id
		return self.db.update(table, cols, vals, where)		

	def find_book_loan(self, searchStr):
		searchStr = "%" + searchStr.lower() + "%"
		sql = "select bl.loan_id, b.card_id, bl.isbn, b.bname \
			from borrower b, book_loans bl \
			where b.card_id=bl.card_id and \
				bl.date_in is NULL and \
				(lower(b.card_id) like '%s' or \
				lower(bl.isbn) like '%s' or \
				lower(b.bname) like '%s' or \
				lower(bl.loan_id) like '%s');"
		args = (searchStr, searchStr, searchStr, searchStr)
		return self.db.query(sql, args)

	def new_borrower(self, ssn, bname, address, phone):
		table = "borrower"
		cols = []
		vals = []
		if(ssn is not None):
			cols.append("ssn")
			vals.append(ssn)
		if(bname is not None):
			cols.append("bname")
			vals.append(bname)
		if(address is not None):
			cols.append("address")
			vals.append(address)
		if(phone is not None):
			cols.append("phone")
			vals.append(phone)
		result = self.db.insert(table, cols, vals)
		if(result == RC_PK_VIOLATION):
			log(self.logfile, "new_borrower", "Error: borrower with ssn %s already exists\n" % ssn)
			return "FAIL_BORROWER_EXISTS"
		elif(result == RC_ERROR):
			log(self.logfile, "new_borrower", "Error: a required field (ssn, bname, address) is null\n")
			return "FAIL_NULL_FIELD"
		else:
			return "SUCCESS"

	def find_borrower(self, searchStr):
		searchStr = "%" + searchStr.lower() + "%"
		sql = "select * from borrower where card_id like '%s' or\
			ssn like '%s' or lower(bname) like '%s';"
		args = (searchStr, searchStr, searchStr)
		return self.db.query(sql, args)

	def borrower_debts(self):
		sql = "select sub.card_id, b.ssn, b.bname, sub.total_due \
			from borrower b, \
			(select b.card_id, sum(f.fine_amt) total_due \
			from book_loans b, fines f \
			where b.loan_id = f.loan_id and f.paid = 'N' \
			group by b.card_id) as sub \
			where b.card_id = sub.card_id;"
		return self.db.query(sql, ())

	def itemized_fines_all(self, card_id):
		sql = "select bl.loan_id, bl.isbn, bl.due_date, f.fine_amt, f.paid \
			from book_loans bl, fines f \
			where f.loan_id = bl.loan_id and bl.card_id = %s;"
		return self.db.query(sql, card_id)

	def itemized_fines_unpaid(self, card_id):
		sql = "select bl.loan_id, bl.isbn, bl.due_date, f.fine_amt, f.paid \
			from book_loans bl, fines f \
			where f.loan_id = bl.loan_id and bl.card_id = %s and f.paid = 'N';"
		return self.db.query(sql, card_id)

	def assess_fines(self):
		today = datetime.now() #.date()
		perDay = 0.25
		table = "fines"
		cols = ["fine_amt", "loan_id", "paid"]
		where = "loan_id = '%s'"

		# refresh the connection
		self.db.refresh()

		# fine query
		fine_sql = "select paid from fines where loan_id = '%s'"

		# late books still checked out
		books_out_sql = "select loan_id, due_date, current_timestamp as date_in\
			from book_loans\
			where due_date < '%s' and date_in is null;"
		late_books = self.db.query(books_out_sql, today)

		# late books turned in
		books_in_sql = "select loan_id, due_date, date_in\
				from book_loans\
				where date_in is not null and due_date < date_in;"
		late_books.extend(self.db.query(books_in_sql, ()))	
		
		failed_fines = []
		for b in late_books:
			loan_id = b["loan_id"]
			due_date = b["due_date"]
			date_in = b["date_in"]
			fine_amt = (date_in-due_date).days*perDay
			fine = self.db.query(fine_sql, loan_id)	

			if(len(fine) == 0):
				if(self.db.insert("fines", cols, [fine_amt,loan_id,"N"]) != RC_SUCCESS):
					failed_fines.append(loan_id)
			elif(fine[0]["paid"] == "N"):
				self.db.update("fines", [cols[0]], [fine_amt], where % loan_id)
			else:
				log(self.logfile, "assess_fines", "Fine already paid for loan %s\n" % loan_id)
		if(len(failed_fines)):
			log(self.logfile, "assess_fines", "Warning: could not assess fines for loans: %s\n" % failed_fines)
		return failed_fines

	def pay_fine(self, loan_id):
		table = "fines"
		cols = ["paid"]
		vals = ["Y"]
		where = "loan_id = '%s' and\
			not exists (select *\
				from book_loans\
				where loan_id = '%s' and\
					date_in is null);" % (loan_id, loan_id)		
		return self.db.update(table, cols, vals, where)
		
		
