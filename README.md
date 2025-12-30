This example implements a minimal async server in FastAPI (can handle multiple requests simulatneosuly)

`/stream_text` : This endpoint emulates behaviour of llm-server like chatgpt

`/data` : This emulates making network call to another API.


### Streaming Server Response from HTTP 
HTTP builds on top of TCP. TCP is raw connection between two processes, and doesn't care about any process sending or receiving data.
However, once we establish that these two processes should use HTTP 1.1 Protocol, the rules to follow is :
Client process makes request to server (in format following HTTP standard), which the server parses and gives out response in similar format and close the connection.

### Streaming Reponse using Server-Side-Events
Like With a llm server, once client asks some question, we can design our HTTP server to provide continously response in chunks.

Now, server keeps on responding with following header in it's response : {'transfer-encoding': 'chunked'} ( [Like this](https://github.com/robinnarsinghranabhat/streaming-client-server/blob/c4dc8f3b7bac36a9e408cb5141950d18c74b9857/stream_client.py#L10) ). 

This is a feature under HTTP protocol, which a HTTP compatible Client library understands. We should not that, unless server has finished sending the entire response, client can't send another request back.
This "anytime" bi-directional communication would come under something like `WebSockets` protocol. Again, at bare tcp-socket level, nothing preventing us from this bidirectional communication. But our human defined  protocols to follow.

### Implementation Details
Once client makes a request, `r =  requests.get(url, stream=True)`,   `stream_updates` endpoint will trigger `event_generator` to `yield` first `bytes` of data to client.
Afterwards, unless client has consumed this initial `byte` stream, server won't send any.
```python
# Suppose Server keeps yielding 8 Bytes of data `hi there` in a loop.
# On client side, only after 2 iterations, server's `event_generator` will be triggered to produce another `byte` stream. 
for chunk in r.iter_content(4): 
    print(chunk)
```
