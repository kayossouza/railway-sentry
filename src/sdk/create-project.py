"""Acceptance-only fixture; execute within Web in the throwaway project."""
import json
import os
from sentry.runner import configure
configure()
from sentry.models.organization import Organization
from sentry.models.organizationmember import OrganizationMember
from sentry.models.team import Team
from sentry.models.project import Project
from sentry.models.projectkey import ProjectKey
from sentry.models.apitoken import ApiToken
from sentry.users.models.user import User

user=User.objects.get(email=os.environ['ADMIN_EMAIL'])
org,_=Organization.objects.get_or_create(slug='bounty-test', defaults={'name':'Bounty test'})
OrganizationMember.objects.get_or_create(organization=org,user_id=user.id, defaults={'role':'owner','user_email':user.email,'user_is_active':True})
team,_=Team.objects.get_or_create(organization=org,slug='bounty',defaults={'name':'Bounty'})
project,_=Project.objects.get_or_create(organization=org,slug='sdk',defaults={'name':'SDK','platform':'python'})
project.add_team(team)
key=ProjectKey.objects.filter(project=project).first() or ProjectKey.objects.create(project=project)
token=ApiToken.objects.create(user=user,scope_list=['org:read','project:read','event:read'])
print('ACCEPTANCE_JSON='+json.dumps({'public_key':key.public_key,'project_id':project.id,'token':token.token,'org':org.slug}))
