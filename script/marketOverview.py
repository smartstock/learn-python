# -*- coding: utf-8 -*-
"""
@author:jackycai

"""

import os
import sys
import getopt
import pandas as pd
import numpy as np

def usage():
	"print usage"
	print("marketOverview.py -d date --all")
	return
		
try:
	opts, args = getopt.getopt(sys.argv[1:], "hd:", ["all"])
except getopt.GetoptError: 
	usage()
	sys.exit()

targetDate=""
allDate=0

for op, value in opts:
	if op == "-d":
		targetDate = value
	elif op == "--all":
		allDate=1
	elif op == "-h":
		usage()
		sys.exit()

#directory of where quota data located
#TODO: update to your directory in your computer
baseDir = "Z:/output/quota/"

if len(targetDate) == 8:
	dateDir=[targetDate+ ".txt"]
elif allDate==1:
	#print all dates
	dateDir = os.listdir(baseDir)
else:
	#default, only print the latest data
	dateList = os.listdir(baseDir)
	dateList.sort(reverse=True)
	dateDir=[dateList[0]]
	
for quotaDateFile in dateDir:
	dateString = quotaDateFile[:8]
	quotaFilePath = baseDir + quotaDateFile
	if quotaDateFile[-3:]!="txt" or (not os.path.exists(quotaFilePath)):
		continue
	print(quotaFilePath)

	df = pd.read_csv(quotaFilePath, encoding="gbk", names=["name","code","ST","market","zgb","ltgb","yclose","top","bottom","open","high","low","close","vol","amount","buy1p","buy1v","sell1p","sell1v","buy2p","buy2v","sell2p","sell2v","buy3p","buy3v","sell3p","sell3v","buy4p","buy4v","sell4p","sell4v","buy5p","buy5v","sell5p","sell5v"], dtype={"code":str}, header=None)
	
	df["ratio"] = round((df["close"] - df["yclose"])/df["yclose"] * 100, 2)
	print("算数平均涨幅 {:.2f}%".format(round(df["ratio"].mean(),2)))
	
	df["weightedRatio"]= df["ratio"] * df["ltgb"]
	print("流通股本加权平均涨幅 {:.2f}%".format(round(df["weightedRatio"].sum()/df["ltgb"].sum(),2)))
	
	print("算数平均股价 {:.2f}".format(round(df["close"].mean(),2)))
	
	df["weightedClose"]= df["close"] * df["ltgb"]
	print("流通股本加权平均股价 {:.2f}".format(round(df["weightedClose"].sum()/df["ltgb"].sum(),2)))
	print()
	
	df["ZTFlag"] =  df["top"] == df["close"]
	df["STZTFlag"] =  (df["top"] == df["close"]) & (df["ST"] == 1)
	df["DTFlag"] =  df["bottom"] == df["close"]
	df["STDTFlag"] =  (df["bottom"] == df["close"]) & (df["ST"] == 1)
	df["up"] =  df["ratio"] > 0
	df["down"] =  df["ratio"] < 0
	df["draw"] =  df["ratio"] == 0
	
	#temp take N-stock as normal stock temporary
	df.loc[(df.ST==2), "ST"] = 0
	

	df["market"] = df["market"].astype("category")
	df["market"].cat.rename_categories(["深圳", "上海"], inplace=True)
	pivot_df = pd.pivot_table(df, index=["market"], values=["code", "up", "down", "draw", "ZTFlag","STZTFlag", "DTFlag", "STDTFlag"], aggfunc=np.count_nonzero, margins=True, margins_name="总计")
	pivot_df.rename(columns={"code":"交易股票数", "up":"涨", "down":"跌", "draw":"平","ZTFlag":"涨停", "DTFlag":"跌停", "STZTFlag":"ST", "STDTFlag":"ST"  }, inplace=True)

	pd.set_option('display.precision', 0)
	print(pivot_df.iloc[:, [3,2,0,1,7,5,6,4]])
	print()