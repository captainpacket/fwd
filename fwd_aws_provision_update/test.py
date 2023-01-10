with open(creds.txt) as f:
    mylist = f.read().splitlines() 

print(mylist[0])
