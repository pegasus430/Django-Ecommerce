from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from django.conf import settings

import os


def stylesheet():
    ''' Override the getSampleStyleSheet, and add own styles'''
    styles = getSampleStyleSheet()
    pdfmetrics.registerFont(TTFont('Arial', os.path.join(settings.STATIC_ROOT, 'pdf/Arial.ttf')))
    styles.add(ParagraphStyle(name='BodyTextCenter', parent=styles['BodyText'], alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold'))

    styles['Title'].fontName = 'Arial'
    styles['BodyText'].fontName = 'Arial'
    styles['Bullet'].fontName = 'Arial'
    styles['Heading1'].fontName = 'Arial'
    styles['Heading2'].fontName = 'Arial'
    styles['Heading3'].fontName = 'Arial'
    styles['BodyTextCenter'].fontName = 'Arial'
    return styles


# def stylesheet():
#     ''' Override the getSampleStyleSheet, and add own styles'''
#     styles = getSampleStyleSheet()
#     styles.add(ParagraphStyle(name='BodyTextCenter', parent=styles['BodyText'], alignment=TA_CENTER))
#     styles.add(ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold'))
#     return styles

def stylesheet_labels():
    ''' Override the getSampleStyleSheet, and add own styles'''
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyTextSmall', parent=styles['BodyText'], fontSize=8))
    styles.add(ParagraphStyle(name='BodyTextSmallCenter', parent=styles['BodyText'], fontSize=8, 
        alignment=TA_CENTER))
    return styles


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