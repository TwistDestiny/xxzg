import os
import sys
import pickle
import shutil
join = os.path.join


sample_root = r"D:\典型样本"
out_root = r"D:\ddd"
name_dict = dict()
for name in os.listdir(sample_root):
    size = os.path.getsize(join(sample_root,name))
    name_dict[name] = size
# print(len(name_dict))
# exit(1)
ddd = []
rrrr = [r"D:\images\2020-11-"+str(i) for i in range(28,31)]
# rrrr = []
rrrr.extend([r"D:\images\2020-12-0"+str(i) for i in range(1,10)])

# for root, dirs, files in os.walk(r"D:\images", topdown=False):
    # print(root,dirs,files)
for rrr in rrrr:
    for rr in os.listdir(rrr):
        rr = join(rrr,rr)
        # print(rr)
        # for r in os.listdir(rr):
        #     r = join(rr,r)
        r = rr
        root = join(r,"light")
        if not os.path.exists(root):
            break
        for file in os.listdir(root):
            if file in name_dict and abs(name_dict[file] - os.path.getsize(join(root,file)))<40:
            # print(join(root,file))
                fff = join(root,file)
                ddd.append(fff)
                shutil.copy(fff.replace("light","dark"),join(out_root,file))
                # print(ddd[-1])
print(len(ddd))
print(ddd)
pickle.dumps(ddd,"tmp.pkl")