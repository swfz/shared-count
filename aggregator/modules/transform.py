from pprint import pprint


class Transform:
    def parse_hatena(self, element):
        bookmarks = map(lambda row: dict(row, **{'url': element['requested_url']}), element['bookmarks'])
        comments = len(list(filter(lambda row: row['comment'] != '', element['bookmarks'])))

        tags = []

        for b in element['bookmarks']:
            for t in b['tags']:
                tags.append({
                    'url': element['requested_url'],
                    'user': b['user'],
                    'tag': t
                    })

        summary = [{
                'url': element['requested_url'],
                'service': 'hatena',
                'metric': 'bookmark',
                'value': element['count']
            }, {
                'url': element['requested_url'],
                'service': 'hatena',
                'metric': 'comments',
                'value': comments
            }]

        return list(bookmarks) + tags + summary

    def parse_hatena_star(self, element):
        url = element['entries'][0]['uri']

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
        value = element['og_object']['engagement']['count'] if 'og_object' in element else 0

        return {
                'url': element['id'],
                'service': 'facebook',
                'metric': 'share',
                'value': value
                }

    def parse_pocket(self, element):
        return {
                'url': element['url'],
                'service': 'pocket',
                'metric': 'count',
                'value': element['count']
                }

    def parse_twitter(self, element):
        return [{
                'url': element['url'],
                'service': 'twitter',
                'metric': 'shared',
                'value': element['count'],
                }, {
                'url': element['url'],
                'service': 'twitter',
                'metric': 'likes',
                'value': element['likes'],
                }]




