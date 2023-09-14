import pandas as pd
import random
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from datetime import datetime
from datetime import date as dt 
from uszipcode import SearchEngine
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
import json
import argparse
#from pyzipcode import ZipCodeDatabase

class Stars:

	def __init__(self, bdate, btime, bplacezip):		
		self.planet_fields={}
		self.bdate=bdate
		self.btime=btime
		self.bplacezip=bplacezip
		self.date = Datetime(str(self.bdate), str(self.btime),'+05:00')
		self.get_birthplace(bplacezip)
		self.pull_chart(bdate, self.btime)
		self.sun_qualities = pd.read_csv('sun_qualities.csv').drop(['Unnamed: 0'], axis=1)
		self.house_qualities = json.load(open('house_qualities.json'))
		self.sign_qualities = json.load(open('sign_qualities.json'))
		self.planet_qualities = json.load(open('planet_qualities.json'))
		self.p = {
		'sun' : {**self.generate_planet_data(self.chart.getObject(const.SUN)), 'planet_governs': self.planet_qualities.get('sun')},
		'moon' : {**self.generate_planet_data(self.chart.getObject(const.MOON)), 'planet_governs':self.planet_qualities.get('moon')},
		'mercury' : {**self.generate_planet_data(self.chart.getObject(const.MERCURY)), 'planet_governs':self.planet_qualities.get('mercury')},
		'venus' : {**self.generate_planet_data(self.chart.getObject(const.VENUS)), 'planet_governs':self.planet_qualities.get('venus')},
		'mars' : {**self.generate_planet_data(self.chart.getObject(const.MARS)), 'planet_governs':self.planet_qualities.get('mars')},
		'jupiter' : {**self.generate_planet_data(self.chart.getObject(const.JUPITER)), 'planet_governs':self.planet_qualities.get('jupiter')},
		'saturn' : {**self.generate_planet_data(self.chart.getObject(const.SATURN)), 'planet_governs':self.planet_qualities.get('saturn')},
		'neptune' : {**self.generate_planet_data(self.chart.getObject(const.NEPTUNE)), 'planet_governs':self.planet_qualities.get('neptune')},
		'pluto' : {**self.generate_planet_data(self.chart.getObject(const.PLUTO)), 'planet_governs':self.planet_qualities.get('pluto')},
		'ascendant' : {**self.generate_planet_data(self.chart.get(const.ASC)), 'planet_governs':self.planet_qualities.get('asc')},
		'chiron' : {**self.generate_planet_data(self.chart.getObject(const.CHIRON)), 'planet_governs':self.planet_qualities.get('chiron')},
		'north_node' : {**self.generate_planet_data(self.chart.getObject(const.NORTH_NODE)), 'planet_governs':self.planet_qualities.get('north_node')},
		'south_node' : {**self.generate_planet_data(self.chart.getObject(const.SOUTH_NODE)), 'planet_governs':self.planet_qualities.get('south_node')},
		'syzygy' : {**self.generate_planet_data(self.chart.getObject(const.SYZYGY)), 'planet_governs':self.planet_qualities.get('syzygy')},
		'pars_fortuna' : {**self.generate_planet_data(self.chart.getObject(const.PARS_FORTUNA)), 'planet_governs':self.planet_qualities.get('pars_fortuna')},
		'house1' : {**self.generate_planet_data(self.chart.get(const.HOUSE1)), 'planet_governs':self.house_qualities.get('house1')},
		'house2' : {**self.generate_planet_data(self.chart.get(const.HOUSE2)), 'planet_governs':self.house_qualities.get('house2')},
		'house3' : {**self.generate_planet_data(self.chart.get(const.HOUSE3)), 'planet_governs':self.house_qualities.get('house3')},
		'house4' : {**self.generate_planet_data(self.chart.get(const.HOUSE4)), 'planet_governs':self.house_qualities.get('house4')},
		'house5' : {**self.generate_planet_data(self.chart.get(const.HOUSE5)), 'planet_governs':self.house_qualities.get('house5')},
		'house6' : {**self.generate_planet_data(self.chart.get(const.HOUSE6)), 'planet_governs':self.house_qualities.get('house6')},
		'house7' : {**self.generate_planet_data(self.chart.get(const.HOUSE7)), 'planet_governs':self.house_qualities.get('house7')},
		'house8' : {**self.generate_planet_data(self.chart.get(const.HOUSE8)), 'planet_governs':self.house_qualities.get('house8')},
		'house9' : {**self.generate_planet_data(self.chart.get(const.HOUSE9)), 'planet_governs':self.house_qualities.get('house9')},
		'house10' : {**self.generate_planet_data(self.chart.get(const.HOUSE10)), 'planet_governs':self.house_qualities.get('house10')},
		'house11' : {**self.generate_planet_data(self.chart.get(const.HOUSE11)), 'planet_governs':self.house_qualities.get('house11')},
		'house12' : {**self.generate_planet_data(self.chart.get(const.HOUSE12)), 'planet_governs':self.house_qualities.get('house12')}
		}
		for k, v in self.p.items():
			self.p[k]['sign_expresses'] = self.sign_qualities.get(v.get('sign').lower())

	def pull_chart(self, date, btime):
		b='+'+str(btime)#.strftime("%H:%M"))
		c=[int(i) for i in date.split('/')]
		offset= ['-',5,0,0] ## modify this for non eastern time zones
		self.pos = GeoPos(self.zipcode_dict["lat"], self.zipcode_dict["lng"])
		self.new_date_obj = Datetime(c, b, offset)
		self.chart = Chart(self.new_date_obj, self.pos, IDs=const.LIST_OBJECTS)

	def get_birthplace(self, bplacezip):
		search = SearchEngine() # simple_zipcode=True
		try:
			zipcode = search.by_zipcode(bplacezip).to_dict()
		except:
			zipcode = search.by_zipcode('01776').to_dict()
		if zipcode['lat'] is not None and zipcode['lng'] is not None:
			self.zipcode_dict=zipcode
		else:
			n=1
			while zipcode['lat'] is None and zipcode['lng'] is None:
				bplacezip = str(int(bplacezip)+n) if len(str(bplacezip))==5 else '02114'
				zipcode = search.by_zipcode(bplacezip).to_dict()
				if zipcode['lat'] is not None and zipcode['lng'] is not None:
					self.zipcode_dict=zipcode
				n+=1
	
	def generate_planet_data(self, planet):
		
		fields = {}

		try:
			fields['name']=planet.__str__()[1:planet.__str__().find(' ')] # planet.name=
		except:
			pass
		try:
			fields['sign']= planet.sign
		except:
			pass
		try:
			fields['isRetrograde']= planet.isRetrograde()
		except:
			pass
		try:
			fields['isFast']= planet.isFast()
		except:
			pass
		try:
			fields['isDirect']= planet.isDirect()
		except:
			pass
		try:
			fields['element']= planet.element()
		except:
			pass
		try:
			fields['gender']= planet.gender()
		except:
			pass
		try:
			fields['movement']= planet.movement()
		except:
			pass
		
		return fields


