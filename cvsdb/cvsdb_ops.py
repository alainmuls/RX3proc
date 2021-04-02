import sys
import os
from termcolor import colored
import logging
from tempfile import mkstemp
from shutil import move, copymode

__author__ = 'amuls'


def cvsdb_open(cvsdb_name: str, logger: logging.Logger = None):
    """
    cvsdb_open opens (or creates the database file for storing statistics on daily basis.
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    if logger is not None:
        logger.info('{func:s}: Creating / Opening database file {file:s}'.format(func=cFuncName, file=colored(cvsdb_name, 'green')))

    if not os.path.exists(cvsdb_name):
        open(cvsdb_name, 'w').close()


def cvsdb_update_line(cvsdb_name: str, line_data: str, id_fields: int, logger: logging.Logger = None):
    """
    cvsdb_update_line updates a line in the database, when the line exists it will be replaced, else it will be added.
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    logger.info('{func:s}: Updating database file {file:s}'.format(func=cFuncName, file=colored(cvsdb_name, 'green')))

    # update is set to false, we first search if this line is already existing
    cvsdb_updated = False

    # Create temp file
    fd, abs_path = mkstemp()

    with os.fdopen(fd, 'w') as fout:
        with open(cvsdb_name, 'r') as fin:
            for line in fin:
                if line.rstrip().startswith(','.join(map(str, line_data[:id_fields]))):
                    fout.write(','.join(map(str, line_data)) + '\n')
                    cvsdb_updated = True
                else:
                    fout.write(line)

        # if update has not happened, than add the line to the database
        if not cvsdb_updated:
            fout.write(','.join(map(str, line_data)) + '\n')

    # Copy the file permissions from the old file to the new file
    copymode(cvsdb_name, abs_path)

    # Remove original file
    os.remove(cvsdb_name)

    # Move new file
    move(abs_path, cvsdb_name)


# def cvsdb_update_list(cvsdb_name: str, lst_data: list, id_fields: int, logger: logging.Logger):
#     """
#     cvsdb_update_list updates a line in the database, when the line exists it will be replaced, else it will be added
#     """
#     cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

#     logger.info('{func:s}: Updating database file {file:s}'.format(func=cFuncName, file=colored(cvsdb_name, 'green')))

#     # update is set to false, we first search if this line is already existing
#     cvsdb_updated = [False] * len(lst_data)
#     print('cvsdb_updated = {}'.format(cvsdb_updated))

#     # Create temp file
#     fd, abs_path = mkstemp()

#     with os.fdopen(fd, 'w') as fout:
#         with open(cvsdb_name, 'r') as fin:
#             for line in fin:
#                 for i, line_data in enumerate(lst_data):
#                     if line.rstrip().startswith(','.join(map(str, line_data[:id_fields]))):
#                         fout.write(','.join(map(str, line_data)) + '\n')
#                         cvsdb_updated[i] = True
#                     else:
#                         fout.write(line)

#             # if update has not happened, than add the line to the database
#             for i, line_data in enumerate(lst_data):
#                 if not cvsdb_updated[i]:
#                     # print('adding line_data {:s}'.format(line_data))
#                     fout.write(','.join(map(str, line_data)) + '\n')

#     # Copy the file permissions from the old file to the new file
#     copymode(cvsdb_name, abs_path)

#     # Remove original file
#     os.remove(cvsdb_name)

#     # Move new file
#     move(abs_path, cvsdb_name)


def cvsdb_sort(cvsdb_name: str, logger: logging.Logger):
    """
    cvsdb_sort sorts the database.
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    logger.info('{func:s}: Sorting database file {file:s}'.format(func=cFuncName, file=colored(cvsdb_name, 'green')))

    # Create temp file
    fd, abs_path = mkstemp()

    # sort database lines
    with open(cvsdb_name, 'r') as fin:
        lines = fin.readlines()
    lines.sort()

    with os.fdopen(fd, 'w') as fout:
        fout.writelines(lines)

    # Copy the file permissions from the old file to the new file
    copymode(cvsdb_name, abs_path)

    # Remove original file
    os.remove(cvsdb_name)

    # Move new file
    move(abs_path, cvsdb_name)
