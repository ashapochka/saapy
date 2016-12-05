# coding=utf-8
from concurrent.futures import ThreadPoolExecutor, wait
from time import sleep


def test_wait_for_all():
    def f(sleep_time: int):
        sleep(sleep_time)
        return sleep_time

    def calc(fs):
        fs_done = wait(fs).done
        r = sum(r.result() for r in fs_done)
        return r

    pool = ThreadPoolExecutor()
    fs = [pool.submit(f, arg) for arg in (3, 2, 5)]
    result = pool.submit(calc, fs).result()
    assert result == 10
