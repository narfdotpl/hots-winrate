def h1(text):
    return '# {}\n'.format(text)


def h2(text):
    return '\n## {}\n'.format(text)


def align_rows(rows, is_column_left_aligned=lambda i: i == 0):
    max_widths = [0] * len(rows[0])
    for row in rows:
        widths = map(len, row)
        max_widths = map(max, zip(widths, max_widths))

    lines = []
    for row in rows:
        line = ''
        for (i, (text, max_width)) in enumerate(zip(row, max_widths)):
            width = len(text)
            fill = ' ' * (max_width - width)
            if is_column_left_aligned(i):
                line += text + fill
            else:
                line += fill + text

        lines.append(line)

    return '\n'.join(lines) + '\n'
