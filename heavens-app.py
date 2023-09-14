import sys
sys.path.append('/usr/local/lib/python3.9/site-packages/flatlib/resources/swefiles')

import streamlit as st
from astrology import Stars
from datetime import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from flatlib import ephem

print('path: ', flatlib.PATH_LIB, flatlib.PATH_RES, sys.path, flush=True)

print('path: ', flatlib.PATH_LIB, flatlib.PATH_RES, sys.path)

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