def email(toaddrs, msg, subj):
	fromaddr = 'starlightstellab@gmail.com'
	sender = 'starlightstellab@gmail.com'
	passwd = 'Gemini69'
	message = MIMEText(msg,"plain","utf-8")
	message['From'] = 'Stella Astrology'
	message['Subject'] = Header(subj,"utf-8").encode()
	smtpObj = smtplib.SMTP("smtp.gmail.com", 587)
	smtpObj.ehlo()                 
	smtpObj.starttls()
	smtpObj.set_debuglevel(1)
	smtpObj.login(sender, passwd)
	smtpObj.sendmail(sender,[toaddrs],message.as_string())
	smtpObj.close()
	time.sleep(10)

def msg_birthchart(star, user):
	body = '''
	Sun Sign: {}
	Moon Sign: {}
	Ascendant Sign: {}
	Mercury Sign: {}
	Venus Sign: {}
	Mars Sign: {}
	Jupiter Sign: {}
	Saturn Sign: {}
	Neptune Sign: {}
	Pluto Sign: {}
	'''.format(star.p.get('sun').get('sign'), star.p.get('moon').get('sign'), star.p.get('asc').get('sign'), star.p.get('mercury').get('sign'), star.p.get('venus').get('sign'), star.p.get('mars').get('sign'), star.p.get('jupiter').get('sign'), star.p.get('saturn').get('sign'), star.p.get('neptune').get('sign'), star.p.get('pluto').get('sign'))
	headline = "Full Birthchart For {}: ".format(user)
	endline = 'Pay special attention to your Sun sign, which is your primary sign, your ascendant, which describes the face you show the world, and your moon sign, which descibes your inner life. Explanations of these coming soon.'
	text = '\n'.join([headline, body, endline])
	print(body)
	subject = "YOUR BIRTHCHART"
	return text, subject

