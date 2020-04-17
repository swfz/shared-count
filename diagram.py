from diagrams import Diagram
from diagrams.gcp.storage import Storage
from diagrams.gcp.compute import Functions
from diagrams.gcp.devtools import Scheduler
from diagrams.gcp.analytics import Pubsub, Dataflow, Bigquery

with Diagram('API Data Collector'):

    schedule = Scheduler('cron "2 * * * *"')
    fn_publish = Functions('publishToCollector')
    pubsub_publisher = Pubsub('memo-collector-publish')

    gcs_rawdata = Storage('raw-data')

    fn_hatena = Functions('collectHatenaCount')
    fn_hatenastar = Functions('collectHatenaStarCount')
    fn_facebook = Functions('collectFacebookCount')
    fn_pocket = Functions('collectPocketCount')
    fn_twitter = Functions('collectTwitterCount')

    pubsub_hatena = Pubsub('memo-hatena-collector')
    pubsub_hatenastar = Pubsub('memo-hatena-collector')
    pubsub_facebook = Pubsub('memo-hatena-collector')
    pubsub_pocket = Pubsub('memo-hatena-collector')
    pubsub_twitter = Pubsub('memo-hatena-collector')

    schedule >> pubsub_publisher >> fn_publish >> gcs_rawdata
    fn_publish >> pubsub_hatena >> fn_hatena >> gcs_rawdata
    fn_publish >> pubsub_hatenastar >> fn_hatenastar >> gcs_rawdata
    fn_publish >> pubsub_facebook >> fn_facebook >> gcs_rawdata
    fn_publish >> pubsub_pocket >> fn_pocket >> gcs_rawdata
    fn_publish >> pubsub_twitter >> fn_twitter >> gcs_rawdata

with Diagram('Aggregate Share Count And Timeseries'):
    gcs_rawdata = Storage('raw-data')
    aggregator = Dataflow('aggregator')
    bq = Bigquery('blog_data.summary')

    gcs_rawdata >> aggregator >> bq

with Diagram('Collect Timeseries Hatena Status'):
    schedule = Scheduler('cron "2 2 * * *"')
    pubsub = Pubsub('memo-timeseries-hatenastatus')
    fn_timeseries_hatenastatus = Functions('timeseriesHatenaStatus')
    gcs_rawdata = Storage('raw-data')

    schedule >> pubsub >> fn_timeseries_hatenastatus >> gcs_rawdata

with Diagram('Collect Analytics Report'):
    schedule = Scheduler('cron "1 1 * * *"')
    pubsub = Pubsub('memo-collector-analytics')
    fn_analytics = Functions('collectAnalyticsReport')
    gcs_rawdata = Storage('raw-data')

    schedule >> pubsub >> fn_analytics >> gcs_rawdata

