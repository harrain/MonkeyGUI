#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging


class Log:
    def __init__(self, level, name, filename=None):
        # create a logging object
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        # format log file
        self.formatter = logging.Formatter('%(asctime)s %(name)s-%(levelname)s: %(message)s')
        # create the logging file handler and format the log file if file_path was set.
        if filename:
            self.fh = logging.FileHandler(filename, mode='a+')
            self.fh.setFormatter(self.formatter)
            self.logger.addHandler(self.fh)
        # create logging print Stream
        self.ch = logging.StreamHandler()
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def close(self):
        self.logger.removeHandler(self.fh)
