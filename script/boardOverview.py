# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 21:57:40 2018

@author: jackycai

list the growth ratio of all HY boards
"""

import os
import sys
import getopt
import pandas as pd
import numpy as np

def usage():
	"print usage"
	print("boardOverview.py -d date --all")
	return
		
try:
	opts, args = getopt.getopt(sys.argv[1:], "hd:", ["all"])
except getopt.GetoptError: 
	usage()
	sys.exit()

#variable has scope, we need to define them here
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


baseDir = "Z:/output/quota/"
boardCategory = "z:/output/board/stockBoard.txt"

board_df = pd.read_csv(boardCategory, encoding="gbk", names=["code","name","hy","area"], usecols=["code","hy","area"], dtype={"code":str}, skiprows=1)

if len(targetDate) == 8:
	dateDir=[targetDate+ ".txt"]
elif allDate==1:
	#print hq data in all dates
	dateDir = os.listdir(baseDir)
else:
	#default, only print the latest quota data
	dateList = os.listdir(baseDir)
	dateList.sort(reverse=True)
	dateDir=[dateList[0]]
	
for quotaDateFile in dateDir:
	dateString = quotaDateFile[:8]
	quotaFilePath = baseDir + quotaDateFile
	if quotaDateFile[-3:]!="txt" or (not os.path.exists(quotaFilePath)):
		continue
	print(quotaFilePath)

	df = pd.read_csv(quotaFilePath, encoding="gbk", names=["name","code","ST","market","zgb","ltgb","yclose","top","bottom","open","high","low","close","vol","amount","buy1p","buy1v","sell1p","sell1v","buy2p","buy2v","sell2p","sell2v","buy3p","buy3v","sell3p","sell3v","buy4p","buy4v","sell4p","sell4v","buy5p","buy5v","sell5p","sell5v"], usecols=["code", "zgb","ltgb","yclose","close", "vol","amount"], dtype={"code":str}, header=None)	
	df = df.join(board_df.set_index("code"), on="code")
	print(df.info())

	df["ratio"] = round((df["close"] - df["yclose"])/df["yclose"] * 100, 2)
	
	df["ltsz"]= df["close"] * df["ltgb"]

	df["weightedRatio"]= df["ratio"] * df["ltgb"]
	print()
	
		
	pivot_df = pd.pivot_table(df, index=["hy"], values=["code", "ratio","weightedRatio","ltgb", "ltsz"], aggfunc={"ratio":np.mean,"weightedRatio":np.sum,"ltgb":np.sum, "code":len, "ltsz":sum})
	print(pivot_df.info())
	print(pivot_df.columns)
	pivot_df["weightedRatio_board"] = pivot_df["weightedRatio"] / pivot_df["ltgb"]
	pivot_df["ltsz_ratio"] = pivot_df["ltsz"] / pivot_df["ltsz"].sum() * 100
	
	pivot_df=pivot_df.sort_values(by="weightedRatio_board")
	print(pivot_df.info())
	print("行业\t\t股票数\t涨幅\t加权涨幅\t板块权重")
	for rowIndex, row in pivot_df.iterrows():
		print("{:10s}\t{:0.0f}\t{:0.2f}\t{:0.2f}\t\t{:0.2f}".format(row.name, row["code"], row["ratio"], row["weightedRatio_board"], row["ltsz_ratio"]))
		
