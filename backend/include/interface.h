#ifndef interface_H
#define interface_H

#include "tensor.h"

//helper macros

#define SINGLE_INPUT_FUNC_DEF(name)     \
    tensor * name(tensor *t0, bool retain_grad)

#define DOUBLE_INPUT_FUNC_DEF(name)      \
    tensor * name(tensor *t0, tensor *t1, bool retain_grad) 


//external functions

#ifdef __cplusplus
extern "C" {
#endif

void backward(tensor * t);

void free_tensor(tensor *t);

tensor * empty_tensor(size_t shape[5], bool retain_grad);
void memset_kernel_tensor(kernel_tensor * k, lemur_float val);
bool is_contiguous(kernel_tensor *k);
void init_random_uniform_kernel_tensor(kernel_tensor * k, lemur_float min, lemur_float max);
void init_random_normal_kernel_tensor(kernel_tensor * k, lemur_float mean, lemur_float std);
void init_seed(unsigned int seed);



extern char* op_map[TOTAL_OPS];
char* get_op_name(int op_id);

//binary ops
DOUBLE_INPUT_FUNC_DEF(add);
DOUBLE_INPUT_FUNC_DEF(sub);
DOUBLE_INPUT_FUNC_DEF(mul);
DOUBLE_INPUT_FUNC_DEF(division);

//unary ops
SINGLE_INPUT_FUNC_DEF(exponential);
DOUBLE_INPUT_FUNC_DEF(power); 
SINGLE_INPUT_FUNC_DEF(relu);
SINGLE_INPUT_FUNC_DEF(sigmoid);
SINGLE_INPUT_FUNC_DEF(logarithm);
SINGLE_INPUT_FUNC_DEF(neg);
SINGLE_INPUT_FUNC_DEF(square_root);
SINGLE_INPUT_FUNC_DEF(absolute);
SINGLE_INPUT_FUNC_DEF(sign);
SINGLE_INPUT_FUNC_DEF(reciprocal);

//reduce ops
DOUBLE_INPUT_FUNC_DEF(sum);

//shape ops
DOUBLE_INPUT_FUNC_DEF(view);
DOUBLE_INPUT_FUNC_DEF(expand);
DOUBLE_INPUT_FUNC_DEF(permute);

//matmul

//compiler
void compile(tensor *root_node);

#ifdef __cplusplus
}
#endif

#endif 
