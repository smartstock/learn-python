# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 17:02:29 2018

@author: Jackycai

list all the stocks which price has been touched to top/bottom
"""

import os
import sys, getopt
import pandas as pd


def displayZDT(zdtFlag, been=False):
	"涨跌停标志位 转换为 中文"
	explainCN = ""
	if zdtFlag==1:
		explainCN = "涨停"
	elif zdtFlag==-1:
		explainCN = "跌停"
	if been :
		explainCN = explainCN + "过"
	return explainCN

def displayPower(powerFlag):
	"封死涨跌停标志位 转换为 中文"
	if powerFlag == 0:
		return "未封死"
	else:
		return ""

def usage():
	"print usage"
	print("ZTDTAnalyse.py -d date --nodt --nozt --all")
	return
		
try:
	opts, args = getopt.getopt(sys.argv[1:], "hd:", ["nodt", "nozt", "all", "ztg", "dtg"])
except getopt.GetoptError: 
	usage()
	sys.exit()

#variable has scope, we need to define them here
targetDate=""
nodt=0
nozt=0
allDate=0
ztg=0
dtg=0

for op, value in opts:
	if op == "-d":
		targetDate = value
	elif op == "--nodt":
		nodt=1
	elif op == "--nozt":
		nozt=1
	elif op == "--all":
		allDate=1
	elif op == "--ztg":
		ztg=1
	elif op == "--dtg":
		dtg=1
	elif op == "-h":
		usage()
		sys.exit()


baseDir = "Z:/output/quota/"

if len(targetDate) == 8:
	dateDir=[targetDate+ ".txt"]
elif allDate==1:
	#print zdt data in all dates
	dateDir = os.listdir(baseDir)
else:
	#default, only print the latest zdt data
	dateList = os.listdir(baseDir)
	dateList.sort(reverse=True)
	dateDir=[dateList[0]]


for quotaDateFile in dateDir:
	ztList = []
	ztgList =[] #had been zt, but not zt at close
	dtList = []
	dtgList =[]
	dateString = quotaDateFile[:8]
	quotaFilePath = baseDir + quotaDateFile
	print(quotaFilePath)
	df = pd.read_csv(quotaFilePath, encoding="gbk", names=["name","code","ST","market","zgb","ltgb","yclose","top","bottom","open","high","low","close","vol","amount","buy1p","buy1v","sell1p","sell1v","buy2p","buy2v","sell2p","sell2v","buy3p","buy3v","sell3p","sell3v","buy4p","buy4v","sell4p","sell4v","buy5p","buy5v","sell5p","sell5v"], dtype={"code":str}, header=None)
	
	for row_index,row in df.iterrows():
		ratio = (row["close"] - row["yclose"] )/row["yclose"] * 100		
		powerFlag = 1
		if row["top"] == row["close"]:
			zdtFlag = 1
			if row["sell1p"] > 0:
				powerFlag = 0
			ztList.append({"name":row["name"],"code":row["code"], "ST":row["ST"], "zdtFlag":zdtFlag, "ratio":ratio, "power":powerFlag})
		elif row["bottom"] == row["close"]:
			zdtFlag = -1
			if row["buy1p"] > 0:
				powerFlag = 0
			dtList.append({"name":row["name"],"code":row["code"], "ST":row["ST"],"zdtFlag":zdtFlag, "ratio":ratio, "power":powerFlag})
		if row["top"] == row ["high"] and row["top"] != row["close"]:
			ztgList.append({"name":row["name"],"code":row["code"], "ST":row["ST"], "zdtFlag":1, "ratio":ratio, "power":0})
		elif row["bottom"] == row ["low"] and row["bottom"] != row["close"]:
			dtgList.append({"name":row["name"],"code":row["code"], "ST":row["ST"], "zdtFlag":-1, "ratio":ratio, "power":0})

	if nozt != 1:
		resultZTPD = pd.DataFrame(ztList, columns =["name","code", "ST", "zdtFlag", "ratio", "power"])
		#use df.shape[0] to get the row numbers
		print("%s 涨停股票 %d 家, 其中ST股票 %d 家" % (dateString, resultZTPD.shape[0], resultZTPD[resultZTPD.ST==1].shape[0]))
		for row_index,row in resultZTPD.sort_values(by="ratio").iterrows():
			print("%s\t%s\t%s\t(%.2f%%)\t%s" % (row["name"].ljust(6), row["code"],displayZDT(row["zdtFlag"]),row["ratio"], displayPower(row["power"])))
		print()
		
	if ztg == 1:
		resultZTGPD = pd.DataFrame(ztgList, columns =["name","code", "ST", "zdtFlag", "ratio", "power"])
		print("%s 涨停过股票 %d 家, 其中ST股票 %d 家" % (dateString, resultZTGPD.shape[0], resultZTGPD[resultZTGPD.ST==1].shape[0]))
		for row_index,row in resultZTGPD.sort_values(by="ratio").iterrows():
			print("%s\t%s\t%s\t(%.2f%%)" % (row["name"].ljust(6), row["code"],displayZDT(row["zdtFlag"], True),row["ratio"]))
		print()
	
	if nodt != 1:
		resultDTPD = pd.DataFrame(dtList, columns =["name","code", "ST","zdtFlag", "ratio", "power"])
		print("%s 跌停股票 %d 家, 其中ST股票 %d 家" % (dateString, resultDTPD.shape[0], resultDTPD[resultDTPD.ST==1].shape[0]))
		for row_index,row in resultDTPD.sort_values(by="ratio", ascending=False).iterrows():
			print("%s\t%s\t%s\t(%.2f%%)\t%s" % (row["name"].ljust(6), row["code"],displayZDT(row["zdtFlag"]),row["ratio"], displayPower(row["power"])))
		print()
		
	if dtg==1:
		resultDTGPD = pd.DataFrame(dtgList, columns =["name","code", "ST","zdtFlag", "ratio", "power"])
		print("%s 跌停过股票 %d 家, 其中ST股票 %d 家" % (dateString, resultDTGPD.shape[0], resultDTGPD[resultDTGPD.ST==1].shape[0]))
		for row_index,row in resultDTGPD.sort_values(by="ratio", ascending=False).iterrows():
			print("%s\t%s\t%s\t(%.2f%%)" % (row["name"].ljust(6), row["code"],displayZDT(row["zdtFlag"], True),row["ratio"] ))
		print()