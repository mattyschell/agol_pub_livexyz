import unittest

import filter_group_report


class FilterGroupReportTestCase(unittest.TestCase):

    def test_excluded_rows_blank_email_with_nyc_username_is_not_suspect(self):

        header = [
            'username'
           ,'user.fullName'
           ,'user.email'
           ,'user.role'
           ,'user.lastLogin'
           ,'group_role'
        ]

        # this is fabricated data
        data_rows = [
                        ['headless.user', 'Headless User', '', '', '2026-07-01', 'member']
                     ,['internal.blank@agency.nyc.gov_nyc', 'Internal Blank', '', '',
                         '2026-07-01', 'member']
           ,['external.user', 'External User', 'ext@example.com', 'org_user',
             '2026-07-01', 'member']
                     ,['nypd.user', 'NYPD User', 'nypd.user@nypd.org', 'org_user',
                         '2026-07-01', 'member']
           ,['employee.user', 'Employee User', 'employee@agency.nyc.gov',
             'org_user', '2026-07-01', 'member']
        ]

        filtered = filter_group_report._excluded_rows(
            header
           ,data_rows
           ,['username', 'user.email']
           ,['*nyc.gov*', '*nypd.org*']
        )

        self.assertEqual(len(filtered)
                        ,2)
        self.assertEqual(filtered[0][0]
                        ,'headless.user')
        self.assertEqual(filtered[1][0]
                        ,'external.user')

    def test_excluded_rows_blank_email_without_match_still_suspect(self):

        header = [
            'username'
           ,'user.fullName'
           ,'user.email'
           ,'user.role'
           ,'user.lastLogin'
           ,'group_role'
        ]

        data_rows = [
            ['headless.user', 'Headless User', '', '', '2026-07-01',
             'member']
           ,['external.user', 'External User', 'ext@example.com', 'org_user',
             '2026-07-01', 'member']
        ]

        filtered = filter_group_report._excluded_rows(
            header
           ,data_rows
           ,['username', 'user.email']
           ,['*nyc.gov*', '*nypd.org*']
        )

        self.assertEqual(len(filtered)
                        ,2)
        self.assertEqual(filtered[0][0]
                        ,'headless.user')
        self.assertEqual(filtered[1][0]
                        ,'external.user')

    def test_excluded_rows_allowlist_suppresses_blank_email_suspect(self):

        header = [
            'username'
           ,'user.fullName'
           ,'user.email'
           ,'user.role'
           ,'user.lastLogin'
           ,'group_role'
        ]

        data_rows = [
            ['known.good.user', 'Known Good User', '', '', '2026-07-01',
             'member']
           ,['external.user', 'External User', 'ext@example.com', 'org_user',
             '2026-07-01', 'member']
        ]

        filtered = filter_group_report._excluded_rows(
            header
           ,data_rows
           ,['username', 'user.email']
           ,['*nyc.gov*', '*nypd.org*']
           ,{'known.good.user'}
        )

        self.assertEqual(len(filtered)
                        ,1)
        self.assertEqual(filtered[0][0]
                        ,'external.user')

    def test_excluded_rows_without_email_column_keeps_pattern_behavior(self):

        header = [
            'username'
           ,'group_role'
        ]

        data_rows = [
            ['a.user', 'member']
           ,['employee.user@agency.nyc.gov', 'member']
        ]

        filtered = filter_group_report._excluded_rows(
            header
           ,data_rows
           ,['username']
              ,['*nyc.gov*', '*nypd.org*']
        )

        self.assertEqual(len(filtered)
                        ,1)
        self.assertEqual(filtered[0][0]
                        ,'a.user')


if __name__ == '__main__':
    unittest.main()
