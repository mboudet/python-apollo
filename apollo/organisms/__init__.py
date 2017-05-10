"""
Contains possible interactions with the Apollo Organisms Module
"""
from apollo.client import Client


class OrganismsClient(Client):
    CLIENT_BASE = '/organism/'

    def add_organism(self, common_name, directory, blatdb=None, genus=None,
                     species=None, public=False):
        """
        Add an organism

        :type common_name: str
        :param common_name: Organism common name

        :type directory: str
        :param directory: Server-side directory

        :type blatdb: str
        :param blatdb: Server-side Blat directory for the organism

        :type genus: str
        :param genus: Genus

        :type species: str
        :param species: Species

        :type public: bool
        :param public: User's email

        :rtype: dict
        :return: a dictionary with information about the new organism
        """
        data = {
            'commonName': common_name,
            'directory': directory,
            'publicMode': public,
        }

        if blatdb is not None:
            data['blatdb'] = blatdb
        if genus is not None:
            data['genus'] = genus
        if species is not None:
            data['species'] = species

        response = self.post('addOrganism', data)
        # Apollo decides here that it would be nice to return information about
        # EVERY organism. LMAO.
        return [x for x in response if x['commonName'] == common_name][0]

    def update_organism(self, organism_id, common_name, directory, blatdb=None, species=None, genus=None, public=False):
        """
        Update an organism

        :type organism_id: str
        :param organism_id: Organism ID Number

        :type common_name: str
        :param common_name: Organism common name

        :type directory: str
        :param directory: Server-side directory

        :type blatdb: str
        :param blatdb: Server-side Blat directory for the organism

        :type genus: str
        :param genus: Genus

        :type species: str
        :param species: Species

        :type public: bool
        :param public: User's email

        .. warning::
            Not specifying genus/species/public state will cause those values to be wiped.

        :rtype: dict
        :return: a dictionary with information about the new organism
        """
        data = {
            'id': organism_id,
            'name': common_name,
            'directory': directory,
            'publicMode': public,
        }

        if blatdb is not None:
            data['blatdb'] = blatdb
        if genus is not None:
            data['genus'] = genus
        if species is not None:
            data['species'] = species

        response = self.post('updateOrganismInfo', data)
        if len(response.keys()) == 0:
            return self.show_organism(organism_id)
        return response

    def get_organisms(self, common_name=None):
        """
        Get all organisms

        :type cn: str
        :param cn: Optionally filter on common name

        :rtype: dict
        :return: Organisms information
        """
        orgs = self.post('findAllOrganisms', {})
        if common_name:
            orgs = [x for x in orgs if x['commonName'] == common_name]
            if len(orgs) == 0:
                raise Exception("Unknown common name")
            else:
                return orgs[0]
        else:
            return orgs

    def show_organism(self, organism_id):
        """
        Get information about a specific organism. Due to the lack of an API,
        this call requires fetching the entire list of organisms and iterating
        through. If you find this painfully slow, please submit a bug report
        upstream.

        :type organism_id: str
        :param organism_id: Organism ID Number

        :rtype: dict
        :return: a dictionary containing the organism's information
        """
        orgs = self.get_organisms()
        orgs = [x for x in orgs if str(x['id']) == str(organism_id)]

        if len(orgs) == 0:
            raise Exception("Unknown ID")
        else:
            return orgs[0]

    def delete_organism(self, organism_id):
        """
        Delete an organim

        :type organism_id: str
        :param organism_id: Organism ID Number

        :rtype: dict
        :return: an empty dictionary
        """
        return self.post('deleteOrganism', {'id': organism_id})

    def delete_features(self, organism_id):
        """
        Remove features of an organism

        :type organism_id: str
        :param organism_id: Organism ID Number

        :rtype: dict
        :return: an empty dictionary
        """
        return self.post('deleteOrganismFeatures', {'id': organism_id})

    def get_sequences(self, organism_id):
        """
        Get the sequences for an organism

        :type organism_id: str
        :param organism_id: Organism ID Number

        :rtype: list of dict
        :return: The set of sequences associated with an organism
        """
        return self.post('getSequencesForOrganism', {'organism': organism_id})
