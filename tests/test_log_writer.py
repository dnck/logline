import argparse

import time

from context import results_manager

if __name__ == "__main__":

    PARSER = argparse.ArgumentParser(description="A tester for line shipper.")
    PARSER.add_argument(
        "n",
        metavar="n",
        type=str,
        default="0",
        help="file number to simulate new log files",
    )
    ARGS = PARSER.parse_args()

    file_logger = results_manager.LogManager(
        level="debug",
        output="file",
        filename="helloworld0{}.log".format(ARGS.n))

    n = 0
    while True:
        file_logger.log.info("Hello world again! {}".format(n))
        n += 1
        time.sleep(0.1)
