#-*- coding: utf-8 -*-

import warnings
import argparse
import threading

import lottecinema
import cgv

warnings.filterwarnings("ignore")

sites = []
FLAGS = None

def run_crawling():
    for site in sites:
        site.start()

    threading.Timer(FLAGS.second, run_crawling).start()

if __name__ == "__main__":

    # argparse를 사용하여 파라미터 정의
    parser = argparse.ArgumentParser()

    # 실행주기
    parser.add_argument(
        '--second',
        type=int,
        default=60,
        help='loop time',
    )

    # 크롬으로 실행여부
    parser.add_argument(
        '--chrome',
        default=False,
        help='If true, uses Chrome driver',
        action='store_true'
    )

    FLAGS, unparsed = parser.parse_known_args()

    sites.append(lottecinema.Lottecinema(FLAGS))
    sites.append(cgv.Cgv(FLAGS))

    print('------ 크롤링을 시작합니다. -------')
    print('크롤링 사이트 갯수: %d' % len(sites))

    run_crawling()