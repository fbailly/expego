import numpy as np
from IPython import embed
mes_bplume = np.array([-3.6004087458,3.3680321189,1.5372971483])*100
mes_brouge = np.array([-3.6178109599,3.9675009516,1.5314543185])*100
mes_bvide = np.array([-3.6363492807,4.5560661391,1.5339595827])*100
val_brouge = np.array([-3.6420,5.0994-2.44/2,2.1465-1.22/2])*100
val_bvide = val_brouge + np.array([0,61,0])
val_bplume = val_brouge - np.array([0,61,0])
embed()
