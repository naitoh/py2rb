
for (x,y,z) in [(x,y,z) for x in range(0,3) for y in range(0,4) for z in range(0,5)]:
    if x < y < z: 
        print(x,y,z,"x<y<z")


