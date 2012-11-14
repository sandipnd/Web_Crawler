import time
from datetime import date , timedelta , datetime
import re

month = {}
count = 1
for mth in [ 'January' , 'February' , 'March' , 'April', 'May' , 'June' , 'July' , 'August', 'September' , 'October' , 'November','December']:
    month[count] = mth
    count = count + 1

def todays(time):
    global month
    tod = date.today()
    dates =  str(tod.day) + " " + month[tod.month] + " " +  str(tod.year)
    time = re.sub(r'Today,',dates,time)
    return time


def yesterdays(time):
    global month
    tod = datetime.now() - timedelta(days=1)
    dates =  str(tod.day) + " " + month[tod.month] + " " +  str(tod.year) 
    time = re.sub(r'Yesterday,',dates,time)
    return time
    

def nDaysAgo(time):
    global month
    #regex to get the number of days which will replace 1 
    tod =datetime.now() - timedelta(days=val)
    dates =  month[tod.month] + " " + str(tod.day) + " " + str(tod.year)
    time = re.sub(r'Yesterday,',dates,time)
    return time

def nMinutesAgo(time):
    global month
    #regex to get the number of days which will replace 1
    m = re.search("(\d{1,2}) minutes",time)
    val = m.group(1)
    tod =datetime.now() - timedelta(minutes=int(val))
    dates = str(tod.day) + " "  + month[tod.month] + " " + str(tod.year)
    tm = "  " +  str(tod.hour) + ":" + str(tod.minute)
    time = dates + tm
    return time

#print yesterdays("Yesterday, uio")
#29 October 2012 - 11:54 PM
def processForDatabase(time):
    flag = False
    try:
        date_object = datetime.strptime(time,'%d %B %Y  %I:%M %p')
        time_format = date_object.date().isoformat()
        time_format = time_format + "  " + date_object.time().isoformat()
        return time_format
    except:
        flag = True
        try:
            date_object = datetime.strptime(time,'%d %B %Y  %H:%M')
        except:
            date_object = datetime.strptime(time,'%d %b %Y  %I:%M %p')
        
    #print "date" , date_object    
    time_format = date_object.date().isoformat()
    
    if flag:
        time_format = time_format + "  " + date_object.time().isoformat()
    return time_format
