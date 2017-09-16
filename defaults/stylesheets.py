from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def stylesheet():
    ''' Override the getSampleStyleSheet, and add own styles'''
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyTextCenter', parent=styles['BodyText'], alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold'))
    return styles

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def stylesheet_washinglabels():
    ''' Override the getSampleStyleSheet, and add own styles'''
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Bold', 
        parent=styles['BodyText'], 
        fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(
        name='NormalSmall',
        parent=styles['Normal'],
        fontSize=8))
    return styles    