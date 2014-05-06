"""Chart url generator."""
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from GChartWrapper import Encoder
from GChartWrapper import VerticalBarStack


def encodedata(self, data):
    """Monkey-patched version of encodedata that supports negative values.

    Not sure why, but the unpatched version filters out values smaller
    than -1. Google Image Charts, however, is able to handle negative
    floating point values (its most recent incarnation is, at least).

    NB: Google's Image Charts has been officially deprecated as of
    April 20, 2012.

    """
    sub_data = []
    for value in data:
        if value in (None, 'None'):
            sub_data.append(self.codeset['none'])
        elif isinstance(value, str):
            sub_data.append(value)
        else:
            try:
                sub_data.append(self.codeset['value'](self.scalevalue(value)))
            except:
                raise ValueError('cannot encode value: %s' % value)
    return self.codeset['dchar'].join(sub_data)

Encoder.encodedata = encodedata

SORT_ORDER_ASC = 'asc'
SORT_ORDER_DESC = 'desc'


def google_column_chart_url(data):
    default_colors = ['ff0000', '00ff00', '0000ff']
    color_idx = 0
    header = data.pop(0)
    length = len(data)
    primary = -1
    sortcolumn = -1
    sortorder = SORT_ORDER_ASC
    colors = []
    legend = []
    units = ''
    for j in range(len(header)):
        if 'primary' in header[j] and header[j]['primary'] == 'true':
            primary = j
        else:
            if 'color' in header[j]:
                colors.append(header[j]['color'])
            else:
                colors.append(default_colors[color_idx])
                color_idx = (color_idx + 1) % 3
            if 'label' in header[j]:
                legend.append(header[j]['label'])
            else:
                legend.append("")
            if 'units' in header[j]:
                units = header[j]['units']
        if 'sort' in header[j]:
            sortcolumn = j
            sortorder = header[j]['sort']
    if sortcolumn > -1:
        data.sort(key=lambda row: row[sortcolumn])
        if sortorder == SORT_ORDER_DESC:
            data.reverse()
    data = zip(*data)
    if len(data) == 0:
        return ''
    if primary > -1:
        xaxis = data.pop(primary)
    chart = VerticalBarStack(data, encoding='text')
    axes = 'y'
    if primary > -1:
        chart.axes.label(1, *xaxis)
        axes += 'x'
        if 'units' in header[primary]:
            chart.axes.label(len(axes), None, header[primary]['units'], None)
            axes += 'x'
    if units != '':
        chart.axes.label(len(axes), None, units, None)
        axes += 'y'
    chart.axes(axes)
    chart.color(*colors)
    chart.fill('bg', 's', 'ffffff00')
    chart.bar(17, 630 / length - 17)
    chart.size(758, 200)
    chart.scale('a')  # automatic
    chart.legend(*legend)
    #Hack to allow a reversed legend.
    # http://code.google.com/p/google-chartwrapper/issues/detail?id=36
    chart['chdlp'] = 'r|r'
    return chart.url
