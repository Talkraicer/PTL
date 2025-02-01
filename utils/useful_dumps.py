# Convert a vType table into a pretty one:
import pandas as pd
from numpy import arange
df = pd.read_pickle(r"C:\PTL\results\output_results\network_simple\DailyTypes\duration_vType.pkl")

av_rates = [round(rate,1) for rate in arange(0.1, 1.0, 0.1)]
rel_cols = [c for c in df.columns if "mean" in c and c[1] in av_rates]

temp_df = pd.DataFrame(df[rel_cols].loc["OneVariableControl_ptl_speed_20_24_60"]).reset_index()
temp_df.columns = ["Demand","av_rate","vType","stam","APTD"]
temp_df.drop(["stam"],inplace=True,axis=1)
temp_df["vType"] = temp_df["vType"].apply(lambda x: x.split("_")[0] if "HD" in x else x)
temp_df = temp_df.groupby(["Demand","av_rate","vType"]).mean().reset_index()

new_df = pd.DataFrame()
for demand in temp_df["Demand"].unique():
    for vType in temp_df["vType"].unique():
        temp = temp_df[(temp_df["Demand"]==demand) & (temp_df["vType"]==vType)]
        temp = temp.set_index("av_rate").drop(["Demand","vType"],axis=1).T
        temp["Demand"] = demand
        temp["vType"] = vType
        new_df = pd.concat([new_df,temp])

new_df["numPass"] = new_df["vType"].apply(lambda x: x.split("_")[1] if "AV" in x else None)
new_df["vType"] = new_df["vType"].apply(lambda x: x.split("_")[0])
new_df = new_df[["Demand","vType","numPass"]+av_rates].reset_index(drop=True)

new_df.to_excel("check.xlsx")