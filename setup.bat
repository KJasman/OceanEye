ECHO Creating Virtual Environment Spectral in current directory
pip install virtualenv
virtualenv Spectral_Test
cd Spectral_Test/
source Scripts/activate
ECHO Virtual Environment activated...
ECHO Cloning Git Repo...
git clone https://github.com/bhans-uvic/Spectral_Detection.git
cd Spectral_Detection/
ECHO Installing requirements...
pip install -r requirements.txt
ECHO Done. Use the following command to start the app:
ECHO streamlit run app.py
streamlit run app.py