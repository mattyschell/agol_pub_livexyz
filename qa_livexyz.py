# calling shell or bat must
# set AGOLPUB=<path>\agol_pub\src\py
# set PYTHONPATH=%PYTHONPATH%;%AGOLPUB%
# set NYCMAPSUSER=xxxx.xxx.xxx  (or use ArcGIS Pro auth)
# set NYCMAPSCREDS=xxxxxx
# set TARGETLOGDIR=<path to log directory>
import sys
import time
import logging
import os
import argparse
import tempfile

import organization


def _get_item(org, itemid):

    return org.gis.content.get(itemid)


def isdownloadable(item):

    try:
        with tempfile.TemporaryDirectory() as tempdir:
            downloaded = item.download(tempdir)
            if downloaded is None:
                print('none')
                return False

            if not os.path.isfile(downloaded):
                return False

        return True
    except Exception:
        return False


def rowcount(item):

    if not item.layers:
        raise ValueError('item {0} does not expose layers'.format(item.id))

    return item.layers[0].query(where='1=1'
                               ,return_count_only=True)


def isinrange(count, pminrows, pmaxrows):

    return pminrows <= count <= pmaxrows


def report(item, pminrows, pmaxrows):

    qareport = ''

    if not isdownloadable(item):
        qareport += '{0} item {1} could not be'.format(
                       os.linesep
                      ,item.id)
        qareport += ' downloaded{0}'.format(os.linesep)
        return qareport

    count = rowcount(item)

    if not isinrange(count, pminrows, pmaxrows):
        qareport += '{0} row count {1} is outside'.format(
                       os.linesep
                      ,count)
        qareport += ' expected range {0}-{1}{2}'.format(
                       pminrows
                      ,pmaxrows
                      ,os.linesep)

    return qareport


def qalogging(logfile
             ,level=logging.INFO):

    qalogger = logging.getLogger(__name__)
    qalogger.setLevel(level)
    filehandler = logging.FileHandler(logfile)
    qalogger.addHandler(filehandler)

    return qalogger


def main():

    parser = argparse.ArgumentParser(
        description='QA a hosted feature layer in ArcGIS Online'
    )

    parser.add_argument('pitemid'
                       ,help='Item id in ArcGIS Online')
    parser.add_argument('pminrows'
                       ,help='Minimum expected row count'
                       ,type=int)
    parser.add_argument('pmaxrows'
                       ,help='Maximum expected row count'
                       ,type=int)

    args = parser.parse_args()

    timestr = time.strftime('%Y%m%d-%H%M%S')

    targetlog = os.path.join(
        os.environ['TARGETLOGDIR']
       ,'qa-livexyz-{0}.log'.format(timestr)
    )

    qalogger = qalogging(targetlog)

    org = organization.Organization.from_env()

    item = _get_item(org, args.pitemid)

    if item is None:
        qalogger.error(
            'ERROR: item {0} not found{1}'.format(
                args.pitemid
               ,os.linesep)
        )
        sys.exit(1)

    retqareport = report(item, args.pminrows, args.pmaxrows)

    if retqareport.strip():
        qalogger.error('ERROR: QA check failed:{0}'.format(os.linesep))
        qalogger.error(retqareport.rstrip())
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
