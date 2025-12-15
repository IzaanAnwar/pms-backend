import json

from django.test import Client, TestCase

from apps.accounts.models import User
from apps.api.jwt import create_access_token
from apps.organizations.models import Organization, OrganizationMember


class GraphQLAuthAndOrgIsolationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _graphql(self, *, query: str, variables: dict | None = None, token: str | None = None, org_id: str | None = None):
        headers: dict[str, str] = {}
        if token:
            headers['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        if org_id:
            headers['HTTP_X_ORGANIZATION_ID'] = org_id

        payload = {'query': query}
        if variables is not None:
            payload['variables'] = variables

        response = self.client.post(
            '/graphql',
            data=json.dumps(payload),
            content_type='application/json',
            **headers,
        )
        return response.json()

    def test_me_requires_authentication(self):
        data = self._graphql(query='query { me { id } }')
        self.assertIn('errors', data)
        self.assertEqual(data['errors'][0]['message'], 'Authentication required')

    def test_org_scoped_query_requires_org_header(self):
        user = User.objects.create_user(email='user@example.com', password='password123')
        token = create_access_token(user=user)

        data = self._graphql(query='query { projects { id } }', token=token)
        self.assertIn('errors', data)
        self.assertEqual(data['errors'][0]['message'], 'X-Organization-ID header required')

    def test_invalid_org_header_is_rejected(self):
        user = User.objects.create_user(email='user@example.com', password='password123')
        token = create_access_token(user=user)

        data = self._graphql(query='query { projects { id } }', token=token, org_id='not-a-real-org')
        self.assertIn('errors', data)
        self.assertEqual(data['errors'][0]['message'], 'Invalid organization')

    def test_permission_enforced_on_mutations(self):
        user = User.objects.create_user(email='user@example.com', password='password123')
        org = Organization.objects.create(name='Acme', slug='acme', contact_email='billing@acme.com')
        OrganizationMember.objects.create(organization=org, user=user, role=OrganizationMember.Role.MEMBER)

        token = create_access_token(user=user)

        data = self._graphql(
            query='mutation CreateProject($name: String!) { createProject(name: $name) { project { id } } }',
            variables={'name': 'Project A'},
            token=token,
            org_id=org.id,
        )

        self.assertIn('errors', data)
        self.assertEqual(data['errors'][0]['message'], 'Permission denied')
