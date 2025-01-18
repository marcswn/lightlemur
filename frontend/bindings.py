import ctypes
import os
import platform
from typing import Optional
import frontend.reprutils as reprutils

SYSTEM = platform.system()
if SYSTEM == "Darwin":
    LIB_FILE = "liblightlemur.dylib"  
elif SYSTEM == "Windows":
    LIB_FILE = "liblightlemur.dll"   
else:
    LIB_FILE = "liblightlemur.so"    

lib_path = os.path.join(
    os.path.dirname(__file__),  
    "..",                      
    LIB_FILE
)

lib = ctypes.CDLL(lib_path)

class lemur_float(ctypes.c_float): #TODO
    pass

class KernelTensor(ctypes.Structure):
    _fields_ = [
        ("array",    ctypes.POINTER(lemur_float)),  
        ("length",   ctypes.c_size_t),
        ("shape",    ctypes.c_size_t * 5),            
        ("stride",   ctypes.c_int64  * 5),            
        ("computed", ctypes.c_bool),
    ]

class Tensor(ctypes.Structure):
    pass 

class Expression(ctypes.Structure):
    _fields_ = [
        ("t0",    ctypes.POINTER(Tensor)),  
        ("t1",    ctypes.POINTER(Tensor)),
        ("backward_func", ctypes.c_int),            
    ] 

class Tensor(ctypes.Structure):
    _fields_ = [
        ("k",             ctypes.POINTER(KernelTensor)), 
        ("comes_from",    ctypes.POINTER(Expression)),    
        ("requires_grad", ctypes.c_bool),
        ("grad",          ctypes.POINTER(KernelTensor)),  
    ]

#from interface.h

# tensor* empty_tensor(size_t shape[5], bool retain_grad);
lib.empty_tensor.argtypes = [(ctypes.c_size_t * 5), ctypes.c_bool]
lib.empty_tensor.restype  = ctypes.POINTER(Tensor)

# void free_tensor(tensor* t);
lib.free_tensor.argtypes = [ctypes.POINTER(Tensor)]
lib.free_tensor.restype  = None

# void backwards(tensor* t);
lib.backwards.argtypes = [ctypes.POINTER(Tensor)]
lib.backwards.restype  = None

# tensor* mul(tensor* t0, tensor* t1, bool retain_grad);
lib.mul.argtypes = [ctypes.POINTER(Tensor), ctypes.POINTER(Tensor), ctypes.c_bool]
lib.mul.restype  = ctypes.POINTER(Tensor)

# tensor* add(tensor* t0, tensor* t1, bool retain_grad);
lib.add.argtypes = [ctypes.POINTER(Tensor), ctypes.POINTER(Tensor), ctypes.c_bool]
lib.add.restype  = ctypes.POINTER(Tensor)

# tensor* relu(tensor* t0, bool retain_grad);
lib.relu.argtypes = [ctypes.POINTER(Tensor), ctypes.c_bool]
lib.relu.restype  = ctypes.POINTER(Tensor)

#tensor * sum(tensor *t0, tensor *dim_data, bool retain_grad)
lib.sum.argtypes = [ctypes.POINTER(Tensor), ctypes.POINTER(Tensor), ctypes.c_bool]
lib.sum.restype  = ctypes.POINTER(Tensor)

#tensor * view(tensor *t0, tensor *dim_data)
lib.view.argtypes = [ctypes.POINTER(Tensor), ctypes.POINTER(Tensor)]
lib.view.restype  = ctypes.POINTER(Tensor)

#tensor * expand(tensor *t0, tensor *dim_data)
lib.expand.argtypes = [ctypes.POINTER(Tensor), ctypes.POINTER(Tensor)]
lib.expand.restype  = ctypes.POINTER(Tensor)

#tensor * permute(tensor *t0, tensor *dim_data)
lib.permute.argtypes = [ctypes.POINTER(Tensor), ctypes.POINTER(Tensor)]
lib.permute.restype  = ctypes.POINTER(Tensor)

#print

class LemurTensor:
    __slots__ = ("_ptr", "_parents")
    #TODO make note that _parents is needed so that when doing w = w.relu() or similar, GC doesnt mess us up

    def __init__(self, 
             shape: Optional[list[int]] = None, 
             requires_grad: Optional[bool] = False, 
             _ptr = None, 
             _parents = None):
        
        if _ptr is not None:
            self._ptr = _ptr
            self._parents = _parents or ()
        else:
            if shape is None:
                shape = (1,)
            c_shape = (ctypes.c_size_t * 5)(*([1]*5))
            for i, dim in enumerate(shape):
                c_shape[i] = dim

            t_ptr = lib.empty_tensor(c_shape, requires_grad)
            if not t_ptr:
                raise RuntimeError("empty_tensor returned NULL.")
            self._ptr = t_ptr

    def __del__(self):
        if getattr(self, "_ptr", None) is not None:
            lib.free_tensor(self._ptr)
            self._ptr = None

    def backward(self):
        lib.backwards(self._ptr)

    def relu(self):
        c_result = lib.relu(self._ptr, False)
        return LemurTensor(_ptr=c_result, _parents=(self,))

    def __add__(self, other):
        if not isinstance(other, LemurTensor):
            raise TypeError("Can't add LemurTensor with non-LemurTensor.")
        c_result = lib.add(self._ptr, other._ptr, False)
        return LemurTensor(_ptr=c_result, _parents=(self, other))

    def __mul__(self, other):
        if not isinstance(other, LemurTensor):
            raise TypeError("Can't multiply LemurTensor with non-LemurTensor.")
        c_result = lib.mul(self._ptr, other._ptr, False)
        return LemurTensor(_ptr=c_result, _parents=(self, other))
    
    def sum(self, other):
        if not isinstance(other, LemurTensor):
            raise TypeError("Can't sum LemurTensor with non-LemurTensor dim.")
        c_result = lib.sum(self._ptr, other._ptr, False)
        return LemurTensor(_ptr=c_result, _parents=(self,))
    
    def view(self, other):
        if not isinstance(other, LemurTensor):
            raise TypeError("Can't view LemurTensor with non-LemurTensor.")
        c_result = lib.view(self._ptr, other._ptr)
        return LemurTensor(_ptr=c_result, _parents=(self,))
    
    def expand(self, other):
        if not isinstance(other, LemurTensor):
            raise TypeError("Can't expand LemurTensor with non-LemurTensor.")
        c_result = lib.expand(self._ptr, other._ptr)
        return LemurTensor(_ptr=c_result, _parents=(self,))
    
    def permute(self, other):
        if not isinstance(other, LemurTensor):
            raise TypeError("Can't permute LemurTensor with non-LemurTensor.")
        print("call")
        c_result = lib.permute(self._ptr, other._ptr)
        return LemurTensor(_ptr=c_result, _parents=(self,))
    
    def __repr__(self):
        return reprutils._tensor_repr(self._ptr)



def tensor(data, shape = None, requires_grad=False):
    """
    Creates a new LemurTensor with shape=(1,1,1,1, len(data)).
    """
    
    _shape = shape
    if not shape:
        _shape = (1, 1, 1, 1, len(data))
    t = LemurTensor(shape=_shape, requires_grad=requires_grad)

    k_ptr = t._ptr.contents.k
    c_arr = k_ptr.contents.array 

    for i, val in enumerate(data):
        c_arr[i] = val 

    return t