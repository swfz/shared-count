from __future__ import absolute_import
import unittest
import logging
import glob
import re
import json
from pprint import pprint
from aggregator import run
from apache_beam.testing.util import open_shards

class AggregatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pprint('setupclass---------------------------------------------------------')
        cls.aggregated = {
            'summary': {
                '://example.com/entry/1': {'hier_part': '://example.com/entry/1'},
                '://example.com/entry/2': {'hier_part': '://example.com/entry/2'}
            },
            'row': []
        }
        def to_hier_part(url):
            return re.sub(r'^http[s]?', '', url)

        files = glob.glob('./sample_input/raw-twitter-basic*.json')

        for filename in files:
            with open(filename) as file:
                for line in file:
                    row = json.loads(line)
                    hier_part = to_hier_part(row['url'])
                    cls.aggregated['summary'][hier_part]['twitter_likes'] = row['likes']
                    cls.aggregated['summary'][hier_part]['twitter_shared'] = row['count']
                    count = {
                        'url': row['url'],
                        'hier_part': hier_part,
                        'service': 'twitter',
                        'metric': 'shared',
                        'value': row['count']
                    }
                    likes = {
                        'url': row['url'],
                        'hier_part': hier_part,
                        'service': 'twitter',
                        'metric': 'likes',
                        'value': row['likes']
                    }
                    cls.aggregated['row'].append(count)
                    cls.aggregated['row'].append(likes)

    def setUp(self):
        self.aggregated = type(self).aggregated

    def tearDown(self):
        pprint('teardown-----------------------------------------------------')


    def test_basic(self):
        run(['--input=%s' % './sample_input/raw-twitter-*.json', '--output=%s.result' % './sample_output/output'])

        with open_shards('./sample_output/' + 'output.result-summary-*-of-*') as result_file:
            lines = []
            for line in result_file:
                lines.append(eval(line))

            self.assertEqual(
                sorted(lines, key=lambda x: x['hier_part']),
                sorted(self.aggregated['summary'].values(), key=lambda x: x['hier_part'])
            )

        with open_shards('./sample_output/' + 'output.result-row-*-of-*') as result_file:
            lines = []
            for line in result_file:
                lines.append(eval(line))

            self.assertEqual(
                sorted(lines, key=lambda x: (x['hier_part'], x['metric'])),
                sorted(self.aggregated['row'], key=lambda x: (x['hier_part'], x['metric']))
            )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
