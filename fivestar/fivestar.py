from fivestar.data import get_data

class FiveStar():

    def __init__(self):
        self.listings = get_data()
        self.clusters = get_data('clusters')

    def get_listing(self, listing_id):
        """Look up full info for an id and return it as a dict???"""
        data = self.listings.loc[listing_id].to_dict('records')[0]
        return data
