"""
Experiment with cuckoo_filter

pip install scalable-cuckoo-filter

Determine the parameters (capacity, bucket_size) via guide in
https://stackoverflow.com/questions/57555236/how-to-size-a-cuckoo-filter

"""
import math

from random import randrange
from cuckoo.filter import CuckooFilter

capacity = 1000000
error_rate = 0.000001
# Create a classic Cuckoo filter with a fixed capacity of 1000000
# buckets
cuckoo = CuckooFilter(capacity=capacity, error_rate=error_rate)

bucket_size = 6
# Setting the bucket size is optional, the bigger the bucket,
# the more number of items a filter can hold, and the longer
# the fingerprint needs to be to stay at the same error rate
cuckoo = CuckooFilter(capacity=capacity, error_rate=error_rate, bucket_size=bucket_size)

# The fingerprint length is computed using the following formula:
fingerprint_size = int(math.ceil(math.log(1.0 / error_rate, 2) + math.log(2 * bucket_size, 2)))

for _ in range(1, 100000):
    item = str(randrange(1, 1000000000))
    cuckoo.insert(item)

    if cuckoo.contains(item):
        print('{} has been added'.format(item))

    cuckoo.delete(item)

    if not cuckoo.contains(item):
        print('{} has been removed'.format(item))
