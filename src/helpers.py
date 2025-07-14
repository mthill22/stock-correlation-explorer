import pickle
import os

def pickle_save(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        pickle.dump(data, f)

def pickle_load(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)