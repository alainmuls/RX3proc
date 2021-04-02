from pylatex import Document, Section, NewLine, Subsection, Tabular, Subsubsection
from pylatex.section import Paragraph

__author__ = 'amuls'


def add_section(title: str, label: bool = True):
    """
    add_section adds a section with its title to doc
    """
    return Section(title=title, label=label)


def add_subsection(title: str, label: bool = True):
    """
    add_section adds a section with its title to doc
    """
    return Subsection(title=title, label=label)


def add_subsubsection(title, numbering=None, *, label=False):
    """
    add_section adds a section with its title to doc
    """
    return Subsubsection(title=title, label=label)


def add_paragraph(title: str, label: bool = True):
    """
    add_section adds a section with its title to doc
    """
    return Paragraph(title=title, label=label)


def add_data2section(sec, data):
    # Section from a dictionary
    if type(data) is dict:
        for k, v in data.items():
            sec.append('{key!s}: {value!s}\n'.format(key=k, value=v))

    sec.append(NewLine())


def add_data2section2(sec, data):
    # Section from a dictionary
    if type(data) is dict:
        with sec.create(Tabular('|r|l|', data=None, pos=None, width=2)) as table:
            table.add_hline(start=None, end=None)
            for k, v in data.items():
                table.add_row((k, v))

    # sec.append(table)
    sec.append(NewLine())














# # make tabular
# tabular1 = Tabular('|c|c|c|c|')
# tabular1.add_hline()
# tabular1.add_row((1, 2, 3, 4))
# tabular1.add_hline()



# with doc.create(Tabular('rc|cl')) as table:
#                 table.add_hline()
#                 table.add_row((1, 2, 3, 4))
#                 table.add_hline(1, 2)
#                 table.add_empty_row()
#                 table.add_row((4, 5, 6, 7))



# def test_table():
#     # Tabular
#     t = Tabular(table_spec='|c|c|', data=None, pos=None, width=2)

#     t.add_hline(start=None, end=None)

#     t.add_row((1, 2), escape=False, strict=True, mapper=[bold])
#     t.add_row(1, 2, escape=False, strict=True, mapper=[bold])

#     # MultiColumn/MultiRow.
#     t.add_row((MultiColumn(size=2, align='|c|', data='MultiColumn'),),
#               strict=True)

#     # One multiRow-cell in that table would not be proper LaTeX,
#     # so strict is set to False
#     t.add_row((MultiRow(size=2, width='*', data='MultiRow'),), strict=False)
