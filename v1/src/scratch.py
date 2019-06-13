from multiprocessing import Pool, Process
import time


def f(x):
    return x*x

if __name__ == '__main__':
    start_time = time.time()
    with Pool(10) as p:
        p.map(f, range(0,100000000))

    print("--- %s seconds ---" % (time.time() - start_time))
