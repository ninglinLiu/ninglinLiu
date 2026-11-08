from datetime import date, timedelta
from io import BytesIO
from unittest import TestCase, main
from unittest.mock import patch
from urllib.error import HTTPError
from scripts import refresh_activity as activity


class CalendarRefreshTests(TestCase):
    def setUp(self):
        self.start = date(2025, 11, 9)
        self.end = self.start + timedelta(days=364)
        self.days = [{'date': str(self.start + timedelta(days=i)),
                      'contributionCount': i % 5, 'contributionLevel': 'FIRST_QUARTILE'}
                     for i in range(365)]

    def test_complete_year_and_level_mapping(self):
        self.days[-1]['contributionLevel'] = 'FOURTH_QUARTILE'
        rows = activity.parse_calendar([{'contributionDays': self.days[::-1]}], self.start, self.end)
        self.assertEqual(len(rows), 365)
        self.assertEqual(rows[0]['date'], str(self.start))
        self.assertEqual(rows[-1]['level'], 4)

    def test_missing_or_duplicate_day_is_rejected(self):
        for days in [self.days[:-1], self.days[:-1] + self.days[:1]]:
            with self.subTest(length=len(days)), self.assertRaises(RuntimeError):
                activity.parse_calendar([{'contributionDays': days}], self.start, self.end)

    @patch.object(activity.time, 'sleep')
    @patch.object(activity.urllib.request, 'urlopen')
    def test_transient_server_error_is_retried(self, urlopen, sleep):
        urlopen.side_effect = [HTTPError('https://api.github.com/graphql', 503, 'Unavailable', {}, None), BytesIO(b'ok')]
        self.assertEqual(activity.request('https://api.github.com/graphql'), 'ok')
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(2)

    @patch.object(activity.time, 'sleep')
    @patch.object(activity.urllib.request, 'urlopen')
    def test_permission_error_is_not_retried(self, urlopen, sleep):
        urlopen.side_effect = HTTPError('https://api.github.com/graphql', 403, 'Forbidden', {}, None)
        with self.assertRaises(HTTPError):
            activity.request('https://api.github.com/graphql')
        self.assertEqual(urlopen.call_count, 1)
        sleep.assert_not_called()


if __name__ == '__main__':
    main()
