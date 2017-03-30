from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from apiclient import errors


class GoogleAdminAPI(object):
    """
    All things Google Admin can be found here
    """

    def __init__(self, scopes, service_account_pkcs12_file_path):
        """
        General values used by all definitions

        :param scopes: the list of scopes that will be used by these methods
        :type scopes: list
        :param service_account_pkcs12_file_path: the location of the PKCS12 file
        :type service_account_pkcs12_file_path: str
        """

        self.SCOPES = scopes
        self.SERVICE_ACCOUNT_EMAIL = 'GOOGLE IAM EMAIL ADDRESS'
        self.SERVICE_ACCOUNT_PKCS12_FILE_PATH = service_account_pkcs12_file_path
        self.DELEGATE = 'EMAIL ADDRESS TO IMPERSONATE'

    def create_directory_service(self, service, api_version):
        """Build and returns an Admin SDK Directory service object authorized with the service accounts
        that act on behalf of the given user.

        user_email: The email of the user. Needs permission to access the Admin APIs.

        :param service: Name of the service to be used
        :type service: str
        :param api_version: API version of the service mentioned
        :type api_version: str
        :return: Admin SDK directory service object.
        :rtype: service object
        """

        # Pull the details from the secrets file
        credentials = ServiceAccountCredentials.from_p12_keyfile(
            self.SERVICE_ACCOUNT_EMAIL,
            self.SERVICE_ACCOUNT_PKCS12_FILE_PATH,
            'notasecret',
            scopes=self.SCOPES
        )

        credentials = credentials.create_delegated(self.DELEGATE)

        return build(service, api_version, credentials=credentials)


