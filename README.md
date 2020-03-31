# shared count collector

## requirements
### GCS bucket
- 事前に作っておく
- production
    - 'memo-raw-data'
- development
    - 'dev-memo-raw-data'

### API
- Twitter
    - 事前にデータを収集するよう申請する(https://jsoon.digitiminimi.com/)

## development

- start server

```
cd twitter
npm ci
npx functions-framework --target=collectTwitterCount --signature-type=event
```

- event.json

```
{
  "url": "https://swfz.hatenablog.com/entry/2019/03/03/233624",
  "service": "twitter"
}
```

- 確認

```
curl -v -XPOST -H 'Content-Type:application/json; charset=utf-8' -d "{\"data\": {\"data\": \"$(cat event.json|base64|tr -d '\n')\"}}" http://localhost:8080/
```


## deploy

```
gcloud functions deploy collectTwitterCount --trigger-topic=memo-collector-twitter --runtime nodejs10 --region asia-northeast1
```

## publish message

```
gcloud pubsub topics publish memo-collector-twitter --message '{"url":"https://example.com","service":"twitter"}'
```

