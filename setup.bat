ECHO Creating Virtual Environment Spectral in current directory...
pip install virtualenv
virtualenv Spectral
cd Spectral/
source Scripts/activate
ECHO Virtual Environment activated...
ECHO Cloning Git Repo...
git clone --branch main https://github.com/KJasman/OceanEye.git
cd OceanEye/
ECHO Installing requirements...
pip install -r requirements.txt
ECHO Done. Use the following command to start the app:
ECHO streamlit run app.py
streamlit run app.py
