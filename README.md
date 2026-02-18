This example implements a minimal async server in FastAPI (can handle multiple requests simulatneosuly)

`/stream_text` : This endpoint emulates behaviour of llm-server like chatgpt

`/data` : This emulates making network call to another API.


### TCP to HTTP 
HTTP builds on top of TCP. TCP is raw connection between two processes, and doesn't care about any process sending or receiving data.
However, once we establish that these two processes should use HTTP 1.1 Protocol, the rules to follow is :
Client process makes request to server (in format following HTTP standard), which the server parses and gives out response in similar format and close the connection.

### Streaming Reponse using Server-Side-Events
With an llm-server, once client asks some question, the behaviour of HTTP server to provide response in chunks.

1. **Client sends a single HTTP request** — just one `GET /stream_updates`. That's the only request the client makes.
2. **Server keeps responding in `chunks` with this headers** including `transfer-encoding: chunked` [like this](https://github.com/robinnarsinghranabhat/streaming-client-server/blob/c4dc8f3b7bac36a9e408cb5141950d18c74b9857/stream_client.py#L10) . This tells the client's HTTP processing library: "the body will arrive in pieces, don't wait for a `Content-Length` to know when you're done."

Each `yield` from server in the `event_generator` produces one `chunk response`.

NOTE : We should not that, unless server has finished sending the entire response, client can't send another request back.
This "anytime" bi-directional communication would come under something like `WebSockets` protocol. Again, at bare tcp-socket level, nothing preventing us from this bidirectional communication. But our human defined  protocols to follow.

3. **Client accumulates and reads** — it is entirely the client program's job to read these chunks. The `requests` library gives you `iter_content()` or `iter_lines()` to pull chunks one at a time. You can concatenate them, process them individually, whatever you want. The HTTP library handles the chunked encoding framing for you.

4. **Server Keeps Sending Until Buffers Are Full**

The server does **not** wait for the client to consume data before sending more.

- When the server calls `yield`, the data goes into the **server's OS-level TCP send buffer**.
- The OS transmits it over the network into the **client's OS-level TCP receive buffer**.
- The client's kernel sends back TCP ACKs (this is at TCP level. Don't take this, why is client communicating back before server even finished.), confirming receipt. The server's kernel frees the acknowledged data from its send buffer.
- **All of this happens in kernel space, independent of whether the client application is reading or not.**

So if the client is blocked (say, paused in a debugger), the data piles up in the **client machine's kernel memory**. The server app keeps going — it can still write data into its own send buffer even after the client's recv buffer is full. It's only when the server's send buffer **also** fills up (because nothing can drain to the client) that the server app finally blocks on `yield`. At maximum backpressure, data is sitting in **both** buffers — server send buffer full, client recv buffer full for that specific "client-server TCP connection".

Statement to be verified : The connection stays open the entire time. The client sent one request; the server just keeps writing to that same response until the generator is exhausted (or the client disconnects).

### How Async Enables Handling Multiple Clients

When the server is blocked on one client (their buffer is full), it doesn't freeze the whole server. Because the `response-handler` is an `async` coroutine. 
SIDE NOTE : We could design server such that incoming request would be assigned to a separate `thread` or a `process`, which is unnecessary for IO tasks (assume our llm-server as something like litellm, is again pinging highly-concurrent openai-llm ).

- The `blocked yield` suspends **only that one coroutine** (blocked yield means, at os level, `select` or `poll` system call would not mark the that `socket` file descriptor as `ready` )
- The event loop moves on to serve other clients — yielding their chunks, processing new connections, etc.
- When the blocked client's buffer frees up (they finally read some data), the event loop resumes the suspended coroutine.

This is why a single-threaded async server like uvicorn can handle many simultaneous streaming clients. Each client's handler cooperatively yields control when it can't make progress, so no one client can starve the others.
