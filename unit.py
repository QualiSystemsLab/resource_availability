from availability_builder import ResourceAvailability


unit = ResourceAvailability()

# init check:
# user_list = unit.cs_session.GetAllUsersDetails().Users
# for user in user_list:
#     print user.Name

target = ['JPN_1', 'JPN_2']
start = '10/05/2017 18:00'
end = '11/05/2017 20:00'
# cap = unit._get_reservations(target)
# print cap
# print unit._convert_to_ISO8601('02/14/2017 23:55')
# if unit._resource_exists(target):
#     print 'I think therefore I am'
# else:
#     print 'Free will is an illusion'

print unit.get_availability(resource_list=target, start_time=start, end_time=end)
