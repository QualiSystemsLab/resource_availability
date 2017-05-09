from availability_builder import ResourceAvailability


unit = ResourceAvailability()

# init check:
# user_list = unit.cs_session.GetAllUsersDetails().Users
# for user in user_list:
#     print user.Name

target = ['JPN_1', 'JPN_2']
start = '09/05/2017 20:00'
end = '11/05/2017 20:00'
# cap = unit._get_reservations(target)
# print cap

# if unit._resource_exists(target):
#     print 'I think therefore I am'
# else:
#     print 'Free will is an illusion'

print unit.get_availability(resource_list=target, start_time=start, end_time=end)
