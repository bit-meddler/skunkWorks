GPs = """5 March: Bahrain (Sakhir)

19 March: Saudi Arabia (Jeddah)

2 April: Australia (Melbourne)

16 April: China (Shanghai)

30 April: Azerbaijan (Baku)

7 May: Miami

21 May: Emilia Romagna (Imola)

28 May: Monaco

4 June: Spain (Barcelona)

18 June: Canada (Montreal)

2 July: Austria (Red Bull Ring)

9 July: United Kingdom (Silverstone)

23 July: Hungary (Budapest)

30 July: Belgium (Spa-Francorchamps)

27 August: Netherlands (Zandvoort)

3 September: Italy (Monza)

17 September: Singapore (Marina Bay)

24 September: Japan (Suzuka)

8 October: Qatar (Losail)

22 October: USA (Austin)

29 October: Mexico (Mexico City)

5 November: Brazil (Sao Paulo)

18 November: Las Vegas

26 November: Abu Dhabi (Yas Marina)""" # copied from BBC F1 page

import re # now you have two problems
from datetime import datetime

re_search = r"\s*(\d+\s[A-Za-z]+):\s*([A-Za-z ]*)(?:\s*\(([A-Za-z ]*)\))?"
DAY_FMT = "%d %B"
MATCH = re.compile( re_search )

# decode and collect the GPs
races = []
for line in GPs.splitlines():
    match = MATCH.match( line )
    if( match ):
        date_str, state, venue = match.groups()
        date = datetime.strptime( date_str, DAY_FMT ).replace( year=2023, hour=14, minute=0, second=0, microsecond=0 )
        races.append( [ date, state, venue ] )

DATE_FMT = "%d/%m/%Y"
TIME_FMT = "%H:%M"
OUT_FILE = "f1.csv"
# output to Google compatible CSV
with open( OUT_FILE, "w" ) as fh:
    fh.write( "Subject,Start Date,Start Time,End Date,End Time,All Day Event,Description,Location\n" )
    for start, state, venue in races:
        state = state.strip()
        if( venue is None ):
            venue = state
        end = start.replace( hour=14 )
        fh.write( "{title},{start_d},{start_t},{end_d},{end_t},FALSE, ,{loc}\n".format(
            title=state + " GP",
            start_d=start.strftime( DATE_FMT ), start_t=start.strftime( TIME_FMT ),
            end_d=end.strftime( DATE_FMT ), end_t=end.strftime( TIME_FMT ),
            loc=venue
        ) )

# Import to g-suite: https://support.google.com/calendar/answer/37118?hl=en#import_to_gcal
# NOTE: Update times when they are confirmed on F1 website
