/**
 * Triggered from a message on a Cloud Pub/Sub topic.
 *
 * @param {!Object} event Event payload.
 * @param {!Object} context Metadata for the event.
 */

const {Storage} = require('@google-cloud/storage');
const {PubSub} = require('@google-cloud/pubsub');
const fs = require('fs');
const os = require('os');

exports.publishToCollector = async (event, context) => {
  const payload = Buffer.from(event.data, 'base64').toString();
  const params = JSON.parse(payload);

  const services = ['twitter', 'pocket', 'facebook', 'hatena'];
  const articles = await getArticles();

  const target = filterTargetArticles(articles, (new Date()).getHours());

  const pubsub = new PubSub();
  const topicPrefix = process.env['TOPIC_PREFIX'];

  for (let i = 0; i < services.length; i++) {
    const service = services[i];
    const topic = `${topicPrefix}${service}`;
    const publisher = pubsub.topic(topic, {batching: { maxMilliseconds: 10000}});

    for (let j = 0; j < target.length; j++) {
      const url = target[j].url;
      const data = {url, service};

      const dataBuffer = Buffer.from(JSON.stringify(data));
      const messageId = await publisher.publish(dataBuffer);
      console.log(`[${topic}][${url}]: Message ${messageId} published.`);
    }
  }
};

const filterTargetArticles = (articles, hour) => {
  const denominator = 24;

  const filterdArticles = articles.filter(a => !a.hasOwnProperty('platform') || a.platform == 'blog');

  const sortFn = (a,b) => {
    if(a.hasOwnProperty('updated')){
      if(a.updated < b.updated) return 1;
      if(a.updated > b.updated) return -1;
      return 0;
    }
    else {
      if (a.title < b.title) return 1;
      if (a.title > b.title) return -1;
      return 0;
    }
  }
  const sortedArticles = filterdArticles.sort(sortFn);

  const unit = Math.ceil(sortedArticles.length / denominator);
  const start = unit * hour;
  const end = start + unit;

  return sortedArticles.slice(start, end);
}

const getArticles = async () => {
  const bucketName = process.env['ARTICLES_BUCKET'];
  const fileName = process.env['ARTICLES_PATH']
  const storage = new Storage();

  await storage.bucket(bucketName).file(fileName).download({destination: `${os.tmpdir()}/articles.json`});

  const articlesJSONLines = fs.readFileSync(`${os.tmpdir()}/articles.json`, 'utf8');
  const json = `[${articlesJSONLines.replace(/\n/gi,',').replace(/,$/,'')}]`;

  return JSON.parse(json);
}
