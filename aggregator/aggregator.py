#!/usr/bin/env python3
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

from bq_schema import HatenaSchema, BqSchema
from transform import Transform


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


class ExtractHatena(beam.DoFn):
    def process(self, element):
        if 'timestamp' in element:
            yield pvalue.TaggedOutput('bookmark', element)
        elif 'quote' in element:
            yield pvalue.TaggedOutput('star', element)
        elif 'tag' in element:
            yield pvalue.TaggedOutput('tag', element)
        elif 'metric' in element:
            yield pvalue.TaggedOutput('summary', element)


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

        rows_twitter = mixed_data.twitter | beam.FlatMap(Transform().parse_twitter)
        rows_pocket = mixed_data.pocket | beam.Map(Transform().parse_pocket)
        rows_facebook = mixed_data.facebook | beam.Map(Transform().parse_facebook)

        mixed_hatena = mixed_data.hatena | beam.FlatMap(Transform().parse_hatena)
        mixed_hatenastar = mixed_data.hatenastar | beam.FlatMap(Transform().parse_hatena_star)

        hatena = (mixed_hatena, mixed_hatenastar) \
            | 'FlattenHatenaData' >> beam.Flatten() \
            | 'ExtractHatena' >> beam.ParDo(ExtractHatena()).with_outputs()

        flattend_rows = (rows_twitter, rows_pocket, rows_facebook, hatena.summary) \
            | 'Flatten' >> beam.Flatten()

        result = flattend_rows \
            | 'PairWithUrl' >> beam.Map(lambda x: (x['url'], x)) \
            | 'GroupByUrl' >> beam.GroupByKey() \
            | 'Merge' >> beam.Map(merge_metrics)

        if(known_args.env == 'prod'):
            result | 'WriteSummaryToGcs' >> WriteToText(known_args.output)
            hatena.bookmark | 'WriteBookmarkToBigQuery' >> beam.io.WriteToBigQuery(
                            known_args.table_spec,
                            schema=BqSchema.bookmark,
                            write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                            )
            hatena.tag | 'WriteTagToBigQuery' >> beam.io.WriteToBigQuery(
                            known_args.table_spec,
                            schema=BqSchema.tag,
                            write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                            )
            hatena.tag | 'WriteStarToBigQuery' >> beam.io.WriteToBigQuery(
                            known_args.table_spec,
                            schema=BqSchema.star,
                            write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                            )
            result | 'WriteSummaryToBigQuery' >> beam.io.WriteToBigQuery(
                            known_args.table_spec,
                            schema=BqSchema.summary,
                            write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                            )
        else:
            hatena.bookmark | 'WriteBookmarkToFile' >> WriteToText(f'{known_args.output}-bookmarks')
            hatena.tag | 'WriteTagToFile' >> WriteToText(f'{known_args.output}-tag')
            hatena.star | 'WriteStarToFile' >> WriteToText(f'{known_args.output}-star')
            flattend_rows | 'WriteRowsToFile' >> WriteToText(f'{known_args.output}-row')
            result | 'WriteSummaryToFile' >> WriteToText(known_args.output)

        p.run().wait_until_finish()

        pprint(vars(result))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARNING)
    run()
