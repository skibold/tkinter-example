from Tkinter import *
from MyWidgets import *
from LibraryDB import LibraryDB

class BookSearchFrame(Frame):
	col_heads = ['isbn','title','authors','available']
	isbn_ix = 0
	title_ix = 1
	auth_ix = 2
	avail_ix = 3
	def __init__(self, lib, mw):
		Frame.__init__(self,mw)
		self.lib = lib
		self.searchframe = Frame(self)
		self.searchframe.pack()
		Label(self.searchframe, text="Search by Isbn, Title, Author").grid(column=1, row=0, padx=2)
		
		self.ebox = Entry(self.searchframe)
		self.ebox.grid(column=2, row=0)
		self.ebox.focus()
		Button(self.searchframe, text="Search", command=self.search).grid(column=3, row=0)
		Button(self.searchframe, text="Clear", command=self.clear).grid(column=4, row=0)

		Label(self.searchframe, text="Borrower Card Number").grid(column=1, row=1, padx=2)
		self.bbox = Entry(self.searchframe)
		self.bbox.grid(column=2, row=1)
		Button(self.searchframe, text="Checkout", command=self.checkout).grid(column=3, row=1)
		Button(self.searchframe, text="Checkin", command=self.checkin).grid(column=4,row=1)
		self.list = MListBox(self, self.col_heads)
		self.list.pack(side='top', fill='both', expand=True)

	def clear(self):
		self.ebox.delete(0,'end')
		self.list.clear()

	def search(self):
		if(self.ebox.get() == ""):
			return
		isbnmap={}
		results = self.lib.book_search(self.ebox.get())
		#print "%d results" % len(results)
		for row in results:
			isbn = row["isbn"]
			auth = row["author"]
			if(isbn in isbnmap): 
				auth += ", %s" % isbnmap[isbn][self.auth_ix]
			isbnmap[isbn] = (isbn, row["title"], auth, "Y" if row["available"] else "N")
			
		self.list.clear()		
		self.list.insert(isbnmap.values())

	def checkin(self):
		success = False
		for row in self.list.getselection():
			loan = self.lib.find_book_loan(row[self.isbn_ix])
			if(len(loan)):
				success = True
				result = self.lib.book_checkin(loan[0]["loan_id"])
			else:
				result = "No lien on book"
			if(result != "SUCCESS"):
				Popup("Error","Failed to checkin %s\n%s" %(row[self.isbn_ix],result))
		if(success): # refresh display if at least one checkout succeeded
			self.search()

	def checkout(self):
		success = False
		borrower = self.bbox.get()
		if(borrower == ""):
			Popup("Error","Enter a borrower card number")
			return
		for row in self.list.getselection():
			result = self.lib.book_checkout(row[self.isbn_ix], borrower)
			#print result
			if(result == "SUCCESS"):
				success = True
				#print "Checked out %s" % row[self.title_ix]
			else:
				Popup("Error","Failed to checkout %s\n%s" % (row[self.isbn_ix], result))			
		if(success): # refresh display if at least one checkout succeeded
			self.search()

class LoanSearchFrame(Frame):
	col_heads = ['loan id','card id','name','isbn']
	loan_ix = 0
	card_ix = 1
	name_ix = 2
	isbn_ix = 3
	def __init__(self, lib, mw):
		Frame.__init__(self,mw)
		self.lib = lib
		self.searchframe = Frame(self)
		self.searchframe.pack()
		Label(self.searchframe, text="Search by Isbn, Loan ID, Card ID, Card Name").grid(column=1, row=0, padx=2)
		self.ebox = Entry(self.searchframe)
		self.ebox.grid(column=2, row=0)
		self.ebox.focus()
		Button(self.searchframe, text="Search", command=self.search).grid(column=3, row=0)
		Button(self.searchframe, text="Clear", command=self.clear).grid(column=4, row=0)
		Button(self.searchframe, text="Checkin", command=self.checkin).grid(column=5, row=0)
		self.list = MListBox(self, self.col_heads)
		self.list.pack(side='top', fill='both', expand=True)

	def search(self):
		if(self.ebox.get() == ""):
			return
		values=[]
		for row in self.lib.find_book_loan(self.ebox.get()):
			values.append((row["loan_id"], row["card_id"], row["bname"], row["isbn"]))
		self.list.clear()
		self.list.insert(values)

	def clear(self):
		self.ebox.delete(0,'end')
		self.list.clear()

	def checkin(self):
		success = False
		for row in self.list.getselection():			
			result = self.lib.book_checkin(row[self.loan_ix])
			if(result != "SUCCESS"):
				Popup("Error","Failed to checkin %s\n%s" %(row[self.isbn_ix],result))
			else:
				success = True
		if(success): # refresh display if at least one checkout succeeded
			self.search()

