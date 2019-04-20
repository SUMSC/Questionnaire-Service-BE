import logging


class api_log:
    def mutation(self, log: str):
        logging.info("[Mutations] {}".format(log))
