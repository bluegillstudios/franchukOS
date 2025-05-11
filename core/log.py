# Copyright 2025 the FranchukOS project authors. 
# Contributed under the Apache License, Version 2.0.

import logging

class Log:
    @staticmethod
    def setup(level=logging.INFO):
        logging.basicConfig(level=level, format='[%(levelname)s] %(message)s')

    @staticmethod
    def info(msg): logging.info(msg)
    @staticmethod
    def warning(msg): logging.warning(msg)
    @staticmethod
    def error(msg): logging.error(msg)
