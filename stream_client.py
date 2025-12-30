import requests

url = "http://127.0.0.1:8000/stream_updates"
url_db = "http://127.0.0.1:8000/data"

s =  requests.get(url_db, stream=False)
r=  requests.get(url, stream=True)

# print(r.headers)
# {'date': 'Tue, 30 Dec 2025 01:13:14 GMT', 'server': 'uvicorn', 'content-type': 'text/event-stream; charset=utf-8', 'transfer-encoding': 'chunked'}

# print(s.headers)
# {'date': 'Tue, 30 Dec 2025 01:13:05 GMT', 'server': 'uvicorn', 'content-length': '44', 'content-type': 'application/json'}


# This Would waits for \n in the response. otherwise blocked
# for chunk in r.iter_lines(2): 


# Better for llm purpose ..
for chunk in r.iter_content(2): 
    print(chunk)

# Making curl request
# curl http://127.0.0.1:8000/stream_updates -i --raw





