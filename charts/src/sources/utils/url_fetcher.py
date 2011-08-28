#######################################################################
# Fetch Feeds
#
# Given a list of urls to feeds, fetch them and cache them with feed cache
#
# Copyright 2011 Casey Link <unnamedrambler@gmail.com>
#
# This code is based off example_threads.py from the feedcache package
# and is Copyright 2007 Doug Hellmann.
# See LICENSE.feedcache for licensing information


#
# Import system modules
#
import Queue
import sys
import shove
import threading
import httplib2
from httpcache import HttpCache

#
# local modules
#
from cache import MAX_THREADS, TTL, httpstorage


def start_job(urls, process_func, storage = None, max_threads=MAX_THREADS):

    # Decide how many threads to start
    num_threads = min(len(urls), max_threads)

    # Add the URLs to a queue
    url_queue = Queue.Queue()
    for url in urls:
        url_queue.put(url)

    # Add poison pills to the url queue to cause
    # the worker threads to break out of their loops
    for i in range(num_threads):
        url_queue.put(None)

    # Track the entries in the feeds being fetched
    entry_queue = Queue.Queue()

    if storage is None:
        storage = httpstorage

    try:

        # Start a few worker threads
        worker_threads = []
        for i in range(num_threads):
            t = threading.Thread(target=fetch_urls,
                                 args=(storage, url_queue, entry_queue,))
            worker_threads.append(t)
            t.setDaemon(True)
            t.start()

        # Start a thread to print the results
        printer_thread = threading.Thread(target=process_response, args=(entry_queue,process_func))
        printer_thread.setDaemon(True)
        printer_thread.start()

        # Wait for all of the URLs to be processed
        url_queue.join()

        # Wait for the worker threads to finish
        for t in worker_threads:
            t.join()

        # Poison the print thread and wait for it to exit
        entry_queue.put((None,None))
        entry_queue.join()
        printer_thread.join()

    finally:
        storage.close()
    return


def fetch_urls(storage, input_queue, output_queue):
    """Thread target for fetching feed data.
    """
    h = httplib2.Http(HttpCache(storage))

    while True:
        next_url = input_queue.get()
        if next_url is None: # None causes thread to exit
            input_queue.task_done()
            break

        resp, content = h.request(next_url, 'GET')

        output_queue.put( (resp, content) )
        input_queue.task_done()
    return


def process_response(input_queue, process_func):
    """Thread target for processing the resposnes.
    """
    while True:
        resp, content = input_queue.get()
        if resp is None: # None causes thread to exit
            input_queue.task_done()
            break

        process_func(resp, content)
        input_queue.task_done()
    return

