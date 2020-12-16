# aggregator


## requirements
- apache_beam[gcp]

## environment

## Deploy(GitHub Actions)

- secrets

| name | description |
|:-|:-|
| GCP_EMAIL | サービスアカウントのメールアドレス |
| GCP_KEY | サービスアカウントのキー(base64) |
| GCP_INPUT_STORAGE | eg) data -> バケット名 |
| GCP_DATAFLOW_STORAGE | eg) hoge -> バケット名 |
| GCP_PROJECT_ID | eg) hoge-000000 |

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

### dependencies
- apache-beam
- google-cloud-bigquery
- google-cloud-storage
- mypy
- green


