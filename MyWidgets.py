from Tkinter import *
import ttk
import tkFont

class Popup(Tk):
	def __init__(self, title, msg):
		Tk.__init__(self)
		self.title(title.title())
		Label(self, text=msg).pack(padx=2, pady=2)
		Button(self, text="Ok", command=self.destroy).pack(padx=2, pady=2)

class MListBox(ttk.Frame):	
	def __init__(self, mw, col_heads):
		ttk.Frame.__init__(self, mw)
		# create a treeview with dual scrollbars
		self.tree = ttk.Treeview(columns=col_heads, show="headings")
		vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
		hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
		self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
		self.tree.grid(column=0, row=0, sticky='nsew', in_=self)
		vsb.grid(column=1, row=0, sticky='ns', in_=self)
		hsb.grid(column=0, row=1, sticky='ew', in_=self)
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)
		self.cols = col_heads
		for col in col_heads:
			self.tree.heading(col, text=col.title(), command=lambda c=col: self.sortby(c, 0))
			# adjust the column's width to the header string
			self.tree.column(col,width=tkFont.Font().measure(col.title()))
		self.rows={}

	def sortby(self, col, descending):
		data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
		data.sort(reverse=descending)
		for ix, item in enumerate(data):
			self.tree.move(item[1], '', ix)
		self.tree.heading(col, command=lambda col=col: self.sortby(col, int(not descending)))

	def insert(self, array_of_tuples): # each tuple should have num(attributes) = num(columns)
		for t in array_of_tuples:
			iid = self.tree.insert('', 'end', values=t)
			self.rows[iid] = t	
			for i, val in enumerate(t):
				w = tkFont.Font().measure(val)
				if(self.tree.column(self.cols[i], width=None) < w):
					self.tree.column(self.cols[i], width=w)

	def delete(self, iid):
		self.rows.delete(iid)
		self.tree.delete(self.tree.item(iid))

	def clear(self):
		self.rows.clear()
		self.tree.delete(*self.tree.get_children())

	def getselection(self):
		selected_rows = []
		for iid in self.tree.selection():
			selected_rows.append(self.rows[iid])
		return selected_rows

	def getall(self):
		return self.rows

	def bind(self, event, command):
		self.tree.bind(event, command)
