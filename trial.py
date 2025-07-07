import pickle
f = open("hai", "wb")
a = "ipsum lorem"
pickle.dump(a,f)
f.close()
f = open("hai", "rb")
print(pickle.load(f))