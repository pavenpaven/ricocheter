# im going to define some globals, i know ii but my code is too messed up.
globals = []

conf_file = open("conf.txt", "r")
conf=conf_file.read()
conf_file.close()

conf = conf.split("\n") #oops
for i in conf:
    x = i.split(" = ") #yes i know but i seriusly cant have not spaces
    globals.append(x) #note that i never int so they can be strings

def conf_search(name): #just gets the data asosiated with a name in the conf_global list
    for i in globals:
        if name == i[0]:
            return i[1]
    a # this is stupid i want to crash the program and forgot how to throw an exeption or something no weit not that 
