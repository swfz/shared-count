/**
 * Triggered from a message on a Cloud Pub/Sub topic.
 *
 * @param {!Object} event Event payload.
 * @param {!Object} context Metadata for the event.
 */

const fetch = require('node-fetch');
const {Storage} = require('@google-cloud/storage');

exports.collectTwitterCount = async (event, context) => {
  console.log(event);
  const data = Buffer.from(event.data, 'base64').toString();
  const params = JSON.parse(data);
  console.log(process.env);

  const urlBase = 'http://jsoon.digitiminimi.com/twitter/count.json?url=';
  const requestUrl = `${urlBase}${params.url}`;

  const bucketName = (process.env['NODE_ENV'] == 'production') ? 'memo-raw-data' : 'dev-memo-raw-data';
  const storage = new Storage();

  const res = await fetch(requestUrl).then((res) => {
    console.log(res);
    return res.json();
  });

  console.log(res);

  const bucket = storage.bucket(bucketName);
  const file = bucket.file(`share-count/service=${params.service}/${encodeURIComponent(params.url)}`);

  await file.save(JSON.stringify(res));
};
