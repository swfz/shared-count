
class HatenaSchema:
    tag = {
            'fields': [{
                'name': 'url', 'type': 'STRING', 'mode': 'REQUIRED'
            }, {
                'name': 'user', 'type': 'STRING', 'mode': 'REQUIRED'
            }, {
                'name': 'tag', 'type': 'STRING', 'mode': 'NULLABLE'
            }]
    }

    bookmak = {
            'fields': [{
                'name': 'url', 'type': 'STRING', 'mode': 'REQUIRED'
            }, {
                'name': 'user', 'type': 'STRING', 'mode': 'REQUIRED'
            }, {
                'name': 'comment', 'type': 'STRING', 'mode': 'NULLABLE'
            }, {
                'name': 'timestamp', 'type': 'DATETIME', 'mode': 'NULLABLE'
            }, {
                'name': 'tags', 'type': 'ARRAY<STRING>', 'mode': 'NULLABLE'
            }]
        }

    star = {
            'fields': [{
                'name': 'url', 'type': 'STRING', 'mode': 'REQUIRED'
            }, {
                'name': 'user', 'type': 'STRING', 'mode': 'REQUIRED'
            }, {
                'name': 'quote', 'type': 'STRING', 'mode': 'NULLABLE'
            }]
        }


class BqSchema:
    summary = {
            'fields': [{
                'name': 'url', 'type': 'STRING', 'mode': 'REQUIRED'
            }, {
                'name': 'twitter_shared', 'type': 'INT64', 'mode': 'NULLABLE'
            }, {
                'name': 'twitter_likes', 'type': 'INT64', 'mode': 'NULLABLE'
            }, {
                'name': 'pocket_count', 'type': 'INT64', 'mode': 'NULLABLE'
            }, {
                'name': 'hatena_bookmark', 'type': 'INT64', 'mode': 'NULLABLE'
            }, {
                'name': 'hatena_comments', 'type': 'INT64', 'mode': 'NULLABLE'
            }, {
                'name': 'hatena_star', 'type': 'INT64', 'mode': 'NULLABLE'
            }, {
                'name': 'hatena_colorstar', 'type': 'INT64', 'mode': 'NULLABLE'
            }, {
                'name': 'facebook_share', 'type': 'INT64', 'mode': 'NULLABLE'
            }]
        }

    row = {
            'fields': [{
                'name': 'url', 'type': 'STRING', 'mode': 'REQUIRED'
            }, {
                'name': 'service', 'type': 'STRING', 'mode': 'REQUIRED'
            }, {
                'name': 'metric', 'type': 'STRING', 'mode': 'REQUIRED'
            }, {
                'name': 'value', 'type': 'INT64', 'mode': 'NULLABLE'
            }]
        }
