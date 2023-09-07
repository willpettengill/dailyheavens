# dailyheavens
Streamlit daily heavens app
Steps to deploy were: (following this guide: https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
install docker on server
git pull repository
change docker entrypoint and expose to 80: 
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=80", "--server.address=0.0.0.0"]
(do not change server address)
docker build -t streamlit .
docker run -p 80:80 streamlit