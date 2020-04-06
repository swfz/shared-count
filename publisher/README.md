# publisher

記事リストをもとに各Topicへpublishするための関数

## 記事リスト

JSONLineフォーマット

```
{"title":"hoge", "url":"https://........", "updated":"2020-04-01", "platform": "blog"},
{"title":"fuga", "url":"https://........", "updated":"2020-04-02", "platform": "blog"},
```

## 準備
### Publisher

- topic

```
gcloud pubsub topics create memo-collector-publish
```

- scheduler

```
gcloud scheduler jobs create pubsub publish-job --schedule="2 * * * *" --topic=memo-collector-publish --message-body="{}"
```

## development

- environment

環境変数の設定が必要

| name | description |
|:-|:-|
| GOOGLE_APPLICATION_CREDENTIALS | credentialファイルのパス |
| ARTICLES_PATH | 記事リストのjsonのファイルパス |
| ARTICLES_BUCKET | 記事リストのjsonがあるバケット名 |
| TOPIC_RREFIX | 各サービスTopic共通のprefix |


プロジェクトに合わせて変える

```
export ARTICLES_PATH=articles/articles.json
export ARTICLES_BUCKET=memo-raw-data
export TOPIC_RREFIX=memo-collector-
npx functions-framework --target=publishToCollector --signature-type=event
```

- 確認

```
curl -XPOST -H 'Content-Type:application/json; charset=utf-8' http://localhost:8080/
```


## deploy

default 60 seconds

最大9分 → 540

```
gcloud functions deploy publishToCollector --trigger-topic=memo-collector-publish --runtime nodejs10 --region asia-northeast1 --set-env-vars ARTICLES_BUCKET=memo-raw-data,ARTICLES_PATH=articles/articles.json,TOPIC_PREFIX=memo-collector- --timeout=540
```

