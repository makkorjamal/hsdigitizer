from pysolar.solar import get_altitude
import datetime

date_time_str = '15/04/1951 12:00'
date_time_obj = datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M').replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=1)
sza = float(90) - get_altitude(46.5475, 46.5475, date_time_obj)
print ("timezone = UTC+1,",sza)
