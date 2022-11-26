"""
Experiment with cuckoo_filter
pickling

pip install scalable-cuckoo-filter
"""
import pickle
from cuckoo.filter import CuckooFilter

capacity = 1000000
error_rate = 0.000001

bucket_size = 6
cuckoo = CuckooFilter(capacity=capacity, error_rate=error_rate, bucket_size=bucket_size)

cuckoo.insert('apple')

assert cuckoo.contains('apple')
print('Succesfully created a cuckoo filter')

with open('cuckoo.pickle', 'wb') as handle:
    pickle.dump(cuckoo, handle, protocol=pickle.HIGHEST_PROTOCOL)
print('Succesfully save a cuckoo filter as pickle')


with open('cuckoo.pickle', 'rb') as handle:
    loaded_cuckoo = pickle.load(handle)


assert loaded_cuckoo.contains('apple')
print('Succesfully loaded a cuckoo filter from pickle')
