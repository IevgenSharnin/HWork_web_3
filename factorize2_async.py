from time import time
from multiprocessing import cpu_count
import concurrent.futures
import logging

def factorize(*number):
    set_list_wo_remain = []
    for each_number in number:
        list_wo_remain = []
        for each in range (1,each_number+1):
            if each_number%each == 0:
                list_wo_remain.append (each)
        set_list_wo_remain.append (list_wo_remain)
    return set_list_wo_remain 

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    numbers = [128, 255, 99999, 10651060, 106510601]
    start = time()
    with concurrent.futures.ThreadPoolExecutor(max_workers = cpu_count()) as executor:
        results = list (executor.map (factorize, numbers))
    for i in results:
        logging.debug (i)

    finish = time()
    print (f'Час роботи: {round(finish - start, 3)} сек')
