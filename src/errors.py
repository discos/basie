"""
This module defines scheduleerror error classes,
should be imported everywhere as from errors import *
"""

class ScheduleError(Exception):
    """
    Generic error in schedulecreator package
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class ReceiverError(ScheduleError):
    """
    Error in receivers specifications
    """
    def __init__(self, *args, **kwargs):
        ScheduleError.__init__(self, *args, **kwargs)

class CoordinateError(ScheduleError):
    """
    Used when illegal operations are done with coordinates objects
    """
    def __init__(self, *args, **kwargs):
        ScheduleError.__init__(self, *args, **kwargs)

class ProcedureError(ScheduleError):
    """
    Used when illegal operations are done with procedure objects
    """
    def __init__(self, *args, **kwargs):
        ScheduleError.__init__(self, *args, **kwargs)