def msg_horoscope_1(star, user, ds, DS, today, expressed):
	subject = '*** HOROSCOPE FOR {}: {} ***'.format(user.upper(), ds)
	body_h = []
	body_p = []
	body_s = [] #list of strings
	body = [] #list of strings
	headline = ['Expressed today ({}) from your birth chart (birthday: {}): \n'.format(DS, stars.bdate)]
	for i in range(len(expressed)):
		sign = expressed[i].get('sign').lower()
		planet = expressed[i].get('name').lower()
		body_h.append('{} in {}'.format(planet.upper(), sign.upper()))
		sign_assoc ='{} is associated with the {}, {}, {} & {}'.format(sign.upper(), star.sign_qualities.get(sign)[0],star.sign_qualities.get(sign)[1], star.sign_qualities.get(sign)[2],star.sign_qualities.get(sign)[3])
		body_s.append(sign_assoc)
		planet_assoc = '{} governs {}, {}, and {}'.format(planet.upper(), star.planet_qualities.get(planet)[0], star.planet_qualities.get(planet)[1], star.planet_qualities.get(planet)[2])
		body_p.append(planet_assoc)
	
	for i in range(len(body_h)):
		body.append('\n'.join([body_h[i],body_p[i],body_s[i]]))
	endline = ['\n\n' + random.choice(['*---Stella signing off---*','We need your feedback! Reply to this email - we read everything :)'])]
	text = '\n'.join(headline+body+endline)
	return text, subject

def msg_sun_explainer(stars, user):
	subject = '*** SUN SIGN EXPLAINER FOR {} ***'.format(user.upper())
	headline = 'UNDERSTANDING SUN IN {}: \n'.format(stars.p.get('sun').get('sign').upper())
	body = stars.sun_qualities[stars.sun_qualities.Quality=='Sun Sign Description'][stars.p.get('sun').get('sign')].values[0]
	endline = ''
	text = '\n'.join([headline, body])
	return text, subject

def msg_moon_explainer(stars, user):
	subject = '*** MOON SIGN EXPLAINER FOR {} ***'.format(user.upper())
	headline = 'UNDERSTANDING MOON IN {}: \n'.format(stars.p.get('moon').get('sign').upper())
	body = stars.sun_qualities[stars.sun_qualities.Quality=='Moon Sign Description'][stars.p.get('moon').get('sign')].values[0]
	text = '\n'.join([headline, body])
	return text, subject

def msg_asc_explainer(stars, user):
	headline = 'UNDERSTANDING RISING SIGN IN {}: \n'.format(stars.p.get('asc').get('sign').upper())
	subject = '*** RISING SIGN EXPLAINER FOR {} ***'.format(user.upper())
	body = stars.sun_qualities[stars.sun_qualities.Quality=='Rising Sign Description'][stars.p.get('asc').get('sign')].values[0]
	text = '\n'.join([headline, body])
	return text, subject

def msg_horoscope(stars, today, username, T):
	N = {k:v.get('sign') for k,v in today.p.items()}
	L =  {k:v.get('sign') for k,v in stars.p.items()}
	X =  {k:v for k,v in L.items() for t,y in N.items() if k==t and v==y }
	horoscope = {}
	if X != {}:
		for x,y in X.items():	# k is username - v is dict # x is planet - y is sign
			print(x,y)
			try:
				result = parse_horoscope(T.loc[x+'_sign_description', y.capitalize()])
				scope = {'{} in {}'.format(x.capitalize(), y): result}
				horoscope.update(scope)
			except:
				pass
	if horoscope != {}:
		headline = 'Expressed today in your sign: {}'.format(' - '.join(horoscope.keys()))
		body = ''
		for k,v in horoscope.items():
			body +=k+':'+'\n'+v+'\n' 
		subject = 'Horoscope for {}'.format(username)
		text = '\n\n'.join([headline]+[body])
		return text, subject
	else:
		return None, None

