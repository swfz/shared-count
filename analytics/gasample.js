const {google} = require('googleapis');
const analytics = google.analytics('v3');
const analyticsreporting = google.analyticsreporting('v4');

const hoge = async () => {

  const auth = new google.auth.GoogleAuth({
    scopes: ['https://www.googleapis.com/auth/analytics.readonly']
  });
  const authClient = await auth.getClient();

  const projectId = await auth.getProjectId();
  console.log(projectId);
  const result = await analytics.data.ga.get({
    auth: authClient,
    ids: 'ga:xxxxxx',
    'start-date': '30daysAgo',
    'end-date': 'yesterday',
    metrics: 'ga:pageViews',
    dimensions: 'ga:pagePath',
    'max-results': 5000
  })
  console.log(result.data.rows);
}

// hoge()

const fuga = async () => {
  const auth = new google.auth.GoogleAuth({
    scopes: ['https://www.googleapis.com/auth/analytics.readonly']
  });
  const authClient = await auth.getClient();

  const projectId = await auth.getProjectId();
  console.log(projectId);
  const res = await analyticsreporting.reports.batchGet({
    auth: authClient,
    requestBody: {
      reportRequests: [
        {
          viewId: 'ga:xxxxxxx',
          dateRanges: [
            {
              startDate: "2020-03-15",
              endDate: "2020-04-15"
            }
          ],
          metrics: [{expression: 'ga:pageViews'}],
          dimensions: [{name: 'ga:pagePath'}],
          pageSize: 5000
        }
      ]
    }
  })
  console.log(res.data.reports[0].data.rows);

  res.data.reports[0].data.rows.forEach(row => {
    console.log(row.dimensions[0])
    console.log(row.metrics[0].values[0])
  });

  const json = JSON.stringify(
  res.data.reports[0]
  )

  console.log(json);
}

fuga()






