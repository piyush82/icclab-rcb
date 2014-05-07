'''
Created on May 7, 2014

@author: kolv
'''

import datetime
from time import strptime

from_date="2014-05-05"
from_time="00:00:00"

end_date="2014-05-06"
end_time="23:00:00"

t1=datetime.datetime.strptime(from_date,"%Y-%m-%d").date()
print t1
t2=datetime.datetime.strptime(from_time,"%H:%M:%S").time()
print t2

t=datetime.datetime.combine(t1,t2)
print t

t3=datetime.datetime.strptime(end_date,"%Y-%m-%d").date()
print t3
t4=datetime.datetime.strptime(end_time,"%H:%M:%S").time()
print t4

tt=datetime.datetime.combine(t3,t4)

pom=tt-t
print pom

m=pom.total_seconds()

print pom.days,  pom.seconds