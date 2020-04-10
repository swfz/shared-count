# aggregator


## requirements
- apache_beam[gcp]


## execution

### development

- 例

各種オプションは適宜入力

```
python aggregator.py --project memo-000000 --env dev --runner DirectRunner --input './raw-*.json' --output aggregated.txt --job_name test-aggregate
```

### production

- 例

各種オプションは適宜入力

```
python aggregator.py --project memo-000000 --env prod --table memo-000000:blog_data.summary --runner DataflowRunner --temp_location gs://memo-000000/temp --input 'gs://memo-raw-data/share-count/service=*/*' --output gs://memo-000000/results/output/aggregate --job_name aggregate
```



