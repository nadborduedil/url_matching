"""
this module is about estimating whether a scraped website belongs to a given
company.
"""

from sklearn.linear_model.logistic import LogisticRegression

common_suffixes = {"public", "limited", "company", "ltd", "ltd.", "(ltd)",
                   "holdings", "group", "llp", "uk", "u.k.", "(uk)", "(u.k.)",
                   "bank", "plc", "p.l.c.", "(plc)", "p-l-c"}
common_prefixes = ["the"]


def normalised(phrase):
    """strips common words from ends of a company name leaving the unique core

    >>> normalised("the best test case I've ever seen limited (uk)")
    "best test case i've ever seen"
    """
    p = phrase.lower().split()
    while len(p) > 1 and p[-1] in common_suffixes:
        p.pop()
    while len(p) > 1 and p[0] in common_prefixes:
        p = p[1:]
    return " ".join(p)


def make_features(url, website, company):
    webset = set(website.lower().split())
    assets = company['accounts_assets_total'] or 0
    assets_nonzero = int(assets != 0)
    name = company['name'].lower()
    normname = normalised(company['name'])

    name_score = 1 if name in website else 0
    norm_name_score = 1 if normname in website else 0
    directors_surnames_count = sum(d['surname'].lower() in webset
                                   for d in company['directors'] if
                                   d['surname'])
    directors_fullnames_count = sum(
        (d['forename'] + " " + d['surname']).lower() in website
        for d in company['directors'] if d['surname'] and d['forename'])

    return [name_score, norm_name_score, directors_surnames_count,
            directors_fullnames_count, assets, assets_nonzero]


class WebsiteMatchConfidencePredictor(object):
    def __init__(self):
        self.model = LogisticRegression()


    def fit(self, urls, websites, y):
        """

        :param urls: list of urls
        :param websites: list of corresponding scraped websites
        :param y: list of corresponding booleans - matches or not
        """
        X = [make_features(url, web) for url, web in zip(urls, websites)]
        self.model.fit(X, y)

    def predict(self, url, website):
        X = make_features(url, website)
        return self.model.predict_proba(X)
