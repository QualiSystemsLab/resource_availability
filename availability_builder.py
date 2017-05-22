import cloudshell.api.cloudshell_api as cs_api
from cloudshell.api.common_cloudshell_api import CloudShellAPIError
import json
import logging
import time
from base64 import b64decode, b64encode
import pymssql


class ResourceAvailability(object):
    def __init__(self):
        # declarations
        # self.reservation_report = []  # AmChart
        self.reservation_report = dict()  # for SQL use
        self.resource_list = []
        self.start_time = ''
        self.end_time = ''
        self.sql_connection = None
        self.sql_cursor = None

        # load configs.json
        self.json_file_path = './configs.json' # 'C:/Users/ksaper/Documents/resource_availability/configs.json'
        self.configs = json.loads(open(self.json_file_path).read())

        # set report headers:
        self.headers = self.configs["report_headers"]
        # set headers to dict - sql use:
        for head in self.headers:
            self.reservation_report[head] = []

        # set metric dict info
        self.metric_rating = self.configs['metric_rating']
        self.metric_default = self.configs['metric_default']

        # connect to CloudShell
        # connecting to CloudShell in GMT (if timezone not specified: accounted for in self.generate_start_end_time()
        try:
            self.cs_session = cs_api.CloudShellAPISession(self.configs["cloudshell_server"],
                                                          self.configs["cs_admin_username"],
                                                          b64decode(self.configs["cs_admin_password"]),
                                                          domain=self.configs["cs_domain"], port=8029)
        except CloudShellAPIError as e:
            msg = self._get_dts() + '\n Critical Error connecting to CloudShell' + \
                  '\n' + self.configs["who_am_i"] + ' attempting to start CloudShell API Session' + \
                  '\nServer: ' + self.configs["cloudshell_server"]
            print '%s\n%s' % (msg, e.message)
            # self._send_email('Error connecting to CloudShell', msg)

    def _get_dts(self):
        return time.strftime('%Y-%m-%d %H:%M:%S')

    def _resource_exists(self, device_name):
        try:
            self.cs_session.GetResourceDetails(resourceFullPath=device_name)
            return True
        except CloudShellAPIError:
            return False

    def _convert_to_ISO8601(self, dts_in=''):
        date, time = dts_in.split(' ', 1)
        MM, DD, YYYY = date.split('/')
        return '%s-%s-%s %s' % (YYYY, MM, DD, time)

    def _get_metric_rating(self, model_name):
        return self.metric_rating.get(model_name, self.metric_default)

    def get_reservations(self, device_name, start_time='', end_time=''):
        """

        :param string device_name: Full Name of Resource in Question
        :rtype: FindResourceListInfo
        """
        item_list = self.cs_session.GetResourceAvailabilityInTimeRange(resourcesNames=[device_name],
                                                                       startTime=start_time,
                                                                       endTime=end_time,
                                                                       showAllDomains=True).Resources

        # Thi is how do format for AmCharts - requires reservation_report to be a list
        # for item in item_list:
        #     if item.FullName == device_name:
        #         temp_d = dict()
        #         temp_d['category'] = device_name
        #         temp_d['segments'] = []
        #         for each in item.Reservations:
        #             inner = dict()
        #             inner['start'] = self._convert_to_ISO8601(each.StartTime)
        #             inner['end'] = self._convert_to_ISO8601(each.EndTime)
        #             inner['task'] = '%s owned by: %s (%s)' % (each.ReservationName, each.Owner, each.ReservationId)
        #             temp_d['segments'].append(inner)
        #         self.reservation_report.append(temp_d)

        # this is formatting for SQL - requires reservation_report to be a dict
        for item in item_list:
            if item.FullName == device_name:
                detail = self.cs_session.GetResourceDetails(device_name)
                model_name = detail.ResourceModelName
                family_name = detail.ResourceFamilyName
                for each in item.Reservations:
                    for header in self.headers:
                        if header == 'ReservationID':
                            self.reservation_report[header].append(each.ReservationId)
                        if header == 'ReservationName':
                            self.reservation_report[header].append(each.ResourceFullName)
                        if header == 'ReservationOwner':
                            self.reservation_report[header].append(each.Owner)
                        if header == 'ReservationStart':
                            self.reservation_report[header].append(self._convert_to_ISO8601(each.StartTime))
                        if header == 'ReservationEnd':
                            self.reservation_report[header].append(self._convert_to_ISO8601(each.EndTime))
                        if header == 'ItemName':
                            self.reservation_report[header].append(device_name)
                        if header == 'ItemFamily':
                            self.reservation_report[header].append(family_name)
                        if header == 'ItemModel':
                            self.reservation_report[header].append(model_name)
                        if header == 'Metric':
                            self.reservation_report[header].append(str(self._get_metric_rating(model_name)))

    def generate_resource_list(self):
        for each in self.configs["fam_model_list"]:
            family, model = each.split(',', 1)
            self.resource_list += self.cs_session.FindResources(resourceFamily=family, resourceModel=model).Resources

    def generate_start_end_time(self):
        start_offset = self.configs["start_offset"] + time.timezone  # +Timezone adjusts for GMT
        end_offset = self.configs["end_offset"] + time.timezone

        self.start_time = time.strftime('%d/%m/%Y %H:%M', time.localtime(time.mktime(time.localtime()) + start_offset))
        self.end_time = time.strftime('%d/%m/%Y %H:%M', time.localtime(time.mktime(time.localtime()) + end_offset))

    def _open_sql_connection(self):
        try:
            self.sql_connection = pymssql.connect(host=self.configs['sql_server_address'],
                                                  user=self.configs['sql_server_user'],
                                                  password=b64decode(self.configs['sql_server_password']),
                                                  database=self.configs['sql_database']
                                                  )
            self.sql_cursor = self.sql_connection.cursor()
        except StandardError as err:
            print err.message
            self.sql_connection = None

    def _close_sql_connection(self):
        if self.sql_connection:
            self.sql_connection.close()

    def _clear_sql_table(self):
        if not self.sql_connection:
            self._open_sql_connection()

        if self.sql_connection:
            self.sql_cursor.execute('DELETE FROM [%s].[dbo].[%s]' % (self.configs['sql_database'],
                                                                     self.configs['sql_table'])
                                    )
            self.sql_connection.commit()

    def write_to_sql(self):
        if not self.sql_connection:
            self._open_sql_connection()

        # clear the existing table
        self._clear_sql_table()

        length = len(self.reservation_report[self.headers[0]])
        for idx in xrange(length):
            line = []
            for h in self.headers:
                temp = self.reservation_report[h]
                line.append(temp[idx])

            sql_line = 'INSERT INTO [%s] VALUES (' % self.configs['sql_table']  # open the sql write line
            check = (len(line) - 1)

            # build data for the sql table
            temp = ''
            for i in xrange(len(line)):
                if i < check:
                    temp += "'%s'," % line[i]
                else:
                    temp += "'%s'" % line[i]
            # end for loop

            sql_line += '%s)' % temp  # add data and close the sql line

            # ensure SQL Connection is opened
            if not self.sql_connection:
                self._open_sql_connection()

            if self.sql_connection:
                try:
                    self.sql_cursor.execute(sql_line)
                    self.sql_connection.commit()
                except StandardError as err:
                    print err.message
        # end report loop

        if self.sql_connection:
            self._close_sql_connection()

    def get_availability(self):
        # --TBD--
        # if start_time == 'DD/MM/YYYY HH:MM':
        #     start_time = time.strftime('%d/%m/%Y %H:%M')
        # if end_time == 'DD/MM/YYYY HH:MM':
        #     end_time = None
        self.generate_resource_list()
        self.generate_start_end_time()
        for resource in self.resource_list:
            if self._resource_exists(resource.Name):
                self.get_reservations(device_name=resource.Name, start_time=self.start_time, end_time=self.end_time)

        self.write_to_sql()
        # return json.dumps(self.reservation_report, sort_keys=False, indent=4, separators=(',', ': ')) for AmCharts
