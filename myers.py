import copy
from tqdm import tqdm

INS = b'+'
DEL = b'-'
EQL = b'='
SEP = b'_'

def string_to_bytearray(string, symbols):
  byte_str = bytes(string, encoding='utf-8')
  res = [byte_str[i:i+1] for i in range(0, len(byte_str), 1)]
  res.append(b'_')
  res += symbols
  return res

def bytearray_to_string(arr):
  string = (b''.join(arr)).decode(encoding='utf-8')
  return string

# Считывание файла в массив байтов

def file_to_buff(filename):
  buff = []
  with open(filename, "rb") as f:
    byte = f.read(1)
    buff.append(byte)
    while byte:
        byte = f.read(1)
        buff.append(byte)
  return buff

def buff_to_file(filename, buff):
  newFile = open(filename, "wb")
  newFile.write(bytearray(b''.join(buff)))

# Реализация алгоритма поиска различий в файлах

def myers_diff(first, second):

  first_len, second_len = len(first), len(second)
  _max = first_len + second_len
  v = {1 : 0}
  trace = {1 : []}

  for d in tqdm(range(0, _max + 1)):
    for k in range(-d, d + 1, 2):
      
      downwards = k == -d or (k != d and v[k - 1] < v[k + 1])
      if downwards:
        x = v[k + 1]
        new_trace = copy.copy(trace[k + 1])
      else:
        x = v[k - 1] + 1
        new_trace = copy.copy(trace[k - 1])
    
      y = x - k

      if 1 <= y <= second_len and downwards:
        new_trace.append(('insert', second[y - 1]))
      elif 1 <= x <= first_len:
        new_trace.append(('delete', first[x - 1], x - 1))

      while x < first_len and y < second_len and first[x] == second[y]:
        x, y = x + 1, y + 1
        new_trace.append(('keep', first[x - 1], x - 1))
      
      v[k] = x
      trace[k] = new_trace

      if x >= first_len and y >= second_len:
        return new_trace

# Получение различий (содержит строки и первого и второго файла с пометками добавить / удалить)

def get_diff_file(first, second, diff_filename):
  first = file_to_buff(first)
  second = file_to_buff(second)
  res = []
  diff = myers_diff(first, second)
  for action in diff:
    if (action[0] == 'insert'):
      res.append(INS)
      res.append(action[1])
    if (action[0] == 'delete'):
      res.append(DEL)
      res.append(action[1])
    if (action[0] == 'keep'):
      res.append(EQL)
      res.append(action[1])
  buff_to_file(diff_filename, res[:-2]) 

# Получение различий (содержит только изменения)

def get_small_diff_file(first, second, diff_filename):
  first = file_to_buff(first)
  print(first)
  second = file_to_buff(second)
  indices = []
  operations = []
  symbols = []
  last_keep = -1
  diff = myers_diff(first, second)
  print(diff)
  for i in range(len(diff) - 1, -1, -1):
    print(i, diff[i])
    action = diff[i]
    if (action[0] == 'insert'):
      operations.append(':'.join(['+', str(last_keep)]))
      symbols.append(action[1])
    if (action[0] == 'delete'):
      operations.append(':'.join(['-', str(action[2])]))
    if (action[0] == 'keep'):
      last_keep = action[2]
  buff_to_file(diff_filename, string_to_bytearray(','.join(operations[::-1]), symbols[::-1])) 

# Патчинг из файла, полученного объемным способом

def patch_file_with_diff(diff_filename, result_filename):
  first = file_to_buff(filename)
  patch = file_to_buff(diff_filename)[:-1]
  res = []
  print('patch', patch)
  for i in range(0, len(patch), 2):
    print(i)
    if patch[i] != DEL:
      res.append(patch[i + 1])
  buff_to_file(result_filename, res)

# Патчинг из файла с изменениями

def patch_file_with_small_diff(filename, diff_filename, result_filename):
  first = file_to_buff(filename)
  patch = file_to_buff(diff_filename)[:-1]
  sep_index = patch.index(b'_')
  byte_indices = patch[:sep_index]
  symbols = patch[sep_index + 1:]

  indices_str = bytearray_to_string(byte_indices)
  op_ind = indices_str.split(',')
  sym_idx = 0

  indices = []
  operations = []

  for elem in op_ind:
    [operation, index] = elem.split(':')
    operations.append(operation)
    indices.append(int(index))

  print(operations, indices, symbols)
  op_idx = 0

  res = []

  for i in range(len(first)):
    deleted = False
    while op_idx < len(indices) and indices[op_idx] <= i:
      if (operations[op_idx] == '-'):
        op_idx += 1
        deleted = True
      elif (operations[op_idx] == '+'):
        res.append(symbols[sym_idx])
        op_idx += 1
        sym_idx += 1
    if not deleted:
      res.append(first[i])
  while (op_idx < len(operations)):
    if (operations[op_idx] == '-'):
        op_idx += 1
    elif (operations[op_idx] == '+'):
      res.append(symbols[sym_idx])
      op_idx += 1
      sym_idx += 1
  buff_to_file(result_filename, res)
