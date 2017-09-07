from operator import itemgetter

COUNTRY_CHOICE = [
    ('DE', 'Germany'),
    ('BE', 'Belgium'),
    ('FR', 'France'),
    ('SE', 'Sweden'),
    ('CH', 'Switzerland'),
    ('DK', 'Denmark'),
    ('NL', 'Netherlands'),
    ('AT', 'Austria'),
    ('IT', 'Italy'),
    ('NO', 'Norway'),
    ('RU', 'Russia'),
    ('GB', 'Great Brittain'),
]
COUNTRY_CHOICE.sort(key=itemgetter(1,0))