class GoogleAdminClient(GoogleAdminAPI):
    """
    GoogleAdminClient using GoogleAdminAPI subclass
    """

    def user_status(self, email):
        # Build the service
        service = self.create_directory_service('admin', 'directory_v1')

        # Get the users current status
        results = service.users().get(userKey=email).execute()

        # Get users status
        return results['suspended']

    def get_group_members(self, group_email):
        """
        Pull the current group members from the Google Group

        :param group_email: full email address of the group to be queried
        :type group_email: str

        :return: a python list of all members
        :rtype: list
        """

        # Build the service
        service = self.create_directory_service('admin', 'directory_v1')
        # Define the list
        members = []

        # Give it a whirl
        try:
            # Build the object but don't execute
            results = service.members().list(groupKey=group_email)

            # Loop until we hit a break condition
            while True:
                # Execute the results object
                this_page = results.execute()

                # look for members if nothing is found
                # update and break
                if 'members' in this_page:
                    for u in this_page['members']:
                        members.append(u['email'])
                if 'members' not in this_page:
                    members.append('No Members')
                    break
                if 'nextPageToken' in this_page:
                    results = service.members().list(groupKey=group_email,
                                                     pageToken=this_page['nextPageToken'])
                else:
                    break

        # When something goes wrong deal with it
        except errors.HttpError as e:
            error = "An error has occurred while getting {email} group membership -- {error}".format(
                email=group_email,
                error=e._get_reason()
            )
            # Return the reason
            return error

        # If nothing went wrong return the list
        return members

    def get_membership(self, user_email):
        """
        Pull the current groups the user is a member of from the Google Domain

        :param user_email: email address of the user
        :type user_email: str

        :return: a list of groups that user is a member of
        :rtype: list
        """

        # Build the service
        service = self.create_directory_service('admin', 'directory_v1')

        # Define the list
        groups = []

        # Give it a whirl
        try:
            # Build the object but don't execute
            results = service.groups().list(domain='bloomreach.com',
                                            userKey=user_email)

            # Loop until we encounter a break
            while True:
                # Execute the results object
                this_page = results.execute()

                # Look for groups and append
                if 'groups' in this_page:
                    for g in this_page['groups']:
                        groups.append(g['email'])
                # If nothing append and break
                if 'groups' not in this_page:
                    groups.append('No Groups')
                    break
                # If a next page token exists go to the next page
                if 'nextPageToken' in this_page:
                    results = service.groups().list(domain='bloomreach.com',
                                                    pageToken=this_page['nextPageToken'])
                # If all above are false
                else:
                    break

        # When something goes wrong deal with it
        except errors.HttpError as e:
            error = "An error has occurred while getting {email} group membership -- {error}".format(
                email=user_email,
                error=e._get_reason()
            )
            # Return the reason
            return error

        # Return the groups list
        return groups

    def add_membership(self, group, email):
        """
        Add a user to the group specified 
        :param group: full email address of the group
        :type group: str
        :param email: the email address of the user
        :type email: str
        :return: if it was successful or not
        :rtype: str
        """

        # Build the service
        service = self.create_directory_service('admin', 'directory_v1')

        # Try to add user to selected group
        try:
            # Add the user to the group
            service.members().insert(groupKey=group,
                                     body={"email": email}).execute()
            results = "{email} was successfully added to {group}".format(email=email,
                                                                         group=group)
            # Return the results of the method
            return results

        # Encounter an error deal with it
        except errors.HttpError as e:
            error = "An error has occurred while adding {email} to {group} -- {error}".format(
                email=email,
                group=group,
                error=e._get_reason()
            )
            # Return the results of the error
            return error

    def remove_members(self, group, email):
        """
        Remove a specified user from the specified group 
        in the Google Domain. 

        :param email: The email of the user to be removed
        :type email: str
        :param group: The full email address of the group to have 
                      the user removed from.
        :type group: str
        :return error: Return an error if something goes wrong
        :rtype: str
        """

        # Build the service
        service = self.create_directory_service('admin', 'directory_v1')

        try:
            # Remove a member from the group
            service.members().delete(groupKey=group,
                                     memberKey=email).execute()
        # Encounter an error deal with it
        except errors.HttpError as e:
            error = "An error has occurred while removing {email} from {group} -- {error}".format(
                email=email,
                group=group,
                error=e._get_reason()
            )
            # Return the results of the error
            return error

    def suspend_user(self, email):
        """
        suspend a specified user from the Google Domain. 

        :param email: The email of the user to be suspended
        :type email: str
        :return error: Return an error if something goes wrong
        :rtype: str
        """
        # Build the service
        service = self.create_directory_service('admin', 'directory_v1')

        # Get the users current status
        results = self.user_status(email)

        try:
            # If the user is not suspended
            if not results:
                # Suspend the user
                service.users().update(userKey=email,
                                       body={"suspended": True}).execute()
        # Encounter an error deal with it
        except errors.HttpError as e:
            error = "An error has occurred while suspending {email} -- {error}".format(
                email=email,
                error=e._get_reason()
            )
            # Return the results of the error
            return error

    def unsuspend_user(self, email):
        """
        un-suspend a specified user from the Google Domain. 

        :param email: The email of the user to be un-suspended
        :type email: str
        :return error: Return an error if something goes wrong
        :rtype: str
        """
        # Build the service
        service = self.create_directory_service('admin', 'directory_v1')

        # Get the users current status
        results = self.user_status(email)

        try:
            # If the user is suspended
            if results:
                # Un-Suspend the user
                service.users().update(userKey=email,
                                       body={"suspended": False}).execute()
        # Encounter an error deal with it
        except errors.HttpError as e:
            error = "An error has occurred while suspending {email} -- {error}".format(
                email=email,
                error=e._get_reason()
            )
            # Return the results of the error
            return error

    def delete_user(self, email):
        """
        This will delete a specified user from the Google Domain. This 
        method is reversible but only within five (5) days from the initial 
        run of the job

        :param email: The email of the user to be deleted
        :type email: str
        :return error: Return an error if something goes wrong
        :rtype: str
        """
        # Build the service
        service = self.create_directory_service('admin', 'directory_v1')

        # Get the users current status
        results = self.user_status(email)

        try:
            # If true
            if results:
                # Delete the user
                service.users().delete(userKey=email).execute()
                print('Deleted {user} if this was done in error'
                      'please use undo_delete_user within 5 DAYS!'.format(user=email))

        # Encounter an error deal with it
        except errors.HttpError as e:
            error = "An error has occurred while deleting {email} -- {error}".format(
                email=email,
                error=e._get_reason()
            )
            # Return the error
            return error

    def undo_delete_user(self, email):
        """
        Undo the delete of the user so long as this is within 5 days

        :param email: the full email address of the user
        :type email: str
        :return: Error if any 
        :rtype: str
        """

        # Build the service
        service = self.create_directory_service('admin', 'directory_v1')

        # Get the users current status
        results = self.user_status(email)

        try:
            # If true
            if results:
                # Un-delete the user from the domain
                service.users().undelete(userKey=email,
                                         body={"orgUnitPath": "/"}).execute()
                print('Un-Deleting {user} if this was done in error'
                      'please use delete_user'.format(user=email))

        # Encounter an error deal with it
        except errors.HttpError as e:
            error = "An error has occurred while un-deleting {email} -- {error}".format(
                email=email,
                error=e._get_reason()
            )
            # Return the error
            return error
