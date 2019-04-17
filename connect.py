import logging

sqla_logger = logging.getLogger('sqlalchemy')
sqla_logger.propagate = False
sqla_logger.addHandler(logging.FileHandler('sqla.log'))