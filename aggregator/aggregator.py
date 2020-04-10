#!/usr/bin/env python
# coding=utf-8

import apache_beam as beam

import argparse
import logging
import json

from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from functools import reduce
from pprint import pprint
from apache_beam import pvalue

class ExtractService(beam.DoFn):

    def process(self, element):

        if 'likes' in element:
            yield pvalue.TaggedOutput('twitter', element)
        elif 'eid' in element:
            yield pvalue.TaggedOutput('hatena', element)
        elif 'entries' in element and len(element['entries']) > 0:
            yield pvalue.TaggedOutput('hatenastar', element)
        elif len(element) == 2 and 'count' in element:
            yield pvalue.TaggedOutput('pocket', element)
        elif 'og_object' in element:
            yield pvalue.TaggedOutput('facebook', element)


def parse_twitter(element):
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


def parse_pocket(element):
    return {
            'url': element['url'],
            'service': 'pocket',
            'metric': 'count',
            'value': element['count']
            }


def parse_facebook(element):
    value = element['og_object']['engagement']['count'] if 'og_object' in element else 0

    return {
            'url': element['id'],
            'service': 'facebook',
            'metric': 'share',
            'value': value
            }


# comment, tagsもどこかで派生させて保存する
def parse_hatena(element):
    return {
            'url': element['requested_url'],
            'service': 'hatena',
            'metric': 'bookmark',
            'value': element['count']
            }


# nameもどっかに派生させる
def parse_hatena_star(element):
    pprint(element)

    star = len(element['entries'][0]['stars']) if 'stars' in element['entries'][0] else 0
    colored = len(element['entries'][0]['colored_stars']) if 'colored_stars' in element['entries'][0] else 0
    return [{
            'url': element['entries'][0]['uri'],
            'service': 'hatena',
            'metric': 'star',
            'value': star,
            }, {
            'url': element['entries'][0]['uri'],
            'service': 'hatena',
            'metric': 'colorstar',
            'value': colored,
            }]


def get_data_schema():
    return {
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
                'name': 'hatena_star', 'type': 'INT64', 'mode': 'NULLABLE'
            }, {
                'name': 'hatena_colorstar', 'type': 'INT64', 'mode': 'NULLABLE'
            }, {
                'name': 'facebook_share', 'type': 'INT64', 'mode': 'NULLABLE'
            }]
        }


def merge_metrics(tpl):
    key, values = tpl

    row = {'url': key}

    def calc(acc, cur):
        key = cur['service'] + '_' + cur['metric']
        acc.update({key: cur['value']})

        return acc

    merged_row = reduce(calc, values, row)

    return merged_row


def run(argv=None, save_main_session=True):
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--input',
            dest='input',
            default='gs://dataflow-samples/shakespeare/kinglear.txt',
            help='Input file to process.')
    parser.add_argument(
            '--output',
            dest='output',
            default='gs://YOUR_OUTPUT_BUCKET/AND_OUTPUT_PREFIX',
            help='Output file to write results to.')
    parser.add_argument(
            '--env',
            dest='env',
            default='dev',
            help='execution environment.')
    parser.add_argument(
            '--table',
            dest='table_spec',
            default='sample:sample.sample',
            help='BigQuery. table')

    known_args, pipeline_args = parser.parse_known_args(argv)

    pprint(known_args.input)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    with beam.Pipeline(options=pipeline_options) as p:

        mixed_data = p | 'READ' >> ReadFromText(known_args.input) \
                       | 'ParseJson' >> beam.Map(lambda x: json.loads(x)) \
                       | 'ExcludeNone' >> beam.Filter(lambda e: e is not None) \
                       | 'DivideService' >> beam.ParDo(ExtractService()).with_outputs()

        rows_twitter = mixed_data.twitter | beam.FlatMap(parse_twitter)
        rows_pocket = mixed_data.pocket | beam.Map(parse_pocket)
        rows_facebook = mixed_data.facebook | beam.Map(parse_facebook)
        rows_hatena = mixed_data.hatena | beam.Map(parse_hatena)
        rows_hatenastar = mixed_data.hatenastar | beam.FlatMap(parse_hatena_star)

        result = (rows_twitter, rows_pocket, rows_facebook, rows_hatena, rows_hatenastar) \
            | 'Flatten' >> beam.Flatten() \
            | 'PairWithUrl' >> beam.Map(lambda x: (x['url'], x)) \
            | 'GroupByUrl' >> beam.GroupByKey() \
            | 'Merge' >> beam.Map(merge_metrics)

        if(known_args.env == 'prod'):
            table_schema = get_data_schema()

            result | 'WriteTextToGcs' >> WriteToText(known_args.output)
            result | 'WriteTextToBigQuery' >> beam.io.WriteToBigQuery(
                            known_args.table_spec,
                            schema=table_schema,
                            write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                            )
        else:
            result | 'WriteTextToFile' >> WriteToText(known_args.output)

        p.run().wait_until_finish()

        pprint(vars(result))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARNING)
    run()
