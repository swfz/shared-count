/**
 * Triggered from a message on a Cloud Pub/Sub topic.
 *
 * @param {!Object} event Event payload.
 * @param {!Object} context Metadata for the event.
 */

const {Storage} = require('@google-cloud/storage');
const {google} = require('googleapis');
const analyticsreporting = google.analyticsreporting('v4');
const moment = require('moment');

exports.collectAnalyticsReport = async (event, context) => {
  const data = Buffer.from(event.data, 'base64').toString();
  const params = JSON.parse(data);

  const bucketName = process.env['BUCKET'];
  const storage = new Storage();
  const bucket = storage.bucket(bucketName);
  const file = bucket.file(`share-count/service=${params.service}/reports.json`);

  const res = await requestReport(params.viewId);

  await file.save(JSON.stringify(res));
};

const requestReport = async (viewId) => {
  const auth = new google.auth.GoogleAuth({
    scopes: ['https://www.googleapis.com/auth/analytics.readonly']
  });
  const authClient = await auth.getClient();

  const last7DaysRange = {
    startDate: moment().add(-8, 'days').format('YYYY-MM-DD'),
    endDate: moment().add(-1, 'days').format('YYYY-MM-DD')
  };
  const last30DaysRange = {
    startDate: moment().add(-31, 'days').format('YYYY-MM-DD'),
    endDate: moment().add(-1, 'days').format('YYYY-MM-DD')
  };
  const totalRange = {
    startDate: '2013-03-01',
    endDate: moment().add(-1, 'days').format('YYYY-MM-DD')
  };

  const generatePayload = (auth, daterange) => {
    return {
      auth: auth,
      requestBody: {
        reportRequests: {
          viewId: viewId,
          dateRanges: [daterange],
          metrics: [{expression: 'ga:pageViews'}],
          dimensions: [{name: 'ga:pagePath'}],
          pageSize: 5000
        }
      }
    }
  };

  const last7DaysRes = await analyticsreporting.reports.batchGet(generatePayload(authClient, last7DaysRange));
  const last30DaysRes = await analyticsreporting.reports.batchGet(generatePayload(authClient, last30DaysRange));
  const totalRes = await analyticsreporting.reports.batchGet(generatePayload(authClient, totalRange));

  return {
    last7days: last7DaysRes.data,
    last30days: last30DaysRes.data,
    total: totalRes.data
  };
};
