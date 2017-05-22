from availability_builder import ResourceAvailability


unit = ResourceAvailability()
unit.generate_resource_list()
unit.generate_start_end_time()
print 'Start Time: %s' % unit.start_time
print '  End Time: %s' % unit.end_time
# init check:
# user_list = unit.cs_session.GetAllUsersDetails().Users
# for user in user_list:
#     print user.Name

# cap = unit._get_reservations(target)
# print cap
# print unit._convert_to_ISO8601('02/14/2017 23:55')
# if unit._resource_exists(target):
#     print 'I think therefore I am'
# else:
#     print 'Free will is an illusion'

unit._clear_sql_table()

unit._open_sql_connection()

sql_line = 'INSERT INTO [%s] VALUES (' % unit.configs['sql_table']
sql_line += "'Test Reservation ID',"
sql_line += "'Test Reservation Name',"
sql_line += "'Test Reservation Owner',"
sql_line += "'2017-05-18 20:00',"
sql_line += "'2017-05-18 22:00',"
sql_line += "'s6000-1000',"
sql_line += "'Test Family',"
sql_line += "'Test Model',"
sql_line += "'5')"

unit.sql_cursor.execute(sql_line)
unit.sql_connection.commit()

unit._clear_sql_table()

for h in unit.configs['report_headers']:
    if ('Start' in h) or ('End' in h):
        unit.reservation_report[h].append('2017-02-14 12:34:00')
    elif h == 'Metric':
        unit.reservation_report[h].append(42)
    else:
        unit.reservation_report[h].append('Test')

unit.write_to_sql()

unit.get_availability()

# l = len(unit.reservation_report[unit.headers[0]])
#
# for n in xrange(l):
#     line = ''
#     for head in unit.headers:
#         t = unit.reservation_report[head]
#         line += '%s || ' % t[n]
#     print line

print 'stop'

