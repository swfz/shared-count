/**
 * Triggered from a message on a Cloud Pub/Sub topic.
 *
 * @param {!Object} event Event payload.
 * @param {!Object} context Metadata for the event.
 */

const {Storage} = require('@google-cloud/storage');
const puppeteer = require('puppeteer');
const moment = require('moment');

exports.timeseriesHatenaStatus = async (event, context) => {
  const data = Buffer.from(event.data, 'base64').toString();
  const params = JSON.parse(data);
  const url = params.url

  const browser = await puppeteer.launch({args: ['--no-sandbox', '--disable-setuid-sandbox']});
  const page = await browser.newPage();

  const requestUrl = `${url}/about`;

  const bucketName = process.env['BUCKET'];
  const storage = new Storage();

  await page.goto(requestUrl);
  await page.waitFor(5000);
  const subscribers = await page.$eval('span.about-subscription-count', span => parseInt(span.textContent.replace('人')));
  const entries     = await page.$$eval('div.entry-content > dl > dd', list => parseInt(list.filter(dd => dd.textContent.match(/記事/))[0].textContent.replace('記事')));

  const date = moment().format('YYYY-MM-DD');

  const bucket = storage.bucket(bucketName);
  const file = bucket.file(`timeseries/service=${params.service}/${date}.json`);

  const payload = {date, url, subscribers, entries, service: params.service};

  await file.save(JSON.stringify(payload));
};

