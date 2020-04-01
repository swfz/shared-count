/**
 * Triggered from a message on a Cloud Pub/Sub topic.
 *
 * @param {!Object} event Event payload.
 * @param {!Object} context Metadata for the event.
 */

const fetch = require('node-fetch');
const {Storage} = require('@google-cloud/storage');

exports.collectFacebookCount = async (event, context) => {
  const data = Buffer.from(event.data, 'base64').toString();
  const params = JSON.parse(data);

  const urlBase = 'http://graph.facebook.com/v6.0/?id=';
  const requestUrl = `${urlBase}${params.url}&fields=og_object{engagement}`;

  const bucketName = (process.env['NODE_ENV'] == 'production') ? 'memo-raw-data' : 'dev-memo-raw-data';
  const storage = new Storage();

  const res = await fetch(requestUrl).then((res) => {
    return res.json();
  });

  console.log(res);

  const bucket = storage.bucket(bucketName);
  const file = bucket.file(`share-count/service=${params.service}/${encodeURIComponent(params.url)}`);

  await file.save(JSON.stringify(res));
};
