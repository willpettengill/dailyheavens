import sys
sys.path.append('/usr/local/lib/python3.9/site-packages/flatlib/resources/swefiles')

import streamlit as st
from uszipcode import SearchEngine
#from astrology import Stars
from datetime import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import flatlib
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

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



print('path: ', flatlib.PATH_LIB, flatlib.PATH_RES, sys.path, flush=True)
date = Datetime('2015/03/13', '17:00', '+00:00')
pos = GeoPos('38n32', '8w54')
chart = Chart(date, pos)
sun = chart.get(const.SUN)
print(sun)


st.title('Calculate Your Chart :night_with_stars::milky_way:')
st.subheader('See the makeup of your full zodiac chart')

with st.form("user_zodiac_data"):
    bd=st.date_input("Your Birthday", format="YYYY/MM/DD")
    bt=st.time_input("Your Birthtime")
    st.caption('optional, approximate is okay')
    bz=st.text_input("Your Birthplace Zip Code", value='01776')
    #st.write(bd, bt, bz)
    st.caption('optional, approximate is okay')
    submitted = st.form_submit_button("Read Chart")
    if submitted:
        stars = Stars(bd.strftime(("%Y/%m/%d")), bt, bz)
        today = Stars(datetime.now().strftime("%Y/%m/%d"), datetime.now().time().strftime("%H:%M:%S"), '01776')

    else:
        st.stop()
df = pd.DataFrame.from_dict(stars.p, orient='index')
df['is_Retrograde'] = df['isRetrograde'].apply(lambda x: 2 if x else 1) # if 
pivot_table = df.pivot_table(index='sign', columns='name', values='is_Retrograde', fill_value=None, sort=False)
# Heatmap: Planetary Movement
fig = plt.figure(figsize=(10, 6))
sns.heatmap(pivot_table, cmap="PiYG", annot=False, fmt="f", cbar=False)

# Show the plot
st.subheader("Your Zodiac Chart")
st.write(df[['sign','planet_governs', 'sign_expresses']])

st.subheader("Planetary Movement (Direct/Retrograde)")
st.pyplot(fig)
st.caption("Green: direct movement; Purple: retrograde movement.")

st.divider()
st.subheader('Understanding Sun in {} :{}:'.format(stars.p.get('sun').get('sign').capitalize(), stars.p.get('sun').get('sign').lower()))
st.markdown(stars.sun_qualities[stars.sun_qualities.Quality=='Sun Sign Description'][stars.p.get('sun').get('sign')].values[0])

st.divider()
st.subheader('Understanding Moon in {} :{}:'.format(stars.p.get('moon').get('sign').capitalize(), stars.p.get('moon').get('sign').lower()))
st.markdown(stars.sun_qualities[stars.sun_qualities.Quality=='Moon Sign Description'][stars.p.get('moon').get('sign')].values[0])

st.divider()
st.subheader('Understanding Rising Sign in {} :{}:'.format(stars.p.get('ascendant').get('sign').capitalize(), stars.p.get('ascendant').get('sign').lower()))
st.markdown(stars.sun_qualities[stars.sun_qualities.Quality=='Rising Sign Description'][stars.p.get('ascendant').get('sign')].values[0])