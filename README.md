

## twitter
## pocket
## facebook


## development

- start server

```
cd twitter
npm ci
npx functions-framework --target=getTwitterCount --signature-type=event
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
curl -v -XPOST -H 'Content-Type:application/json; charset=utf-8' -d "{\"data\": \"$(cat event.json|base64|tr -d '\n')\"}" http://localhost:8080/
```


## deploy


```
gcloud functions deploy
```
