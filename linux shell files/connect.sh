curl -X POST \
  http://192.168.0.11:8000/register_with \
  -H 'Content-Type: application/json' \
  -d '{"node_address": "http://192.168.0.14:8000/"}'
