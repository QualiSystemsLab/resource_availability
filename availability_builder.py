import cloudshell.api.cloudshell_api as cs_api
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
import json
import logging
import time
from base64 import b64decode, b64encode


class ResourceAvailability(object):

    def __init__(self):
        # declarations
        self.reservation_report = {}

        # load configs.json
        self.json_file_path = 'configs.json'
        self.configs = json.loads(open(self.json_file_path).read())

        # connect to CloudShell
        try:
            self.cs_session = cs_api.CloudShellAPISession(self.configs["cloudshell_server"],
                                                          self.configs["cs_admin_username"],
                                                          b64decode(self.configs["cs_admin_password"]),
                                                          domain=self.configs["cs_domain"], port=8029)
        except CloudShellAPIError as e:
            msg = self._get_dts() + '\n Critical Error connecting to CloudShell' + \
                  '\n' + self.configs["who_am_i"] + ' attempting to start CloudShell API Session' + \
                  '\nServer: ' + self.configs["cloudshell_server"]
            print msg
            # self._send_email('Error connecting to CloudShell', msg)

    def _get_dts(self):
        return time.strftime('%Y-%m-%d %H:%M:%S')

    def _resource_exists(self, device_name):
        try:
            self.cs_session.GetResourceDetails(resourceFullPath=device_name)
            return True
        except CloudShellAPIError:
            return False

    def get_reservations(self, device_name, start_time='', end_time=''):
        """
        
        :param string device_name: Full Name of Resource in Question
        :rtype: FindResourceListInfo
        """
        item_list = self.cs_session.GetResourceAvailabilityInTimeRange(resourcesNames=[device_name],
                                                                       startTime=start_time,
                                                                       endTime=end_time,
                                                                       showAllDomains=True).Resources

        for item in item_list:
            if '/' not in item.Name:
                for each in item.Reservations:
                    keys = self.reservation_report.keys()
                    if device_name not in keys:
                        self.reservation_report[device_name] = {'Name': [], 'Owner': [], 'Start': [], 'End': [],
                                                                'ID': []}

                    # pull from master dict
                    temp_d = self.reservation_report[device_name]

                    # fill it out
                    temp_d['Name'].append(each.ResourceFullName)
                    temp_d['Owner'].append(each.Owner)
                    temp_d['Start'].append(each.StartTime)
                    temp_d['End'].append(each.EndTime)
                    temp_d['ID'].append(each.ReservationId)

                    # return it to master
                    self.reservation_report[device_name] = temp_d

    def get_availability(self, resource_list=[], start_time='DD/MM/YYYY HH:MM', end_time='DD/MM/YYYY HH:MM'):
        # --TBD--
        # if start_time == 'DD/MM/YYYY HH:MM':
        #     start_time = time.strftime('%d/%m/%Y %H:%M')
        # if end_time == 'DD/MM/YYYY HH:MM':
        #     end_time = None

        for resource in resource_list:
            if self._resource_exists(resource):
                self.get_reservations(device_name=resource, start_time=start_time, end_time=end_time)

        return json.dumps(self.reservation_report, sort_keys=False, indent=4, separators=(',', ': '))
