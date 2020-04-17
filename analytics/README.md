# analytics

## requirements

- pub/sub topic

```
gcloud pubsub topics create memo-collector-analytics
```


- scheduler

dailyスケジュール

```
gcloud scheduler jobs create pubsub publish-collector-analytics-job --schedule="1 1 * * *" --topic=memo-collector-analytics --message-body='{"url": "https://swfz.hatenablog.com", "service": "analytics"}'
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
  "service": "analytics",
  "viewId": "ga:xxxxx"
}
```

## deploy

BUCKETは任意のバケット名

```
cd analytics
gcloud functions deploy collectAnalyticsReport --trigger-topic=memo-collector-analytics --runtime nodejs10 --region asia-northeast1 --set-env-vars BUCKET=memo-raw-data
```

## publish message

```
gcloud pubsub topics publish memo-collector-analytics --message '{"url":"https://example.com","service":"analytics","viewId":"ga:xxxxx"}'
```
