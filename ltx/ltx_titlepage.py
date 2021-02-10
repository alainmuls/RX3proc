import os
from pylatex import Document, MiniPage, TextBlock, MediumText, HugeText, NewPage, NewLine, NoEscape, TextColor, Figure
from pylatex.utils import bold

__author__ = 'amuls'


def add_lines(ltx_part, nr_lines: int = 1):
    """
    add_lines add given number of linebreaks
    """
    for i in range(nr_lines):
        ltx_part.append(NewLine())


def report_titlepage(doc: Document, report_info: list):
    """
    report_titlepage creates the titlepage for a report
    """
    # Defines a new command for the horizontal lines, change thickness here
    # hrule = Command(command=r'newcommand{\HRule}{\rule{\linewidth}{0.5mm}}')

    # width A4 is 210 x 297

    # doc.append(hrule)
    # doc.append(r'HRule')

    # doc.append('test')
    # doc.add_hline(color="blue")
    # doc.append('test')
    # NewLine(arguments=None, options=None, *, extra_arguments=None)

    doc.change_length(r"\TPHorizModule", "1mm")
    doc.change_length(r"\TPVertModule", "1mm")

    with doc.create(MiniPage(width=r"\textwidth")) as page:
        # with page.create(TextBlock())
        with page.create(TextBlock(134, 20, 50)):
            page.append(NoEscape(r"\noindent\rule{\textwidth}{1pt}"))
            add_lines(ltx_part=page, nr_lines=2)
            page.append(HugeText(bold('{title:s}\n'.format(title=report_info['title']))))
            add_lines(ltx_part=page, nr_lines=2)
            page.append(MediumText(bold('{subtitle:s}\n'.format(subtitle=report_info['subtitle']))))
            page.append(NoEscape(r"\noindent\rule{\textwidth}{1pt}"))

            # page.append(VerticalSpace('14mm', *))
            add_lines(ltx_part=page, nr_lines=5)
            for author, company in zip(report_info['author'], report_info['company']):
                page.append(MediumText(bold('{author:s}, {company:s}\n\n'.format(author=author, company=company))))

            # add if not None the classification level
            if report_info['classification'] is not None:
                add_lines(ltx_part=page, nr_lines=5)
                page.append(MediumText(TextColor(color='red', data=report_info['classification'])))

            # add the logo
            add_lines(ltx_part=page, nr_lines=5)
            with page.create(Figure(position='h!')) as logo:
                logo.add_image(os.path.expanduser('/home/amuls/amPython/rnxproc/logo-rma.eps'), width='105px')

    doc.append(NewPage())

    doc.append(NoEscape(r'\tableofcontents'))
    doc.append(NoEscape(r"\noindent\rule{\textwidth}{1pt}"))
