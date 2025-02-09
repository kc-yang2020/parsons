from parsons.utilities import json_format
import logging

logger = logging.getLogger(__name__)


class People(object):

    def __init__(self, van_connection):

        self.connection = van_connection

    def find_person(self, first_name=None, last_name=None, date_of_birth=None, email=None,
                    phone=None, street_number=None, street_name=None, zip=None, match_map=None):
        """
        Find a person record.

        .. note::
            Person find must include the following minimum combinations to conduct
            a search.

            - first_name, last_name, email
            - first_name, last_name, phone
            - first_name, last_name, zip5, date_of_birth
            - first_name, last_name, street_number, street_name, zip5
            - email_address

        .. note::
            The arguments that can be passed are a selection of the possible values that
            can be used in a search. A full list of possible values can be found
            `here <https://developers.ngpvan.com/van-api#match-candidates>`_. To use these
            values, pass in a dictionary using the match_map argument.

        `Args:`
            first_name: str
                The person's first name
            last_name: str
                The person's last name
            dob: str
                ISO 8601 formatted date of birth (e.g. ``1981-02-01``)
            email: str
                The person's email address
            phone: str
                Phone number of any type (Work, Cell, Home)
            street_number: str
                Street Number
            street_name: str
                Street Name
            zip: str
                5 digit zip code
            match_map: dict
                A dictionary of values to match against. Will override all
                other arguments if provided.
            fields: The fields to return. Leave as default for all available fields
        `Returns:`
            A person dict
        """

        logger.info(f'Finding {first_name} {last_name}.')

        return self._people_search(first_name, last_name, date_of_birth, email, phone,
                                   street_number, street_name, zip, match_map)

    def upsert_person(self, first_name=None, last_name=None, date_of_birth=None, email=None,
                      phone=None, street_number=None, street_name=None, zip=None, match_map=None):
        """
        Create or update a person record.

        .. note::
            Person find must include the following minimum combinations.

            - first_name, last_name, email
            - first_name, last_name, phone
            - first_name, last_name, zip5, date_of_birth
            - first_name, last_name, street_number, street_name, zip5
            - email_address

        .. note::
            The arguments that can be passed are a selection of the possible values that
            can be used in a search. A full list of possible values can be found
            `here <https://developers.ngpvan.com/van-api#match-candidates>`_. To use these
            values, pass in a dictionary using the match_map argument.

        .. warning::
            This method can only be run on MyMembers, EveryAction, MyCampaign databases.

        `Args:`
            first_name: str
                The person's first name
            last_name: str
                The person's last name
            dob: str
                ISO 8601 formatted date of birth (e.g. ``1981-02-01``)
            email: str
                The person's email address
            phone: str
                Phone number of any type (Work, Cell, Home)
            street_number: str
                Street Number
            street_name: str
                Street Name
            zip: str
                5 digit zip code
            match_map: dict
                A dictionary of values to match against. Will override all
                other arguments if provided.
        `Returns:`
            A person dict
        """

        return self._people_search(first_name, last_name, date_of_birth, email, phone,
                                   street_number, street_name, zip, match_map, create=True)

    def _people_search(self, first_name=None, last_name=None, date_of_birth=None, email=None,
                       phone=None, street_number=None, street_name=None, zip=None, match_map=None,
                       create=False):
        # Internal method to hit the people find/create endpoints

        # Ensure that the minimum combination of fields were passed
        self._valid_search(first_name, last_name, email, phone, date_of_birth, street_number,
                           street_name, zip, match_map)

        # Check to see if a match map has been provided
        if not match_map:
            json = {"firstName": first_name, "lastName": last_name}

            # Will fail if empty dicts are provided, hence needed to add if exist
            if email:
                json['emails'] = [{'email': email}]
            if phone:  # To Do: Strip out non-integers from phone
                json['phones'] = [{'phoneNumber': phone}]
            if date_of_birth:
                json['dateOfBirth'] = date_of_birth
            if zip:
                json['addresses'] = [{'zipOrPostalCode': zip}]
        else:
            json = match_map

        # Determine correct url
        url = 'people/find'
        if create:
            url = url + 'OrCreate'

        return self.connection.post_request(url, json=json)

    def _valid_search(self, first_name, last_name, email, phone, dob, street_number,
                      street_name, zip, match_map):
        # Internal method to check if a search is valid
        if not match_map:
            if (
                None in [first_name, last_name, email] and
                None in [first_name, last_name, phone] and
                None in [first_name, last_name, zip, dob] and
                None in [first_name, last_name, street_number, street_name, zip] and
                None in [email]
            ):
                raise ValueError("""
                                 Person find must include the following minimum
                                 combinations to conduct a search.
                                    - first_name, last_name, email
                                    - first_name, last_name, phone
                                    - first_name, last_name, zip, dob
                                    - first_name, last_name, street_number, street_name, zip
                                    - email
                                """)
        else:
            if (
                None in [
                    match_map.get('firstName', None),
                    match_map.get('lastName', None),
                    match_map.get('emails', [{}])[0].get('email', None)
                ] and
                None in [
                    match_map.get('firstName', None),
                    match_map.get('lastName', None),
                    match_map.get('phones', [{}])[0].get('phoneNumber', None)
                ] and
                None in [
                    match_map.get('firstName', None),
                    match_map.get('lastName', None),
                    match_map.get('addresses', [{}])[0].get('zipOrPostalCode', None),
                    match_map.get('dateOfBirth', None)
                ] and
                None in [
                    match_map.get('firstName', None),
                    match_map.get('addresses', [{}])[0].get('addressLine1', None),
                    match_map.get('addresses', [{}])[0].get('zipOrPostalCode', None)
                ] and
                None in [match_map.get('emails', [{}])[0].get('email', None)]
            ):
                print(match_map)
                raise ValueError("""
                                 Person find must include the following minimum
                                 combinations to conduct a search.
                                    - first_name, last_name, email
                                    - first_name, last_name, phone
                                    - first_name, last_name, zip, dob
                                    - first_name, last_name, street_number, street_name, zip
                                    - email
                                """)
        return True

    def get_person(self, id, id_type='vanid', expand_fields=[
                   'contribution_history', 'addresses', 'phones', 'emails',
                   'codes', 'custom_fields', 'external_ids', 'preferences',
                   'recorded_addresses', 'reported_demographics', 'suppressions',
                   'cases', 'custom_properties', 'districts', 'election_records',
                   'membership_statuses', 'notes', 'organization_roles', 'scores',
                   'disclosure_field_values']):
        """
        Returns a single person record using their VANID or external id.

        `Args:`
            id: str
                A valid id
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``
            expand_fields: list
                A list of fields for which to include data. If a field is omitted,
                ``None`` will be returned for that field. Can be ``contribution_history``,
                ``addresses``, ``phones``, ``emails``, ``codes``, ``custom_fields``,
                ``external_ids``, ``preferences``, ``recorded_addresses``,
                ``reported_demographics``, ``suppressions``, ``cases``, ``custom_properties``,
                ``districts``, ``election_records``, ``membership_statuses``, ``notes``,
                ``organization_roles``, ``scores``, ``disclosure_field_values``.
        `Returns:`
            A person dict
        """

        # Change end point based on id type
        if id_type == 'vanid':
            url = f'people/{id}'
        else:
            url = f'people/{id_type}:{id}'

        expand_fields = ','.join([json_format.arg_format(f) for f in expand_fields])

        logger.info(f'Getting person with {id_type} of {id}')
        return self.connection.get_request(url, params={'$expand': expand_fields})

    def apply_canvass_result(self, id, result_code_id, response=None, id_type='vanid', contact_type_id=None,
                             input_type_id=None, date_canvassed=None):
        """
        Apply a canvass result to a person. Use this end point for attempts that do not
        result in a survey response or an activist code (e.g. Not Home).

        `Args:`
            id: str
                A valid person id
            result_code_id : int
                Specifies the result code of the attempt. Valid ids can be found
                by using the :meth:`get_canvass_responses_result_codes`
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``
            contact_type_id : int
                `Optional`; A valid contact type id
            input_type_id : int
                `Optional`; Defaults to 11 (API Input)
            date_canvassed : str
                `Optional`; ISO 8601 formatted date. Defaults to todays date
        `Returns:`
            ``None``
        """

        logger.info(f'Applying result code {result_code_id} to {id_type} {id}.')
        return self.apply_response(id, response=response, id_type=id_type, contact_type_id=contact_type_id,
                                   input_type_id=input_type_id, date_canvassed=date_canvassed,
                                   result_code_id=result_code_id)

    def toggle_volunteer_action(self, id, volunteer_activity_id, action, id_type='vanid',
                                result_code_id=None, contact_type_id=None, input_type_id=None,
                                date_canvassed=None):
        """
        Apply or remove a volunteer action to or from a person.

        `Args:`
            id: str
                A valid person id
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``
            volunteer_activity_id: int
                A valid volunteer activity id
            action: str
                Either 'apply' or 'remove'
            result_code_id : int
                `Optional`; Specifies the result code of the response. If
                not included,responses must be specified. Conversely, if
                responses are specified, result_code_id must be null. Valid ids
                can be found by using the :meth:`get_canvass_responses_result_codes`
            contact_type_id: int
                `Optional`; A valid contact type id
            input_type_id: int
                `Optional`; Defaults to 11 (API Input)
            date_canvassed: str
                `Optional`; ISO 8601 formatted date. Defaults to todays date

        ** NOT IMPLEMENTED **
        """

        """
        response = {"volunteerActivityId": volunteer_activity_id,
                    "action": self._action_parse(action),
                    "type": "VolunteerActivity"}

        logger.info(f'{action} volunteer activity {volunteer_activity_id} to {id_type} {id}')
        self.apply_response(id, response, id_type, contact_type_id, input_type_id, date_canvassed,
                            result_code_id)
        """

    def apply_response(self, id, response, id_type='vanid', contact_type_id=None,
                       input_type_id=None, date_canvassed=None, result_code_id=None):
        """
        Apply responses such as survey questions, activist codes, and volunteer actions
        to a person record. This method allows you apply multiple responses (e.g. two survey
        questions) at the same time. It is a low level method that requires that you
        conform to the VAN API `response object format <https://developers.ngpvan.com/van-api#people-post-people--vanid--canvassresponses>`_.

        `Args:`
            id: str
                A valid person id
            response: dict
                A list of dicts with each dict containing a valid action.
            id_type: str
                A known person identifier type available on this VAN instance
                such as ``dwid``
            result_code_id : int
                `Optional`; Specifies the result code of the response. If
                not included,responses must be specified. Conversely, if
                responses are specified, result_code_id must be null. Valid ids
                can be found by using the :meth:`get_canvass_responses_result_codes`
            contact_type_id : int
                `Optional`; A valid contact type id
            input_type_id : int
                `Optional`; Defaults to 11 (API Input)
            date_canvassed : str
                `Optional`; ISO 8601 formatted date. Defaults to todays date
            responses : list or dict
        `Returns:`
            ``True`` if successful

        .. code-block:: python

            response = [{"activistCodeId": 18917,
                         "action": "Apply",
                         "type": "ActivistCode"},
                        {"surveyQuestionId": 109149,
                         "surveyResponseId": 465468,
                         "action": "SurveyResponse"}
                        ]
            van.apply_response(5222, response)
        """  # noqa: E501,E261

        # Set url based on id_type
        if id_type == 'vanid':
            url = f"people/{id}/canvassResponses"
        else:
            url = f"people/{id_type}:{id}/canvassResponses"

        json = {"canvassContext": {
            "contactTypeId": contact_type_id,
            "inputTypeId": input_type_id,
            "dateCanvassed": date_canvassed},
            "resultCodeId": result_code_id}

        if response:
            json['responses'] = response

        if result_code_id is not None and response is not None:
            raise ValueError("Both result_code_id and responses cannot be specified.")

        if isinstance(response, dict):
            json["responses"] = [response]

        if result_code_id is not None and response is not None:
            raise ValueError(
                "Both result_code_id and responses cannot be specified.")

        return self.connection.post_request(url, json=json)

    def create_relationship(self, vanid_1, vanid_2, relationship_id):
        """
        Create a relationship between two individuals

        `Args:`
            vanid_1 : int
                The vanid of the primary individual; aka the node
            vanid_2 : int
                The vanid of the secondary individual; the spoke
            relationship_id : int
                The relationship id indicating the type of relationship
        `Returns:`
            ``None``
        """

        json = {'relationshipId': relationship_id,
                'vanId': vanid_2}

        self.connection.post_request(f"people/{vanid_1}/relationships", json=json)
        logger.info('Relationship {vanid_1} to {vanid_2} created.')
