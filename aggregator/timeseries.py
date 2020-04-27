#!/usr/bin/env python3
# coding=utf-8

import apache_beam as beam # type: ignore

import argparse
import logging
import json

from apache_beam.options.pipeline_options import PipelineOptions # type: ignore
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.io import ReadFromText # type: ignore
from apache_beam.io import WriteToText
from functools import reduce
from pprint import pprint

from modules.bq_schema import HatenaSchema, BqSchema

def merge_metrics(tpl):
    key, values = tpl

    row = {'date': key}

    merged_row = reduce(lambda a, c: dict(a, **c), values, row)
    del merged_row['service']

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
            '--dataset',
            dest='dataset',
            default='sample:sample',
            help='BigQuery. dataset')

    known_args, pipeline_args = parser.parse_known_args(argv)

    pprint(known_args.input)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

    p = beam.Pipeline(options=pipeline_options)

    result = p | 'READ' >> ReadFromText(known_args.input) \
               | 'ParseJson' >> beam.Map(lambda x: json.loads(x)) \
               | 'ExcludeNone' >> beam.Filter(lambda e: e is not None) \
               | 'PairWithDate' >> beam.Map(lambda x: (x['date'], x)) \
               | 'GroupByDate' >> beam.GroupByKey() \
               | 'Merge' >> beam.Map(merge_metrics)


    if(known_args.env == 'prod'):
        result | 'WriteSummaryToGcs' >> WriteToText(known_args.output)
        result | 'WriteSummaryToBigQuery' >> beam.io.WriteToBigQuery(
                        f'{known_args.dataset}.daily_kpi',
                        schema=BqSchema.daily_kpi,
                        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
                        )

    else:
        result | 'WriteSummaryToFile' >> WriteToText(known_args.output)

    p.run().wait_until_finish()
    pprint(vars(result))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARNING)
    run()
