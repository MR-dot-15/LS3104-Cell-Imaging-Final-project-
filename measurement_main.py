from PIL import Image, ImageOps
import numpy as np
import os

# accessing some particular folder 
# and reading the images stored
path = os.getcwd() + '\\f_avg_2\\'
files = os.listdir(path)
#files = ["P1.jpg", "P2.jpg", "P3.jpg", "P4.jpg", "P5.jpg", "P6.jpg"]

for fp in files:
    # threshold value, for grayscale -> binary conversion
    # can be altered with hair = -1 (user-input)
    threshold = 125
    # min_dist, width_det to be accessed by hair = -2
    min_dist = 30
    wid_chek = [5, 10]
    while True:
        path_n = path + fp
        img = Image.open(path_n)

        # opening the image, gray-scaling
        # and creating its equivalent np array
        new_img = ImageOps.grayscale(img)
        array = np.array(new_img)
        x, y = array.shape

        # grayscale to binary
        for i in range(x):
            for j in range(y):
                if array[i, j] <= threshold:
                    array[i, j] = 0
                else:
                    array[i, j] = 255
        binary = Image.fromarray(array)

        #----------------------------------------------------
        # all vertical measurements now
        # finding a potential line of symmetry
        vert_line = array[:, round(y/2)]   
        points = []

        for i in range(1, x):
            if vert_line[i] == 0:
                if len(points) == 0:
                    points.append(i)
                    continue
                # try-except as there was overflow error for low-res images
                try:
                    prev, next = vert_line[i-1], vert_line[i+1]
                    # decides the minimum gap between two consecutive "black"
                    if prev + next == 255 and i - points[-1] > min_dist:
                        points.append(i)
                except:
                    continue

        # visually identifying the detected "edges"
        for i in points:
            for j in range(y):
                if points.index(i) == 1:
                    array[i, j] = 255
                else:
                    array[i, j] = 0

        #----------------------------------------------------
        # measuring face width
        # observation: bizygomatic diameter lies at around x/2
        # left + 0, right + 5
        x0, y0 = round(x/2), round(y/2)
        # l_len, r_len hold the distance estimation
        l_len = r_len = 0
        # determines if left/ right end of the face is reached
        left = right = 0

        # role of wid_chek
        # wid_chek[0] = boundary constraint at the left end
        # ...[1] = " for the right end
        # if the value is i, it checks 
        # whether the pixel after i distance is black
        # proceeds, if not 
        while left + right != 2:
            if left != 1:
                if array[x0, y0 - l_len - 1] != 0:
                    l_len += 1
                elif array[x0, y0 - l_len - 1] == 0\
                    and array[x0, y0 - l_len - wid_chek[0]] != 0:
                    l_len += 1
                else:
                    left = 1
            if right != 1:
                if array[x0, y0 + r_len + 1] != 0:
                    r_len += 1
                elif array[x0, y0 + r_len + 1] == 0\
                    and array[x0, y0 + r_len + wid_chek[1]] != 0:
                    r_len += 1
                else:
                    right = 1

        # face ends
        for i in range(x):
            array[i, y0 - l_len] = 0
            array[i, y0 + r_len] = 0

        # saving the image with all the detection marks (/lines)
        new_img = Image.fromarray(array)
        new_img.show()
        new_img.save(path+"f"+fp)

        # the program tracks spots with a colour change (b->w, w->b)
        # the pixel "detected" must be 30 units of distance apart 
        # from the last detected pixel [more flexibility]
        # now the user decides the "detected pixels" which correspond to-
        # hair-line, nasal tip, chin
        hair = int(input("Hair: "))
        # customizing a few parameters (self-explanatory)
        if hair == -1:
            threshold = int(input("New threshold: "))
            continue
        elif hair == -2:
            min_dist = int(input(" Min dist: "))
            temp = input("To detect face width (format: x,y): ")
            wid_chek = [int(i) for i in temp.split(',')]
            continue
        nose = int(input("Nose: "))
        #lips = int(input("Lips"))
        chin = int(input("Chin: "))
        print("----------------\n")

        # estimation of a few parameters, self-explanatory
        width = l_len + r_len + 5
        length = points[chin-1] - points[hair-1]
        hair2nose = points[nose-1] - points[hair-1]
        nose2chin = points[chin-1] - points[nose-1]

        # saving the quantities estimated in a csv
        with open('mes_avg.csv', 'a') as inf:
            inf.write("%s,%f,%f,%f,%f\n"%\
                (fp[:-4],length,width,hair2nose,nose2chin))
            break