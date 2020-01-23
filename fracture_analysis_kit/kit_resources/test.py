# import glob
# from pathlib import Path
# import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# fig, axes = plt.subplots(5, 5)
#
# # getting length range stuff
# for idx, row in trace_data.uniframe.iterrows():
#     l = 10
#     print(f'more than {l}')
#     print(row.code)
#     print(row.uni_ld.lineframe_main.length.loc[row.uni_ld.lineframe_main.length > l].count())

df = pd.DataFrame()

df.loc[0, 'asd'] = 'idx'

print(df)