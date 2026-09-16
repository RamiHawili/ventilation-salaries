"""Mise en forme Excel (style maison) — utilisé pour écrire les classeurs de sortie."""
import re
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

GRIS = "D9D9D9"; BLEU = "1F4E78"; VERT = "548235"; BLANC = "FFFFFF"; NOIR = "000000"
FMT_NB = "0;-0;"          # nombres, masque les zéros
FMT_PCT = "0.0%;-0.0%;"   # pourcentage, masque les zéros
_side = Side(style="thin", color="BFBFBF")
BORD = Border(left=_side, right=_side, top=_side, bottom=_side)
TABLE_ROW = 4  # ligne de l'en-tête (tableau démarre à startrow=3)


def _tname(name):
    n = re.sub(r"[^A-Za-z0-9_]", "_", name)
    return n if n[:1].isalpha() else "T_" + n


def write_sheet(writer, df, sheet_name, title, subtitle="",
                header="gris", text_cols=None, pct_cols=None):
    """Écrit un DataFrame stylé dans une feuille du classeur."""
    text_cols = set(text_cols or []); pct_cols = set(pct_cols or [])
    df.to_excel(writer, sheet_name=sheet_name, startrow=TABLE_ROW - 1, index=False)
    ws = writer.sheets[sheet_name]
    n_rows, n_cols = df.shape
    first, last = TABLE_ROW + 1, TABLE_ROW + n_rows

    ws.sheet_view.showGridLines = False
    ws.freeze_panes = f"A{first}"
    for row in ws.iter_rows(min_row=1, max_row=last, max_col=n_cols):
        for c in row:
            c.font = Font(name="Arial", size=10)

    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols)
    ws.cell(1, 1, title).font = Font(name="Arial", size=16, bold=True, color=BLEU)
    ws.row_dimensions[1].height = 24
    if subtitle:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols)
        ws.cell(2, 1, subtitle).font = Font(name="Arial", size=10, italic=True, color=BLEU)

    if header == "vert":
        fill = PatternFill("solid", fgColor=VERT); font = Font(name="Arial", size=10, bold=True, color=BLANC)
    else:
        fill = PatternFill("solid", fgColor=GRIS); font = Font(name="Arial", size=10, bold=True, color=BLEU)
    for j in range(1, n_cols + 1):
        c = ws.cell(TABLE_ROW, j)
        c.fill = fill; c.font = font
        c.alignment = Alignment(horizontal="center", vertical="center"); c.border = BORD

    for j, col in enumerate(df.columns, start=1):
        for i in range(first, last + 1):
            c = ws.cell(i, j); c.border = BORD
            if col in pct_cols:
                c.number_format = FMT_PCT; c.alignment = Alignment(horizontal="center")
            elif pd.api.types.is_numeric_dtype(df[col]):
                c.number_format = FMT_NB; c.alignment = Alignment(horizontal="right")
            if col in text_cols:
                c.font = Font(name="Arial", size=10, bold=True, color=NOIR)

    for j in range(1, n_cols + 1):
        w = max([len(str(df.columns[j - 1]))] +
                [len(str(v)) for v in df.iloc[:, j - 1].head(200)])
        ws.column_dimensions[get_column_letter(j)].width = min(w + 3, 45)

    if n_rows:
        tbl = Table(displayName=_tname(sheet_name),
                    ref=f"A{TABLE_ROW}:{get_column_letter(n_cols)}{last}")
        tbl.tableStyleInfo = TableStyleInfo(name=None, showRowStripes=False,
                                            showColumnStripes=False)
        ws.add_table(tbl)
    return ws