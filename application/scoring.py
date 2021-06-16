import json
import math
import numpy as np

def load_best(bgn, end):
    with open(f"{folder}/best.json") as json_file:
        data = json.load(json_file)

    arr = np.array(data)
    return arr[bgn:end + 1]


def load_test(num, bgn):
    with open(f"{folder}/{num}.json") as json_file:
        data = json.load(json_file)

    arr = np.array(data)
    return arr[bgn:]

def oks_score():
    og = best_pts.copy()
    en = test_pts.copy()
    scores = []

    for i, og_frame in enumerate(og):
        try:
            en_frame = en[i]
        except IndexError:
            break

        #Translate pelvis (6) to (0,0)
        og_trans = [[x - og_frame[6][0],y - og_frame[6][1]] for [x,y] in og_frame]
        en_trans = [[x - en_frame[6][0],y - en_frame[6][1]] for [x,y] in en_frame]

        #Find scale using pelvis (6) and head (9)
        og_dist = np.hypot(og_trans[9][0], og_trans[9][1])
        en_dist = np.hypot(en_trans[9][0], en_trans[9][1])

        scale_factor = og_dist / en_dist
        en_scaled = [[x * scale_factor, y * scale_factor] for [x,y] in og_trans]

        #Prepare variables for en_scaled
        xs, ys = map(list, zip(*en_scaled))
        area = (max(xs) - min(xs)) * (max(ys) - min(ys))
        k = [0.01, 0.05, 0.05, 0.05, 0.05, 0.01, 0.05, 0.04, 0.04, 0.01, 0.8, 0.04, 0.04, 0.04, 0.04, 0.01]
        #k = 0.05

        #Apply OKS between og_trans and en_scaled
        oks = 0
        total = 0
        for j, og_pnt in enumerate(og_trans):
            en_pnt = en_scaled[j]
            dist = np.hypot((og_pnt[0] - en_pnt[0]),(og_pnt[1] - en_pnt[1]))
            oks += math.exp(-((dist ** 2)/(2 * area ** 2 * k[j] ** 2)))
            total += 1
        
        scores.append(oks/total)

    return scores


def cos_score():
    og = best_pts.copy()
    en = test_pts.copy()
    scores = []
    limbs = [(0,1),(1,2),(2,6),(5,4),(4,3),(3,6),(6,7),(7,8),(8,9),(10,11),(11,12),(12,7),(15,12),(14,13),(13,7)]

    for i, og_frame in enumerate(og):
        try:
            en_frame = en[i]
        except IndexError:
            break

        score = 0
        for (p1, p2) in limbs:
            [x1,y1] = en_frame[p1]
            [x2,y2] = en_frame[p2]
            [x3,y3] = og_frame[p1]
            [x4,y4] = og_frame[p2]

            cos_score = ((x2 - x1) * (x4 - x3) + (y2 - y1) * (y4 - y3)) / (np.hypot(x2 - x1, y2 - y1) * np.hypot(x4 - x3, y4 - y3))

            if cos_score > 0.5:
                score += cos_score

        scores.append(score / len(limbs))

    return scores



#f4.5 
# folder = "f_4.5_som"
# best_pts = load_best(14,58)
# test_frames = [0, 5, 5, 5, 4, 6, 7, 10, 3]

#b3.5
# folder = "b_3.5_som"
# best_pts = load_best(1,43)
# test_frames = [9, 7, 5, 20, 7, 7, 9, 12, 7, 10]

#i3.5 
# folder = "i_3.5_som"
# best_pts = load_best(7,49)
# test_frames = [21, 7, 17, 2, 6, 5, 13, 8, 15, 8]

#r3.5 
folder = "r_3.5_som"
best_pts = load_best(4,49)
test_frames = [10, 1, 14, 4, 0, 1, 9, 13, 14, 12, 19, 0]


for i in range(len(test_frames)):
    test_pts = load_test(i+1,test_frames[i])
    # oks_scores = oks_score()
    # print(sum(oks_scores)/len(oks_scores))

    cos_scores = cos_score()
    print(sum(cos_scores)/len(cos_scores))