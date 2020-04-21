from __future__ import absolute_import
import unittest
import logging
import glob
import json
from pprint import pprint
from timeseries import run
from apache_beam.testing.util import open_shards

class TimeseriesTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.aggregated = []

        s_files = glob.glob('./sample_input/snapshot-sns-*.json')
        for filename in s_files:
            with open(filename) as file:
                for line in file:
                    row = json.loads(line)

                    index = next((index for (index, d) in enumerate(cls.aggregated) if d['date'] == row['date']), None)
                    if not index is None:
                        cls.aggregated[index] = dict(cls.aggregated[index], **row)
                    else:
                        cls.aggregated.append(row)

        h_files = glob.glob('./sample_input/snapshot-hatenastatus-*.json')
        for filename in h_files:
            with open(filename) as file:
                for line in file:
                    row = json.loads(line)
                    del row['service']

                    index = next((index for (index, d) in enumerate(cls.aggregated) if d['date'] == row['date']), None)
                    if not index is None:
                        cls.aggregated[index] = dict(cls.aggregated[index], **row)
                    else:
                        cls.aggregated.append(row)

    def setUp(self):
        self.aggregated = type(self).aggregated


    def tearDown(self):
        pprint('teardown-----------------------------------------------------')

    def test_basic(self):
        run(['--input=%s' % './sample_input/snapshot-*.json', '--output=%s.timeseries' % './sample_output/output'])

        with open_shards('./sample_output/' + 'output.timeseries-*-of-*') as result_file:
            lines = []
            for line in result_file:
                lines.append(eval(line))

            with self.subTest(type='timeseries'):
                self.assertEqual(
                    sorted(lines, key=lambda x: x['date']),
                    sorted(self.aggregated, key=lambda x: x['date'])
                )


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
