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
from feedcache import cache
#
# Module
#

MAX_THREADS=5
OUTPUT_DIR='/tmp/charts/feedcache'
TTL=3600


def start_job(urls=[], max_threads=MAX_THREADS):

    if not urls:
        print 'Specify the URLs to a few RSS or Atom feeds on the command line.'
        return

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

    print 'Saving feed data to', OUTPUT_DIR
    storage = shove.Shove('file://' + OUTPUT_DIR)
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
        printer_thread = threading.Thread(target=print_entries, args=(entry_queue,))
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
    c = cache.Cache(storage, TTL)

    while True:
        next_url = input_queue.get()
        if next_url is None: # None causes thread to exit
            input_queue.task_done()
            break

        feed_data = c.fetch(next_url)
        for entry in feed_data.entries:
            output_queue.put( (feed_data.feed, entry) )
        input_queue.task_done()
    return


def print_entries(input_queue):
    """Thread target for printing the contents of the feeds.
    """
    while True:
        feed, entry = input_queue.get()
        if feed is None: # None causes thread to exist
            input_queue.task_done()
            break

        print '%s: %s' % (feed.title, entry.title)
        input_queue.task_done()
    return

