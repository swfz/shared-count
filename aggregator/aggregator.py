#!/usr/bin/env python3
# coding=utf-8

import apache_beam as beam # type: ignore

import argparse
import logging
import json
import re

from apache_beam.options.pipeline_options import PipelineOptions # type: ignore
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.io import ReadFromText # type: ignore
from apache_beam.io import WriteToText
from functools import reduce
from pprint import pprint
from apache_beam import pvalue

from modules.bq_schema import HatenaSchema, BqSchema
from modules.transform import Transform


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
        elif 'last7days' in element:
            yield pvalue.TaggedOutput('analytics', element)


class ExtractHatena(beam.DoFn):
    def process(self, element):
        if 'tags' in element:
            yield pvalue.TaggedOutput('bookmark', element)
        elif 'timestamp' in element:
            yield pvalue.TaggedOutput('comment', element)
        elif 'quote' in element:
            yield pvalue.TaggedOutput('star', element)
        elif 'tag' in element:
            yield pvalue.TaggedOutput('tag', element)
        elif 'metric' in element:
            yield pvalue.TaggedOutput('summary', element)


def merge_metrics(tpl):
    key, values = tpl

    row = {'hier_part': key}

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
            '--domain',
            dest='domain',
            default='example.com',
            help='target metric domain.')
    parser.add_argument(
            '--dataset',
            dest='dataset',
            default='sample:sample',
            help='BigQuery. dataset')

    known_args, pipeline_args = parser.parse_known_args(argv)

    pprint(known_args.input)
    pprint(f'start aggregate {known_args.domain}. metrics')

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

    transformer = Transform(domain=known_args.domain)
    p = beam.Pipeline(options=pipeline_options)

    mixed_data = p | 'READ' >> ReadFromText(known_args.input) \
                   | 'ParseJson' >> beam.Map(lambda x: json.loads(x)) \
                   | 'ExcludeNone' >> beam.Filter(lambda e: e is not None) \
                   | 'DivideService' >> beam.ParDo(ExtractService()).with_outputs()

    rows_twitter = mixed_data.twitter | beam.FlatMap(transformer.parse_twitter)
    rows_pocket = mixed_data.pocket | beam.Map(transformer.parse_pocket)
    rows_facebook = mixed_data.facebook | beam.Map(transformer.parse_facebook)
    rows_analytics = mixed_data.analytics | beam.FlatMap(transformer.parse_analytics)

    mixed_hatena = mixed_data.hatena | beam.FlatMap(transformer.parse_hatena)
    mixed_hatenastar = mixed_data.hatenastar | beam.FlatMap(transformer.parse_hatena_star)

    hatena = (mixed_hatena, mixed_hatenastar) \
        | 'FlattenHatenaData' >> beam.Flatten() \
        | 'ExtractHatena' >> beam.ParDo(ExtractHatena()).with_outputs()

    flattend_rows = (rows_twitter, rows_pocket, rows_facebook, hatena.summary, rows_analytics) \
        | 'Flatten' >> beam.Flatten()

    result = flattend_rows \
        | 'PairWithUrl' >> beam.Map(lambda x: (x['hier_part'], x)) \
        | 'GroupByUrl' >> beam.GroupByKey() \
        | 'Merge' >> beam.Map(merge_metrics)

    if(known_args.env == 'prod'):
        result | 'WriteSummaryToGcs' >> WriteToText(known_args.output)
        hatena.bookmark | 'WriteBookmarkToBigQuery' >> beam.io.WriteToBigQuery(
                        f'{known_args.dataset}.bookmark',
                        schema=HatenaSchema.bookmark,
                        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                        )
        hatena.comment | 'WriteCommentToBigQuery' >> beam.io.WriteToBigQuery(
                        f'{known_args.dataset}.comment',
                        schema=HatenaSchema.comment,
                        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                        )
        hatena.tag | 'WriteTagToBigQuery' >> beam.io.WriteToBigQuery(
                        f'{known_args.dataset}.tag',
                        schema=HatenaSchema.tag,
                        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                        )
        hatena.star | 'WriteStarToBigQuery' >> beam.io.WriteToBigQuery(
                        f'{known_args.dataset}.star',
                        schema=HatenaSchema.star,
                        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                        )
        result | 'WriteSummaryToBigQuery' >> beam.io.WriteToBigQuery(
                        f'{known_args.dataset}.summary',
                        schema=BqSchema.summary,
                        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                        )
        flattend_rows | 'WriteRowToBigQuery' >> beam.io.WriteToBigQuery(
                        f'{known_args.dataset}.row',
                        schema=BqSchema.row,
                        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                        )
    else:
        hatena.bookmark | 'WriteBookmarkToFile' >> WriteToText(f'{known_args.output}-bookmarks')
        hatena.comment | 'WriteCommentToFile' >> WriteToText(f'{known_args.output}-comments')
        hatena.tag | 'WriteTagToFile' >> WriteToText(f'{known_args.output}-tag')
        hatena.star | 'WriteStarToFile' >> WriteToText(f'{known_args.output}-star')
        flattend_rows | 'WriteRowsToFile' >> WriteToText(f'{known_args.output}-row')
        result | 'WriteSummaryToFile' >> WriteToText(f'{known_args.output}-summary')

    p.run().wait_until_finish()

    pprint(vars(result))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARNING)
    run()
