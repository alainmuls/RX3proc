import os
import argparse
from gfzrnx import gfzrnx_constants as gfzc

__author__ = 'amuls'

ROOTDIR = os.path.expanduser('~/RxTURP/BEGPIOS/')
P3RS2RNXDIR = os.path.expanduser('~/RxTURP/BEGPIOS/P3RS2/rinex/')
P3RS2PVTLSDIR = os.path.expanduser('~/RxTURP/BEGPIOS/P3RS2/LOG/pvt_ls/')

lst_logging_choices = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']


class logging_action(argparse.Action):
    def __call__(self, parser, namespace, log_actions, option_string=None):
        for log_action in log_actions:
            if log_action not in lst_logging_choices:
                raise argparse.ArgumentError(self, "log_actions must be in {choices!s}".format(choices=lst_logging_choices))
        setattr(namespace, self.dest, log_actions)


class year_action(argparse.Action):
    def __call__(self, parser, namespace, year, option_string=None):
        if year not in range(1000, 10000):
            raise argparse.ArgumentError(self, "year must be in [1000...9999]")
        setattr(namespace, self.dest, year)


class doy_action(argparse.Action):
    def __call__(self, parser, namespace, doy, option_string=None):
        if doy not in range(1, 366):
            raise argparse.ArgumentError(self, "day-of-year must be in [1...366]")
        setattr(namespace, self.dest, doy)


class marker_action(argparse.Action):
    def __call__(self, parser, namespace, marker, option_string=None):
        if len(marker) != 4:
            raise argparse.ArgumentError(self, "marker name must be 4 chars long")
        setattr(namespace, self.dest, marker)


class gnss_action(argparse.Action):
    def __call__(self, parser, namespace, gnsss, option_string=None):
        for gnss in gnsss:
            if gnss not in gfzc.lst_GNSSs:
                raise argparse.ArgumentError(self, 'select GNSS(s) out of {gnsss:s}'.format(gnsss='|'.join(gfzc.lst_GNSSs)))
        setattr(namespace, self.dest, gnsss)


class obstype_action(argparse.Action):
    def __call__(self, parser, namespace, obstypes, option_string=None):
        for obstype in obstypes:
            if obstype not in gfzc.lst_obstypes:
                raise argparse.ArgumentError(self, 'select obstype(s) out of {obstypes:s}'.format(obstypes='|'.join(gfzc.lst_obstypes)))
        setattr(namespace, self.dest, obstypes)


class session_action(argparse.Action):
    def __call__(self, parser, namespace, session, option_string=None):
        if not (len(session) == 1 and (session.isalpha() or int(session) in range(0, 9))):
            raise argparse.ArgumentError(self, 'session can only be a single chararcter 0..9 or a..z, A..Z')
        setattr(namespace, self.dest, session)
