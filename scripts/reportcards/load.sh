YEAR="2013"
MONTH="03"
COUNTRIES="tz zm mw mz zw za ls cd"

for COUNTRY in ${COUNTRIES}
do
    wget http://tendai.medicinesinfohub.net/scorecards/${COUNTRY}/${YEAR}/${MONTH}/ -O scorecard_${COUNTRY}.svg
done
