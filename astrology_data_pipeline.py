## cd '/Users/wpettengill/Desktop/willpettengill.github.io/ai_astrology'
from __future__ import print_function
import gspread
#from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import re
import hashlib
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

answerMapping={
'agree':1, 'disagree':0,
'true':1, 'false':0}

SCOPE = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
SECRETS_FILE = "ML Horoscope-57bf7abc958a.json"
SPREADSHEET = "Machine Learning Horoscope (Responses)"



def user_content(df, udf):
	for i in range(len(udf)):
		x = Dog(udf.birthdate[i], udf.birthtime[i], '02461')
		

def answer_map(x):
	if type(x)==int:
		return x
	elif answerMapping.get(x.lower()) is not None:
		return answerMapping.get(x.lower())
	else:
		return x.lower()

def zip_normalize(x):
	if len(x) == 4:
		x = '0'+ x
	else:
		pass	
	return x


def ping():
	print('running ping')
	ldf = pd.read_csv('users.csv')
	ldf['timestamp']=pd.to_datetime(ldf['timestamp'])
	df, udf, ww, categoricals = transform(SCOPE, SECRETS_FILE, SPREADSHEET)
	if len(udf)==len(ldf):
		return False 
	else:
		return True 

def transform(SCOPE, SECRETS_FILE, SPREADSHEET):
	print('running transform')
	json_key_filename='ml-horoscope-0b2e20e90e59.json'
	credentials = Credentials.from_service_account_file(json_key_filename, scopes=SCOPE)
	service = build('sheets', 'v4', credentials=credentials)
	gc = gspread.authorize(credentials)
	workbook = gc.open(SPREADSHEET)
	sheet = workbook.sheet1
	data = pd.DataFrame.from_records(sheet.get_all_records())
	column_map = {k:re.sub(r'[^\w\s]','',k.lower().replace(' ','')) for k in data.columns.tolist()}
	data = data.rename(columns=column_map)
	data['emd5'] = data['emailaddress'].map(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest())
	data['birthplacezipcode'] = data['birthplacezipcode'].astype(str)
	data['birthplacezipcode'] = data['birthplacezipcode'].map(lambda x: zip_normalize(x))
	data = data.set_index('emd5')
	user_data = ['birthdate', 'birthtime', 'birthplacezipcode', 'timestamp', 'emailaddress']
	udf = data[user_data]
	df = data[[i for i in data.columns.tolist() if i not in user_data]]
	df = df.applymap(lambda x: answer_map(x))
	categoricals = {k.name: list(v) for k, v in df.columns.to_series().groupby(df.dtypes).groups.items()}
	w = workbook.get_worksheet(2) #occult
	ww = pd.DataFrame.from_records(w.get_all_records(), index='Quality').reset_index()
	
	return df, udf, ww, categoricals

def write(df, udf, ww, categoricals):
	print('running adp write')
	with open('categoricals.json', 'w') as fp:
	    json.dump(categoricals, fp)
	df.to_csv('survey.csv')
	udf.to_csv('users.csv')
	ww.to_csv('sun_qualities.csv')
	
def main():
	print('running main')
	df, udf, ww, categoricals = transform(SCOPE, SECRETS_FILE, SPREADSHEET)
	write(df, udf, ww, categoricals)

if __name__ == '__main__':
	
	main()
		
	

