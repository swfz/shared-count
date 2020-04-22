# timeseries-hatenastatus

## requirements

- pub/sub topic

```
gcloud pubsub topics create memo-timeseries-hatenastatus
```


- scheduler

dailyスケジュール

```
gcloud scheduler jobs create pubsub publish-timeseries-hatenastatus-job --schedule="2 1 * * *" --topic=memo-timeseries-hatenastatus --message-body='{"url": "https://swfz.hatenablog.com", "service": "hatenastatus"}'
```

## development

- environment

環境変数の設定が必要

| name | description |
|:-|:-|
| GOOGLE_APPLICATION_CREDENTIALS | credentialファイルのパス |
| BUCKET | テストで使用するバケット名 |

- event.json

```
{
  "url": "https://swfz.hatenablog.com",
  "service": "hatenastatus"
}
```

## deploy

BUCKETは任意のバケット名

```
cd twitter
gcloud functions deploy timeseriesHatenaStatus --trigger-topic=memo-timeseries-hatenastatus --runtime nodejs10 --region asia-northeast1 --set-env-vars BUCKET=memo-raw-data --memory=512MB
```

## publish message

```
gcloud pubsub topics publish memo-timeseries-hatenastatus --message '{"url":"https://example.com","service":"hatenastatus"}'
```
