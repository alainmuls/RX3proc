from pylatex import Document, Section, Command, Package, simple_page_number, NewLine, FootnoteText, UnsafeCommand
from pylatex.utils import bold

__author__ = 'amuls'


def create_document(fhead: list, ffoot: list) -> Document:
    """
    create_document creates the latex document with fancy headers and returns the doc created
    """
    # Document with `\maketitle` command activated
    geometry_options = {
        'includeheadfoot': True,
        'headheight': '15mm',
        'headsep': '5mm',
        'landscape': False,
        'margin': '15mm',
        'bottom': '15mm',
        'footskip': '10mm'
    }

    doc = Document(documentclass='scrarticle', font_size='normalsize', geometry_options=geometry_options)

    doc.packages.append(Package('graphicx'))
    doc.packages.append(Package('fancyhdr'))
    # doc.packages.append(Package('a4wide'))
    doc.packages.append(Package('lastpage'))

    doc.packages.append(Package('babel', options='english'))
    doc.packages.append(Package('todonotes', options='colorinlistoftodos'))
    doc.packages.append(Package('adjustbox', options='export'))
    # doc.packages.append(Package('inputenc', options='utf8x'))

    doc.packages.append(Package('amsmath'))
    doc.packages.append(Package('graphicx'))
    doc.packages.append(Package('enumitem'))
    doc.packages.append(Package('listings'))
    doc.packages.append(Package('filecontents'))
    doc.packages.append(Package('verbatim'))
    doc.packages.append(Package('eurosym'))

    doc.packages.append(Package('tabu'))
    doc.packages.append(Package('ragged2e'))
    doc.packages.append(Package('varioref'))
    doc.packages.append(Package('float'))
    doc.packages.append(Package('makecell'))

    doc.packages.append(Package('color'))
    doc.packages.append(Package('hyperref'))
    doc.packages.append(UnsafeCommand('hypersetup', extra_arguments=r'colorlinks, breaklinks, urlcolor=blue, linkcolor=blue'))
    # \hypersetup{
    #     colorlinks=true, % make the links colored
    #     linkcolor=blue, % color TOC links in blue
    #     urlcolor=red, % color URLs in red
    #     linktoc=all % 'all' will create links for everything in the TOC
    # }

    # set fancy header styles
    doc.preamble.append(Command('pagestyle', 'fancy'))

    # create fancy header
    doc.preamble.append(Command('lhead', arguments=FootnoteText(fhead[0])))
    doc.preamble.append(Command('chead', arguments=FootnoteText(bold(fhead[1]))))
    doc.preamble.append(Command('rhead', arguments=FootnoteText(fhead[2])))
    # create fancy footer
    doc.preamble.append(Command('lfoot', arguments=FootnoteText(ffoot[0])))
    doc.preamble.append(Command('cfoot', arguments=FootnoteText(bold(ffoot[1]))))
    doc.preamble.append(Command('rfoot', arguments=FootnoteText(simple_page_number())))

    return doc


def document2pdf(doc: Document, pdfname: str):
    """
    document2pdf creates the pdf file from doc
    """
    doc.generate_tex(pdfname.split('.')[0])
    doc.generate_pdf(pdfname.split('.')[0], clean_tex=False, compiler_args=['--pdf'])


def add_section(doc: Document, sec_title: str, sec_content: list):
    """
    add_section add section to doc. The content has a paragraph for each element in the sec_content list
    """
    with doc.create(Section(sec_title)):
        for content in sec_content:
            doc.append(content)
            doc.append(NewLine)
