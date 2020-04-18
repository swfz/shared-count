from pprint import pprint
import datetime as dt
import re
from functools import reduce


class Transform:
    def parse_hatena(self, element):
        url = re.sub(r'^http[s]?', '', element['requested_url'])
        def transform(row):
            return dict(row, **{
                'url': url,
                'timestamp': dt.datetime.strptime(row['timestamp'], '%Y/%m/%d %H:%M').strftime('%Y-%m-%d %H:%M:%S')
            })

        bookmarks = map(transform, element['bookmarks'])
        comments = len(list(filter(lambda row: row['comment'] != '', element['bookmarks'])))

        tags = []

        for b in element['bookmarks']:
            for t in b['tags']:
                tags.append({
                    'url': url,
                    'user': b['user'],
                    'tag': t
                })

        summary = [{
            'url': url,
            'service': 'hatena',
            'metric': 'bookmark',
            'value': element['count']
        }, {
            'url': url,
            'service': 'hatena',
            'metric': 'comments',
            'value': comments
        }]

        return list(bookmarks) + tags + summary

    def parse_hatena_star(self, element):
        url = re.sub(r'^http[s]?', '', element['entries'][0]['uri'])

        stars = map(lambda row: dict(row, **{'url': url}), element['entries'][0]['stars'])

        star = len(element['entries'][0]['stars']) if 'stars' in element['entries'][0] else 0
        colored = len(element['entries'][0]['colored_stars']) if 'colored_stars' in element['entries'][0] else 0

        summary = [{
            'url': url,
            'service': 'hatena',
            'metric': 'star',
            'value': star,
        }, {
            'url': url,
            'service': 'hatena',
            'metric': 'colorstar',
            'value': colored,
        }]

        return list(stars) + summary

    def parse_facebook(self, element):
        url = re.sub(r'^http[s]?', '', element['id'])
        value = element['og_object']['engagement']['count'] if 'og_object' in element else 0

        return {
            'url': url,
            'service': 'facebook',
            'metric': 'share',
            'value': value
        }

    def parse_pocket(self, element):
        url = re.sub(r'^http[s]?', '', element['url'])
        return {
            'url': url,
            'service': 'pocket',
            'metric': 'count',
            'value': int(element['count'])
        }

    def parse_twitter(self, element):
        url = re.sub(r'^http[s]?', '', element['url'])
        return [{
            'url': url,
            'service': 'twitter',
            'metric': 'shared',
            'value': element['count'],
        }, {
            'url': url,
            'service': 'twitter',
            'metric': 'likes',
            'value': element['likes'],
        }]

    def parse_analytics(self, element):
        domain = '://swfz.hatenablog.com'

        def transform(row):
            return {
                'url': domain + roundPath(row['dimensions'][0]),
                'value': int(row['metrics'][0]['values'][0]),
            }

        def roundPath(dimension):
            return re.sub(r'\?.*', '', dimension)

        def merge_row(acc, row):
            transformed = transform(row)
            key = transformed['url']

            if key in acc:
                value = acc[key]['value'] + transformed['value']
                acc[key].update({'value': value})
            else:
                acc[key] = {'url': key, 'value': transformed['value']}

            return acc

        def format_values(range, rows):
            return map(lambda x: dict(x, **{'service': 'analytics', 'metric': range}), rows)

        last7days_by_path = reduce(merge_row, element['last7days']['reports'][0]['data']['rows'], {})
        formatted_last7days = format_values('last7days', last7days_by_path.values())

        last30days_by_path = reduce(merge_row, element['last30days']['reports'][0]['data']['rows'], {})
        formatted_last30days = format_values('last30days', last30days_by_path.values())

        total_by_path = reduce(merge_row, element['total']['reports'][0]['data']['rows'], {})
        formatted_total = format_values('total', total_by_path.values())

        return list(formatted_last7days) + list(formatted_last30days) + list(formatted_total)
