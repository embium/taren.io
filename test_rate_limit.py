import urllib.request
import urllib.error
import threading
import time
import json

# To test the global rate limit (100/minute)
GLOBAL_URL = "http://localhost:8000/health"
GLOBAL_REQUESTS = 150

# To test the specific /reddit/jobs rate limit (5/minute), you will need a valid JWT token
JOBS_URL = "http://localhost:8000/reddit/jobs"
JOBS_REQUESTS = 10
AUTH_TOKEN = "YOUR_JWT_TOKEN_HERE"


def test_endpoint(url, method="GET", num_requests=10, token=None, body=None):
    print(f"\n--- Testing {url} with {num_requests} requests ---")

    def make_request(i):
        try:
            req = urllib.request.Request(url, method=method)
            if token:
                req.add_header("Authorization", f"Bearer {token}")
            if body:
                req.add_header("Content-Type", "application/json")
                req.data = json.dumps(body).encode("utf-8")

            response = urllib.request.urlopen(req)
            print(f"[{i+1:03d}] Status: {response.status}")
        except urllib.error.HTTPError as e:
            print(
                f"[{i+1:03d}] Status: {e.code} (Rate Limited!)"
                if e.code == 429
                else f"[{i+1:03d}] Status: {e.code}"
            )
        except Exception as e:
            print(f"[{i+1:03d}] Error: {e}")

    threads = []
    for i in range(num_requests):
        t = threading.Thread(target=make_request, args=(i,))
        threads.append(t)
        t.start()
        # Sleep a tiny bit to avoid client-side socket exhaustion all at the exact same millisecond
        time.sleep(0.02)

    for t in threads:
        t.join()


if __name__ == "__main__":
    # Test 1: Fire 110 requests at the global /health endpoint (limit is 100/min)
    test_endpoint(GLOBAL_URL, num_requests=GLOBAL_REQUESTS)

    # Test 2: Fire 10 requests at the specific /reddit/jobs endpoint (limit is 5/min)
    # UNCOMMENT the lines below and add your JWT token to test this endpoint

    # dummy_body = {
    #     "subreddits": ["test"],
    #     "scrape_limit": 5
    # }
    # test_endpoint(JOBS_URL, method="POST", num_requests=JOBS_REQUESTS, token=AUTH_TOKEN, body=dummy_body)