class BorrowerManagement(Frame):
	col_heads = ["card id", "ssn", "name", "address", "phone"]
	def __init__(self, lib, mw):
		Frame.__init__(self, mw)
		self.lib = lib
		self.newframe = Frame(self)
		self.newframe.pack(fill='both', expand=True)
		Label(self.newframe, text="Name").grid(column=1, row=0, sticky='nsew', padx=2)
		self.nbox = Entry(self.newframe)
		self.nbox.grid(column=2, row=0, sticky='nsew', padx=2)
		Label(self.newframe, text="SSN").grid(column=1, row=1, sticky='nsew', padx=2)
		self.sbox = Entry(self.newframe)
		self.sbox.grid(column=2, row=1, sticky='nsew', padx=2)
		Label(self.newframe, text="Address").grid(column=1, row=2, sticky='nsew', padx=2)
		self.abox = Entry(self.newframe)
		self.abox.grid(column=2, row=2, sticky='nsew', padx=2)
		Label(self.newframe, text="Phone").grid(column=1, row=3, sticky='nsew', padx=2)
		self.pbox = Entry(self.newframe)
		self.pbox.grid(column=2, row=3, sticky='nsew', padx=2)
		Button(self.newframe, text="Create", command=self.create).\
			grid(column=3, row=1, sticky='nsew', padx=2)
		Button(self.newframe, text="Clear", command=self.clearnew).\
			grid(column=3, row=2, sticky='nsew', padx=2)
		self.newframe.grid_columnconfigure(2, weight=2)

		self.searchframe = Frame(self)
		self.searchframe.pack()
		Label(self.searchframe, text="Search by Card ID, Name, SSN").grid(column=1, row=0, padx=2)
		self.ebox = Entry(self.searchframe)
		self.ebox.grid(column=2, row=0)
		self.ebox.focus()
		Button(self.searchframe, text="Search", command=self.search).grid(column=3, row=0)
		Button(self.searchframe, text="Clear", command=self.clearsearch).grid(column=4, row=0)
		self.list = MListBox(self, self.col_heads)
		self.list.pack(fill='both', expand=True)

	def search(self):
		if(self.ebox.get() == ""):
			return
		values = []
		for b in self.lib.find_borrower(self.ebox.get()):
			values.append((b["card_id"], b["ssn"], b["bname"], b["address"], b["phone"]))
		self.list.clear()
		self.list.insert(values)

	def clearsearch(self):
		self.ebox.delete(0,'end')
		self.list.clear()

	def create(self):
		if(self.nbox.get() == ""):
			Popup("Error","Name must not be empty")
			return
		if(self.sbox.get() == ""):
			Popup("Error","SSN must not be empty")
			return
		if(self.abox.get() == ""):
			Popup("Error","Address must not be empty")
			return
		result = self.lib.new_borrower(self.sbox.get(), self.nbox.get(), self.abox.get(), self.pbox.get())
		if(result == "SUCCESS"):
			Popup("Success","Created new borrower %s" % self.sbox.get())
		else:
			Popup("Error","Failed to create borrower %s\n%s" % (self.sbox.get(),result))

	def clearnew(self):
		self.nbox.delete(0,'end')
		self.sbox.delete(0,'end')
		self.abox.delete(0,'end')
		self.pbox.delete(0,'end')

class FineManagement(Frame):
	top_heads = ["card id", "ssn", "name", "debt"]
	card_ix = 0
	ssn_ix = 1
	name_ix = 2
	debt_ix = 3
	detail_heads = ["loan id", "isbn", "due date", "fine", "paid"]
	loan_ix = 0
	isbn_ix = 1
	due_ix = 2
	fine_ix = 3
	paid_ix = 4
	def __init__(self, lib, mw):
		Frame.__init__(self, mw)
		self.lib = lib
		self.topframe = Frame(self)
		self.topframe.pack()
		Label(self.topframe, text="Total debts by borrower").grid(column=1,row=0, padx=2)
		Button(self.topframe, text="Refresh", command=self.refresh).grid(column=2,row=0, padx=2)
		self.list = MListBox(self, self.top_heads)
		self.list.pack(side='top', fill='both', expand=True)
		self.list.bind("<ButtonRelease-1>", self.populatedetails)	

		self.detailframe = Frame(self)
		self.detailframe.pack()
		Label(self.detailframe, text="Itemized fines").grid(column=1,row=0, padx=2)
		Button(self.detailframe, text="Pay", command=self.pay).grid(column=2,row=0)
		self.togvar = IntVar()
		Checkbutton(self.detailframe, text="Show All", command=self.toggle, variable=self.togvar).grid(column=3, row=0)
		self.details = MListBox(self, self.detail_heads)
		self.details.pack(side='top', fill='both', expand=True)

		self.populatelist()

	def refresh(self):
		failures = self.lib.assess_fines()
		if(len(failures)):
			Popup("Warning","Could not assess fines for loans %s\n" % failures)
		self.populatelist()

	def pay(self):
		success = False
		for row in self.details.getselection():
			result = self.lib.pay_fine(row[self.loan_ix])
			if(result == "SUCCESS"):
				success = True
			elif(result == "NO_ROWS"):
				if(row[self.paid_ix] == "Y"):
					Popup("Error", "Fine already paid for loan %s\n" % row[self.loan_ix])
				else:
					Popup("Error","Could not pay fine for loan %s\nBook %s still out" %\
						(row[self.loan_ix], row[self.isbn_ix]))
		if(success): # refresh display if at least one checkout succeeded
			self.populatedetails(None)

	def toggle(self):
		self.populatedetails(None)

	def populatelist(self):
		debts = []
		for row in self.lib.borrower_debts():
			debts.append((row["card_id"], row["ssn"], row["bname"], row["total_due"]))
		self.details.clear()
		self.list.clear()
		self.list.insert(debts)

	def populatedetails(self, event):
		row = self.list.getselection()[0]
		card = row[self.card_ix]
		items = []
		fines = []
		if(self.togvar.get()):
			fines = self.lib.itemized_fines_all(card)
		else:
			fines = self.lib.itemized_fines_unpaid(card)
		for i in fines:
			items.append((i["loan_id"], i["isbn"], i["due_date"], i["fine_amt"], i["paid"]))
		self.details.clear()
		self.details.insert(items)


