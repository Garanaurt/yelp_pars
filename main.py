import multiprocessing
import time
import redis
from redis import Redis
from rq.worker import Worker
from rq import Queue
from worker import get_info
from urls_list import get_urls
import time


yelp_url = 'https://www.yelp.ca/search?find_desc=Day+Spas&find_loc=vancouver%2C+BC'

num_processes = 3



def run_worker(queue):
    redis_conn = Redis(host='localhost', port=6379)
    worker = Worker(queue, connection=redis_conn)
    worker.work(burst=True)


def main():


    try:
        redis_conn = redis.Redis(host='localhost', port=6379)
        redis_conn.ping()
        print("Redis сервер доступен.")
    except redis.ConnectionError:
        print("Не удалось подключиться к Redis серверу.")


    start_time = time.time()
    biz_links = get_urls(yelp_url)
    queue = Queue(connection=redis_conn)

    for link in biz_links:
        queue.enqueue(get_info, link)

    num_workers = num_processes
    processes = []
    for _ in range(num_workers):
        proces = multiprocessing.Process(target=run_worker, args=(queue,))
        processes.append(proces)
        proces.start()

    for process in processes:
        process.join()
    

 

    queue.empty()

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Программа выполнена за: {execution_time} секунд")


main()

