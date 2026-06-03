import argparse
import csv
import fnmatch
import os
import sys
import time


def _read_report(infile):

    with open(infile
             ,'r'
             ,newline=''
               ,encoding='utf-8-sig') as f:
        rows = list(csv.reader(f))

    if not rows:
        return [], []

    return rows[0], rows[1:]


def _column_indices(header
                   ,columns):

    indices = []

    for column in columns:
        try:
            indices.append(header.index(column))
        except ValueError:
            raise ValueError(
                'Column {0} not found in report header {1}'.format(
                    column
                   ,header))

    return indices


def _excluded_rows(header
                  ,data_rows
                  ,columns
                  ,pattern):

    indices = _column_indices(header
                             ,columns)

    excluded = []
    for row in data_rows:
        matched = False
        for index in indices:
            if index >= len(row):
                value = ''
            else:
                value = row[index]

            if fnmatch.fnmatch(value
                              ,pattern):
                matched = True
                break

        # Keep only rows where no checked column matches the pattern.
        if not matched:
            excluded.append(row)

    return excluded


def _output_path(infile
                ,outdir):

    if outdir is None:
        outdir = os.path.dirname(os.path.abspath(infile))

    timestr = time.strftime('%Y%m%d-%H%M%S')

    return os.path.join(outdir
                       ,'livexyz-group-report-{0}.log'.format(timestr))


def _write_output(outfile
                 ,header
                 ,rows):

    if not rows:
        with open(outfile
                 ,'w'
                 ,encoding='utf-8') as f:
            f.write('\nNo suspect users to report\n\n')
        return

    label_width = max(len(column) for column in header)

    with open(outfile
             ,'w'
             ,encoding='utf-8') as f:
        f.write('LiveXYZ Group Report - Filtered Results\n')
        f.write('{0}\n'.format('=' * 72))
        f.write('Suspect users found: {0}\n'.format(len(rows)))
        f.write('{0}\n\n'.format('=' * 72))

        for index, row in enumerate(rows
                                   ,start=1):
            # Fill short rows so every header column prints a value.
            normalized_row = row[:len(header)] + [''] * max(
                0
               ,len(header) - len(row))

            f.write('User {0}\n'.format(index))
            f.write('{0}\n'.format('-' * 72))

            for column, value in zip(header
                                    ,normalized_row):
                safe_value = value.strip() if value else ''
                if not safe_value:
                    safe_value = '(blank)'

                f.write('{0:<{1}} : {2}\n'.format(
                    column
                   ,label_width
                   ,safe_value))

            f.write('\n')


def main():

    parser = argparse.ArgumentParser(
        description=(
            'Filter a comma-delimited group report, keeping only rows '
            'whose checked columns do not match a pattern')
    )

    parser.add_argument('infile'
                       ,help='Input comma-delimited group report csv')
    parser.add_argument('--outdir'
                       ,default=None
                       ,help='Output directory (default: infile directory)')
    parser.add_argument('--columns'
                       ,nargs='+'
                       ,default=['username', 'user.email']
                       ,help=(
                            'Columns to check '
                            '(default: username user.email)'))
    parser.add_argument('--pattern'
                       ,default='*.nyc.gov*'
                       ,help='Glob pattern to exclude (default: *.nyc.gov*)')

    args = parser.parse_args()

    try:
        header, data_rows = _read_report(args.infile)

        if not header:
            raise ValueError(
                'Input report {0} is empty'.format(args.infile))

        excluded = _excluded_rows(header
                                 ,data_rows
                                 ,args.columns
                                 ,args.pattern)

        outfile = _output_path(args.infile
                              ,args.outdir)

        _write_output(outfile
                     ,header
                     ,excluded)

        print(outfile)
    except Exception as e:
        raise ValueError(
            'Failure filtering group report {0}: {1}'.format(
                args.infile
               ,e))

    sys.exit(0)


if __name__ == '__main__':
    main()
