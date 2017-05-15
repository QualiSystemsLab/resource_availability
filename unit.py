from availability_builder import ResourceAvailability


unit = ResourceAvailability()

# init check:
# user_list = unit.cs_session.GetAllUsersDetails().Users
# for user in user_list:
#     print user.Name

target = ['ct-z9100-1', 'dv-ngos-s4148u-2', 'ngos-s6000-4', 'dv-fedgov-m1000e-1', 'st-sjc-s4048-1', 'st-sjc-s4048t-1',
          'dv-sjc-mcast-nav-102', 'dv-s4810-7']
start = '10/05/2017 18:00'
end = '17/05/2017 18:00'
# cap = unit._get_reservations(target)
# print cap
# print unit._convert_to_ISO8601('02/14/2017 23:55')
# if unit._resource_exists(target):
#     print 'I think therefore I am'
# else:
#     print 'Free will is an illusion'

print unit.get_availability(resource_list=target, start_time=start, end_time=end)
