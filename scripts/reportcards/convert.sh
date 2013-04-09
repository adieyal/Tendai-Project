YEAR="2012"
MONTH="09"
COUNTRIES="tz zm mw mz zw za ls cd"

for COUNTRY in ${COUNTRIES}
do
    inkscape scorecard_${COUNTRY}.svg --export-pdf=scorecard_${COUNTRY}.pdf
done

