import pdpyras

# Send an event to PagerDuty
# https://developer.pagerduty.com/api-reference/368ae3d938c9e-send-an-event-to-pager-duty
# Routing Key is a unique secret that dictates endpoint used
ROUTING_KEY = 'e93facc04764012d7bfb002500d5d1a6'

events_session = pdpyras.EventsAPISession(ROUTING_KEY)
dedup_key = events_session.trigger('Status IO Status is bad', 'xyz123.status.io')
events_session.acknowledge(dedup_key)
events_session.resolve(dedup_key)

