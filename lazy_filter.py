import sys

def my_filter(importer, name, fromlist):
    return False

sys.set_lazy_imports_filter(my_filter)
