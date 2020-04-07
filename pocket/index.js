/**
 * Triggered from a message on a Cloud Pub/Sub topic.
 *
 * @param {!Object} event Event payload.
 * @param {!Object} context Metadata for the event.
 */

const {Storage} = require('@google-cloud/storage');
const puppeteer = require('puppeteer');

exports.collectPocketCount = async (event, context) => {
  const data = Buffer.from(event.data, 'base64').toString();
  const params = JSON.parse(data);

  const browser = await puppeteer.launch({args: ['--no-sandbox', '--disable-setuid-sandbox']});
  const page = await browser.newPage();

  const requestUrl = `https://widgets.getpocket.com/v1/button?v=1&count=vertical&url=${params.url}&src=${params.url}`;

  const bucketName = process.env['BUCKET'];
  const storage = new Storage();

  await page.goto(requestUrl);
  await page.waitFor(5000);
  const count = await page.$eval('span', span => span.textContent);

  console.log(count);

  const bucket = storage.bucket(bucketName);
  const file = bucket.file(`share-count/service=${params.service}/${encodeURIComponent(params.url)}`);

  await file.save(JSON.stringify({count: count, url: params.url}));
};

