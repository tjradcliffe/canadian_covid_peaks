cd download
python3 download_covid_data.py
python3 extract_hospitalized.py
cp can_hosp_patients.csv ../peak_fit/
cd ../peak_fit
python3 detrend.py
cp can_hosp_patients_fit.csv can_hosp_patients.dat ../seir_fit/
cd ../seir_fit
python3 seir_model.py -1
