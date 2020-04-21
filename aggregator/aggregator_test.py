from __future__ import absolute_import
import unittest
import logging
import glob
import re
import json
import datetime as dt
from functools import reduce
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
                '://example.com/entry/2': {'hier_part': '://example.com/entry/2'},
                '://example.com/': {'hier_part': '://example.com/'} # analyticsでは定形のURL以外の形式で入ってくることもる
            },
            'row': [],
            'bookmarks': [],
            'tag': [],
            'star': []
        }

        def to_hier_part(url):
            return re.sub(r'^http[s]?', '', url)

        tw_files = glob.glob('./sample_input/raw-twitter-basic*.json')
        for filename in tw_files:
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

        hb_files = glob.glob('./sample_input/raw-hatena-basic*.json')
        for filename in hb_files:
            with open(filename) as file:
                for line in file:
                    row = json.loads(line)

                    hier_part = to_hier_part(row['requested_url'])
                    comments = len(list(filter(lambda x: x['comment'] != '', row['bookmarks'])))
                    cls.aggregated['summary'][hier_part]['hatena_bookmark'] = row['count']
                    cls.aggregated['summary'][hier_part]['hatena_comments'] = comments
                    count = {
                        'url': row['url'],
                        'hier_part': hier_part,
                        'service': 'hatena',
                        'metric': 'bookmark',
                        'value': row['count']
                    }
                    comments = {
                        'url': row['url'],
                        'hier_part': hier_part,
                        'service': 'hatena',
                        'metric': 'comments',
                        'value': comments
                    }
                    cls.aggregated['row'].append(count)
                    cls.aggregated['row'].append(comments)

                    for b in row['bookmarks']:
                        bookmark = dict(b, **{'url': row['url'], 'hier_part': hier_part, 'timestamp': dt.datetime.strptime(b['timestamp'], '%Y/%m/%d %H:%M').strftime('%Y-%m-%d %H:%M:%S')})
                        cls.aggregated['bookmarks'].append(bookmark)
                        for tag in b['tags']:
                            t = {'url': row['url'], 'hier_part': hier_part, 'user': b['user'], 'tag': tag}
                            cls.aggregated['tag'].append(t)

        star_files = glob.glob('./sample_input/raw-hatenastar-basic*.json')
        for filename in star_files:
            with open(filename) as file:
                for line in file:
                    row = json.loads(line)
                    hier_part = to_hier_part(row['entries'][0]['uri'])
                    star_count = len(row['entries'][0]['stars'])
                    colorstar_count = len(row['entries'][0]['colored_stars']) if 'colored_star' in row['entries'][0] else 0

                    cls.aggregated['summary'][hier_part]['hatena_star'] = star_count
                    cls.aggregated['summary'][hier_part]['hatena_colorstar'] = colorstar_count
                    star = {
                        'url': row['entries'][0]['uri'],
                        'hier_part': hier_part,
                        'service': 'hatena',
                        'metric': 'star',
                        'value': star_count
                    }
                    colorstar = {
                        'url': row['entries'][0]['uri'],
                        'hier_part': hier_part,
                        'service': 'hatena',
                        'metric': 'colorstar',
                        'value': colorstar_count
                    }
                    cls.aggregated['row'].append(colorstar)
                    cls.aggregated['row'].append(star)

                    for star in row['entries'][0]['stars']:
                        cls.aggregated['star'].append(dict(star, **{
                            'url': row['entries'][0]['uri'],
                            'hier_part': hier_part
                        }))
                    if 'colored_stars' in row['entries'][0]:
                        for colorstar in row['entries'][0]['colored_stars']:
                            cls.aggregated['star'].append(dict(star, **{
                                'url': row['entries'][0]['uri'],
                                'hier_part': hier_part
                            }))

        fb_files = glob.glob('./sample_input/raw-facebook-basic*.json')
        for filename in fb_files:
            with open(filename) as file:
                for line in file:
                    row = json.loads(line)
                    hier_part = to_hier_part(row['id'])
                    cls.aggregated['summary'][hier_part]['facebook_share'] = row['og_object']['engagement']['count']
                    count = {
                        'url': row['id'],
                        'hier_part': hier_part,
                        'service': 'facebook',
                        'metric': 'share',
                        'value': row['og_object']['engagement']['count']
                    }
                    cls.aggregated['row'].append(count)

        p_files = glob.glob('./sample_input/raw-pocket-basic*.json')
        for filename in p_files:
            with open(filename) as file:
                for line in file:
                    row = json.loads(line)
                    hier_part = to_hier_part(row['url'])
                    cls.aggregated['summary'][hier_part]['pocket_count'] = int(row['count'])
                    count = {
                        'url': row['url'],
                        'hier_part': hier_part,
                        'service': 'pocket',
                        'metric': 'count',
                        'value': int(row['count'])
                    }
                    cls.aggregated['row'].append(count)

        a_files = glob.glob('./sample_input/raw-analytics-basic*.json')
        for filename in a_files:
            with open(filename) as file:
                for line in file:
                    report = json.loads(line)

                    last7days = report['last7days']['reports'][0]['data']['rows']
                    for r in last7days:
                        hier_part = '://example.com' + re.sub(r'\?.*', '', r['dimensions'][0])
                        v = int(r['metrics'][0]['values'][0])
                        row = {
                            'hier_part': hier_part,
                            'service': 'analytics',
                            'metric': 'last7days',
                            'value': v
                        }

                        index = next((index for (index, d) in enumerate(cls.aggregated['row']) if d['hier_part'] == hier_part and d['service'] == 'analytics' and d['metric'] == 'last7days'), None)
                        if not index is None:
                            cls.aggregated['row'][index]['value'] = cls.aggregated['row'][index]['value'] + v
                        else:
                            cls.aggregated['row'].append(row)

                        if 'analytics_last7days' in cls.aggregated['summary'][hier_part]:
                            cls.aggregated['summary'][hier_part]['analytics_last7days'] = cls.aggregated['summary'][hier_part]['analytics_last7days'] + v
                        else:
                            cls.aggregated['summary'][hier_part]['analytics_last7days'] = v

                    last30days = report['last30days']['reports'][0]['data']['rows']
                    for r in last30days:
                        hier_part = '://example.com' + re.sub(r'\?.*', '', r['dimensions'][0])
                        v = int(r['metrics'][0]['values'][0])
                        row = {
                            'hier_part': hier_part,
                            'service': 'analytics',
                            'metric': 'last30days',
                            'value': v
                        }

                        index = next((index for (index, d) in enumerate(cls.aggregated['row']) if d['hier_part'] == hier_part and d['service'] == 'analytics' and d['metric'] == 'last30days'), None)
                        if not index is None:
                            cls.aggregated['row'][index]['value'] = cls.aggregated['row'][index]['value'] + v
                        else:
                            cls.aggregated['row'].append(row)

                        if 'analytics_last30days' in cls.aggregated['summary'][hier_part]:
                            cls.aggregated['summary'][hier_part]['analytics_last30days'] = cls.aggregated['summary'][hier_part]['analytics_last30days'] + v
                        else:
                            cls.aggregated['summary'][hier_part]['analytics_last30days'] = v

                    total = report['total']['reports'][0]['data']['rows']
                    for r in total:
                        hier_part = '://example.com' + re.sub(r'\?.*', '', r['dimensions'][0])
                        v = int(r['metrics'][0]['values'][0])
                        row = {
                            'hier_part': hier_part,
                            'service': 'analytics',
                            'metric': 'total',
                            'value': v
                        }

                        index = next((index for (index, d) in enumerate(cls.aggregated['row']) if d['hier_part'] == hier_part and d['service'] == 'analytics' and d['metric'] == 'total'), None)
                        if not index is None:
                            cls.aggregated['row'][index]['value'] = cls.aggregated['row'][index]['value'] + v
                        else:
                            cls.aggregated['row'].append(row)

                        if 'analytics_total' in cls.aggregated['summary'][hier_part]:
                            cls.aggregated['summary'][hier_part]['analytics_total'] = cls.aggregated['summary'][hier_part]['analytics_total'] + v
                        else:
                            cls.aggregated['summary'][hier_part]['analytics_total'] = v



    def setUp(self):
        self.aggregated = type(self).aggregated

    def tearDown(self):
        pprint('teardown-----------------------------------------------------')


    def test_basic(self):
        run(['--input=%s' % './sample_input/raw-*.json', '--output=%s.result' % './sample_output/output', '--domain=example.com'])

        with open_shards('./sample_output/' + 'output.result-summary-*-of-*') as result_file:
            lines = []
            for line in result_file:
                lines.append(eval(line))

            with self.subTest(type='summary'):
                self.assertEqual(
                    sorted(lines, key=lambda x: x['hier_part']),
                    sorted(self.aggregated['summary'].values(), key=lambda x: x['hier_part'])
                )

        with open_shards('./sample_output/' + 'output.result-row-*-of-*') as result_file:
            lines = []
            for line in result_file:
                lines.append(eval(line))

            with self.subTest(type='row'):
                self.assertEqual(
                    sorted(lines, key=lambda x: (x['hier_part'], x['service'], x['metric'])),
                    sorted(self.aggregated['row'], key=lambda x: (x['hier_part'], x['service'], x['metric']))
                )

        with open_shards('./sample_output/' + 'output.result-bookmarks-*-of-*') as result_file:
            lines = []
            for line in result_file:
                lines.append(eval(line))
            with self.subTest(type='bookmarks'):
                self.assertEqual(
                    sorted(lines, key=lambda x: (x['hier_part'], x['timestamp'])),
                    sorted(self.aggregated['bookmarks'], key=lambda x: (x['hier_part'], x['timestamp']))
                )

        with open_shards('./sample_output/' + 'output.result-tag-*-of-*') as result_file:
            lines = []
            for line in result_file:
                lines.append(eval(line))

            with self.subTest(type='tag'):
                self.assertEqual(
                    sorted(lines, key=lambda x: (x['hier_part'], x['user'], x['tag'])),
                    sorted(self.aggregated['tag'], key=lambda x: (x['hier_part'], x['user'], x['tag']))
                )

        with open_shards('./sample_output/' + 'output.result-star-*-of-*') as result_file:
            lines = []
            for line in result_file:
                lines.append(eval(line))

            with self.subTest(type='star'):
                self.assertEqual(
                    sorted(lines, key=lambda x: (x['hier_part'], x['name'])),
                    sorted(self.aggregated['star'], key=lambda x: (x['hier_part'], x['name']))
                )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