def parse_horoscope(s):
	k = s.split('. ')
	k = [i for i in k if i.find("If your Sun is in") == -1]
	num = random.choice(range(len(k)-2))
	sentences = k[num:num+3]
	return ". ".join(sentences)

def ops_get_basic_info():
	df=pd.read_csv('survey.csv')
	udf=pd.read_csv('users.csv', dtype = {'birthplacezipcode':str}).dropna().reset_index()	
	DS = dt.today().strftime("%Y-%m-%d")
	_ds = dt.today().strftime("%m/%d/%Y")
	sends = json.load(open('sends.json'))
	ds = dt.today().strftime("%B %d, %Y") # full string
	return df, udf, DS, _ds, sends, ds 

def ops_email():
	#if args.type =='test':
		#i = udf.index.get_indexer_for(udf[udf.emailaddress.apply(lambda x: x.find(args.acct)>=0)].index)[0]
	#if udf.emd5[i] in recd_birthchart and udf.emd5[i] in recd_sun_explainer and udf.emd5[i] in recd_moon_explainer and udf.emd5[i] in recd_asc_explainer:
		#continue

	if udf.emd5[i] not in recd_birthchart:
		msg, subject = msg_birthchart(stars, username)
		msg_type = 'birthchart_1'
	#			email(emailaddr, msg, subject)
		json_data = {'emd5': udf.emd5[i], 'msg_type': msg_type, 'ds': ds}
		sends.append(json_data)

	if udf.emd5[i] not in recd_sun_explainer:
		msg, subject = msg_sun_explainer(stars, username)
		msg_type = 'sun_explainer'
	#			email(emailaddr, msg, subject)
		json_data = {'emd5': udf.emd5[i], 'msg_type': msg_type, 'ds': ds}
		sends.append(json_data)

	if udf.emd5[i] not in recd_moon_explainer:
		msg, subject = msg_moon_explainer(stars, username)
		msg_type = 'moon_explainer'
	#			email(emailaddr, msg, subject)
		json_data = {'emd5': udf.emd5[i], 'msg_type': msg_type, 'ds': ds}
		sends.append(json_data)

	if udf.emd5[i] not in recd_asc_explainer:	
		msg, subject = msg_asc_explainer(stars, username)
		msg_type = 'asc_explainer'
	#			email(emailaddr, msg, subject)
		json_data = {'emd5': udf.emd5[i], 'msg_type': msg_type, 'ds': ds}
		sends.append(json_data)

	else:
		msg, subject = msg_horoscope(stars, today, username, T)
		if msg:
			msg_type = 'horoscope_1'
			email(emailaddr, msg, subject)
			json_data = {'emd5': udf.emd5[i], 'msg_type': msg_type, 'ds': ds}
			sends.append(json_data)
			print(msg)

def ops_loop_item(i, udf):
	stars = Stars(udf.birthdate[i], udf.birthtime[i], udf.birthplacezipcode[i])		
	username = udf.emailaddress[i].split('@')[0]
	msg_type = ''
	msg = None
	emailaddr=udf.emailaddress[i]
	L = []
	X= []
	N =  {k:v.get('sign') for k,v in stars.p.items()}
	N['username']=username
	L.append(N)
	return stars, today, username, emailaddr
	

def main(test=True):
	print('running ast main')
	parser = argparse.ArgumentParser()
	parser.add_argument('--type', type=str, help='scan or daily or test & acct')
	parser.add_argument('--acct', type=str)
	args = parser.parse_args()
	#get data from csv files
	df, udf, DS, _ds, sends, ds = ops_get_basic_info()
	
	i=0
	global today
	print(_ds, udf.birthtime[i], udf.birthplacezipcode[i])
	today = Stars(_ds, udf.birthtime[i], udf.birthplacezipcode[i])
	with open('today_data.txt', 'w') as file:
		file.write(json.dumps(today.p))
	#for i in reversed(range(len(udf))):
	#	stars, today, username, emailaddr = ops_loop_item(i, udf)
		#ops_email()
	#	with open('sends.json', 'w') as fp:
	#		    json.dump(sends, fp)

#wp=Stars(udf.birthdate[0], udf.birthtime[i], udf.birthplacezipcode[i])

#wp.p.keys()

if __name__ == "__main__":
	main()