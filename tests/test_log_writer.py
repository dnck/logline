import time

from prometheus_exporter import results_manager


file_logger = results_manager.LogManager(
    level="debug", output="file", filename="helloworld.log")

while True:
    file_logger.log.info("Hello world!")
    time.sleep(0.1)
