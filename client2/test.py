
class X:
    def is_admin(self):
        return True
import dill
# def is_admin(self):
#     return True

import pickle
import binascii

thing = X()
dill.dump(thing, open('pickles-r-us', 'wb'))

with open('pickles-r-us', 'rb') as f:
    a = f.read()
    c = binascii.hexlify(a)
    print(c)
    print(pickle.loads(a))