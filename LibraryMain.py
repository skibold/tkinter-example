from LibraryView import *
from LibraryDB import LibraryDB
from sys import argv

logfile = None
if(len(argv) >= 2):
	logfile = argv[1]
else:
	logfile = "library.log"
lib = LibraryDB(logfile)
		
mw = Tk()
mw.title("Library")
mw.geometry('1000x500')

# setup frames, but don't pack yet
bs = BookSearchFrame(lib, mw)
ls = LoanSearchFrame(lib, mw)
bm = BorrowerManagement(lib, mw)
fm = FineManagement(lib, mw)

# toggle visible frame functions
def showBookSearch():
	fm.pack_forget()
	bm.pack_forget()
	ls.pack_forget()
	bs.pack(fill='both', expand=True)
def showLoanSearch():
	fm.pack_forget()
	bm.pack_forget()
	bs.pack_forget()
	ls.pack(fill='both', expand=True)
def showFines():
	bm.pack_forget()
	bs.pack_forget()
	ls.pack_forget()
	fm.pack(fill='both', expand=True)
def showBorrower():
	fm.pack_forget()
	bs.pack_forget()
	ls.pack_forget()
	bm.pack(fill='both', expand=True)

MenuFrame = Frame(mw)
Button(MenuFrame, text="Book Search", command=showBookSearch).grid(column=1,row=0)
Button(MenuFrame, text="Loan Search", command=showLoanSearch).grid(column=2,row=0)
Button(MenuFrame, text="Manage Fines", command=showFines).grid(column=3,row=0)
Button(MenuFrame, text="Manage Borrowers", command=showBorrower).grid(column=4,row=0)
MenuFrame.pack(pady=5)

# show book search frame on startup
showBookSearch()

mw.mainloop()
