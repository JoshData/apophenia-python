from ctypes import *

from bindings import *

libc = cdll.LoadLibrary("libc.so.6") 

class Data:
	ptr = None

	def __init__(self, rows=None, float_cols=None, text_cols=None):
		if isinstance(rows, POINTER(apop_data)):
			# Clone.
			self.ptr = rows
		else:
			# New.
			self.ptr = apop.apop_data_alloc_base(rows, rows, float_cols) # vector size == matrix row count
			if text_cols > 0:
				apop.apop_text_alloc(self.ptr, rows, text_cols)
			# TODO: Allocate weights vector.

	def __del__(self):
		apop.apop_data_free_base(self.ptr)

	@property
	def sizetuple(self):
		return (self.ptr.contents.matrix.contents.size1, self.ptr.contents.matrix.contents.size2, self.ptr.contents.textsize[1])

	def __str__(self):
		# Call apop_data_print writing to an in-memory buffer, assumed to be UTF-8,
		# and return the contents of that buffer.
		bufp = pointer(c_char_p(0))
		sizep = pointer(c_int())
		f = libc.open_memstream(bufp, sizep)
		if not f: raise OSError("Error opening memory stream.") # sanity check
		try:
			apop.apop_data_print_base(self.ptr, None, f, b"f", b" ")
			libc.fflush(f) # must call so open_memstream fills buffer
			return bufp.contents.value.decode("utf8", "replace")
		finally:
			libc.fclose(f)
			if bufp.contents:
				libc.free(bufp.contents)

	def __bool__(self):
		if self.sizetupletuple[0] == 0:
			# no rows
			return False
		elif self.sizetuple[0] > 1 or self.sizetuple[1] > 0:
			# has more than one row or has matrix
			return True
		else:
			return bool(self[0])

	@property
	def title(self):
		return self.ptr.contents.names.title.value.decode("utf8")
	@title.setter
	def title(self, value):
		self.ptr.contents.names.contents.title = libc.strdup(c_char_p(value.encode("utf8")))

	@property
	def vector_name(self):
		return self.ptr.contents.names.vector.value.decode("utf8")
	@vector_name.setter
	def vector_name(self, value):
		self.ptr.contents.names.contents.vector = libc.strdup(c_char_p(value.encode("utf8")))

	def __getitem__(self, key):
		return self.getset("get", key)

	def getset(self, mode, key, value=None):
		if isinstance(key, int):
			# self[int]: Access the vector value at the given row.
			if key < 0 or key >= self.sizetuple[0]: raise IndexError()
			if mode == "get":
				return apop.apop_data_get_base(self.ptr, c_int(key), -1, None, None, None)
			elif mode == "set":
				# c_double will coerce to float or raise an exception
				apop.apop_data_set_base(self.ptr, c_int(key), -1, c_double(value), None, None, None)

		elif isinstance(key, tuple):
			# self[(int, int)]: Access the matrix or text value at the given row and column 
			# (text columns start after the matrix columns).
			if key[0] < 0 or key[0] >= self.sizetuple[0]: raise IndexError()
			if key[1] < 0: raise IndexError()
			if key[1] < self.sizetuple[1]:
				# Access the matrix.
				if mode == "get":
					return apop.apop_data_get_base(self.ptr, c_int(key[0]), c_int(key[1]), None, None, None)
				elif mode == "set":
					# c_double will coerce to float or raise an exception
					apop.apop_data_set_base(self.ptr, c_int(key[0]), c_int(key[1]), c_double(value), None, None, None)
			elif key[1]-self.sizetuple[1] < self.sizetuple[2]:
				# Access the text.
				if mode == "get":
					return self.ptr.contents.text[key[0]][key[1]-self.sizetuple[1]].decode("utf8")
				elif mode == "set":
					if not isinstance(value, str): raise TypeError()
					apop.apop_text_set(self.ptr, c_int(key[0]), c_int(key[1]-self.sizetuple[1]), b"%s", value.encode("utf8"))
			else:
				raise IndexError()

		else:
			raise TypeError()

	def __setitem__(self, key, value):
		self.getset("set", key, value)

	def rowname(self, row, value=Ellipsis):
		if row < 0 or row >= self.sizetuple[0]: raise IndexError()
		if value != Ellipsis and not isinstance(value, str): raise TypeError()
		if value == Ellipsis:
			# Ellipsis is standing in as a sentinel for a get operation
			if row >= self.ptr.contents.names.contents.rowct: return None
			return self.ptr.contents.names.contents.row[row].decode("utf8")
		else:
			# Set the row name. Make sure the name slot is allocated first.
			while row >= self.ptr.contents.names.contents.rowct:
				apop.apop_name_add(self.ptr.contents.names, b"", b"r"[0])
			self.ptr.contents.names.contents.row[row] = libc.strdup(value.encode("utf8"))

	def __or__(self, other):
		return Data(apop.apop_data_stack_base(self.ptr, other.ptr, b'c', 0))
	def __xor__(self, other):
		return Data(apop.apop_data_stack_base(self.ptr, other.ptr, b'r', 0))

	def clone(self):
		return Data(apop.apop_data_copy(self.ptr))

if __name__ == "__main__":
	d = Data(2, 1, 1)
	d.title = "Hi"
	d.vector_name = "Bye"
	d.rowname(0, "A")
	d.rowname(1, "B")
	d[0] = -1
	d[1] = -2
	d[0, 0] = 1
	d[1, 0] = 2
	d[0, 1] = "x"
	d[1, 1] = "y"
	d |= d
	d ^= d
	print(d)
