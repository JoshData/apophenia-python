# ctypes bindings for the apophenia C library.

from ctypes import *

apop = CDLL("libapophenia.so")

class apop_name(Structure):
	_fields_ = [
		("title", c_char_p),
		("vector", c_char_p),
		("col", POINTER(c_char_p)),
		("row", POINTER(c_char_p)),
		("text", POINTER(c_char_p)),
		("colct", c_int),
		("rowct", c_int),
		("textct", c_int),
	]

class gsl_matrix(Structure):
	_fields_ = [
		("size1", c_size_t),
		("size2", c_size_t),
		("tda", c_size_t),
		("data", POINTER(c_double)),
		("block", c_void_p),
		("owner", c_int),
	]
class gsl_vector(Structure):
	_fields_ = [
		("size", c_size_t),
		("stride", c_size_t),
		("data", POINTER(c_double)),
		("block", c_void_p),
		("owner", c_int),
	]

class apop_data(Structure):
	_fields_ = [
		("matrix", POINTER(gsl_matrix)),
		("more", c_void_p),
		("names", POINTER(apop_name)),
		("text", POINTER(POINTER(c_char_p))),
		("textsize", c_size_t*2),
		("vector", POINTER(gsl_vector)),
		("weights", POINTER(gsl_vector)),
		("error", c_char),
	]

apop.apop_data_alloc_base.argtypes = [c_int, c_int, c_int]
apop.apop_data_alloc_base.restype = POINTER(apop_data)

apop.apop_data_free_base.argtypes = [POINTER(apop_data)]
apop.apop_data_free_base.restype = None

apop.apop_data_copy.restype = POINTER(apop_data)

Output_declares = [c_char_p, c_void_p, c_char, c_char] # (output_name, FILE * output_pipe, output_type, output_append)
apop.apop_data_print_base.argtypes = [POINTER(apop_data)] + Output_declares
apop.apop_data_print_base.restype = None

apop.apop_data_show.argtypes = [POINTER(apop_data)]
apop.apop_data_show.restype = None

apop.apop_data_get_base.restype = c_double

apop.apop_data_stack_base.argtypes = [POINTER(apop_data), POINTER(apop_data), c_char, c_char]
apop.apop_data_stack_base.restype = POINTER(apop_data)

__ALL__ = [apop, apop_data]

