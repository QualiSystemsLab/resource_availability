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
unit.get_availability()

l = len(unit.reservation_report[unit.headers[0]])

for n in xrange(l):
    line = ''
    for head in unit.headers:
        t = unit.reservation_report[head]
        line += '%s || ' % t[n]
    print line

print 'stop'

