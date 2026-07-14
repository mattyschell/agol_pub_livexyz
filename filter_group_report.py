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
                  ,patterns
                  ,allow_usernames=None):

    indices = _column_indices(header
                             ,columns)

    if allow_usernames is None:
        allow_usernames = set()

    username_index = None
    try:
        username_index = header.index('username')
    except ValueError:
        pass

    email_index = None
    try:
        email_index = header.index('user.email')
    except ValueError:
        pass

    excluded = []
    for row in data_rows:
        username_value = ''
        if username_index is not None and username_index < len(row):
            username_value = row[username_index].strip().lower()

        if username_value in allow_usernames:
            continue

        matched = False
        for index in indices:
            if index >= len(row):
                value = ''
            else:
                value = row[index]

            for pattern in patterns:
                if fnmatch.fnmatch(value
                                  ,pattern):
                    matched = True
                    break

            if matched:
                break

        # Keep allowed-domain matches out of suspect output.
        if matched:
            continue

        # Blank user.email is suspect only when row did not match patterns.
        if email_index is not None:
            email_value = ''
            if email_index < len(row):
                email_value = row[email_index]
            if not email_value.strip():
                excluded.append(row)
                continue

        # Keep only rows where no checked column matches the pattern.
        excluded.append(row)

    return excluded


def _load_allow_usernames(allowlist_file):

    if allowlist_file is None:
        return set()

    usernames = set()
    with open(allowlist_file
             ,'r'
             ,encoding='utf-8') as f:
        for raw_line in f:
            value = raw_line.strip()
            if not value:
                continue
            if value.startswith('#'):
                continue
            usernames.add(value.lower())

    return usernames


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
    parser.add_argument('--patterns'
                       ,nargs='+'
                       ,default=['*nyc.gov*', '*nypd.org*']
                       ,help=(
                            'Glob patterns to exclude '
                           '(default: *nyc.gov* *nypd.org*)'))
    parser.add_argument('--allowlist-file'
                       ,default=None
                       ,help=(
                           'Optional file with usernames to suppress '
                           'from suspect output'))

    args = parser.parse_args()

    try:
        header, data_rows = _read_report(args.infile)

        if not header:
            raise ValueError(
                'Input report {0} is empty'.format(args.infile))

        allow_usernames = _load_allow_usernames(args.allowlist_file)

        excluded = _excluded_rows(header
                                 ,data_rows
                                 ,args.columns
                                 ,args.patterns
                                 ,allow_usernames)

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
