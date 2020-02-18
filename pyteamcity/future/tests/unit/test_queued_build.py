import datetime

import pytest
import responses

from pyteamcity.future import exceptions, TeamCity
from pyteamcity.future.build import Build
from pyteamcity.future.queued_build import QueuedBuild

tc = TeamCity()


def test_unit_all():
    queued_builds = tc.queued_builds.all()
    assert queued_builds._get_url().endswith('/app/rest/buildQueue/')


def test_unit_filter_by_project():
    queued_builds = tc.queued_builds.all().filter(
        project='Dummysvc_ReleaseToMt1',
        count=5)
    assert 'count:5' in queued_builds._get_url()
    assert 'project:(Dummysvc_ReleaseToMt1)' in queued_builds._get_url()


def test_unit_filter_by_build_type():
    build_type = 'DevOps_Metacloud_DeleteOldVMs'
    queued_builds = tc.queued_builds.all().filter(build_type=build_type)
    assert 'buildType:%s' % build_type in queued_builds._get_url()


@responses.activate
def test_unit_queued_build_with_responses():
    response_json = {
        "id": 1471658,
        "buildTypeId": "Responseweb_2_Branches_Package",
        "number": "2695",
        "status": "UNKNOWN",
        "state": "finished",
        "branchName": "preview",
        "href": "/httpAuth/app/rest/builds/id:1471658",
        "webUrl": "https://tcserver/viewLog.html"
                  "?buildId=1471658"
                  "&buildTypeId=Responseweb_2_Branches_Package",
        "statusText": "Canceled (Snapshot dependencies failed: 3 (new))",
        "buildType": {
            "id": "Responseweb_2_Branches_Package",
            "name": "package",
            "projectName": "responseweb :: branches",
            "projectId": "Responseweb_2_Branches",
            "href": "/httpAuth/app/rest/buildTypes"
                    "/id:Responseweb_2_Branches_Package",
            "webUrl": "https://tcserver/viewType.html"
                      "?buildTypeId=Responseweb_2_Branches_Package",
        },
        "canceledInfo": {
            "timestamp": "20160812T094513-0700",
            "text": "Build was canceled"
                    " because one of the builds it depends on failed",
        },
        "queuedDate": "20160812T094312-0700",
        "startDate": "20160812T094513-0700",
        "finishDate": "20160812T094513-0700",
    }
    response_list_json = {
        "count": 2,
        "href": "/httpAuth/app/rest/buildQueue/",
        "build": [
            {
                "id": 1455869,
                "buildTypeId": "Scansvc_PullRequests_Py27",
                "state": "queued",
                "branchName": "master",
                "href": "/httpAuth/app/rest/buildQueue/id:1455869",
                "webUrl": "https://tcserver/viewQueued.html?itemId=1455869",
            },
            {
                "id": 1471658,
                "buildTypeId": "Responseweb_2_Branches_Package",
                "state": "queued",
                "branchName": "master",
                "href": "/httpAuth/app/rest/buildQueue/id:1471658",
                "webUrl": "https://tcserver/viewQueued.html?itemId=1471658",
            },
        ],
    }
    response_build_type = {
        "id": "Responseweb_2_Branches_Package",
        "name": "package",
        "projectName": "responseweb :: branches",
        "projectId": "Responseweb_2_Branches",
        "href": "/httpAuth/app/rest/buildTypes"
                "/id:Responseweb_2_Branches_Package",
        "webUrl": "https://tcserver/viewType.html"
                  "?buildTypeId=Responseweb_2_Branches_Package",
    }

    responses.add(
        responses.GET,
        tc.relative_url('app/rest/buildQueue/'),
        json=response_list_json, status=200,
        content_type='application/json',
    )
    responses.add(
        responses.GET,
        tc.relative_url('app/rest/buildQueue/id:1471658'),
        json=response_json, status=200,
        content_type='application/json',
    )
    responses.add(
        responses.GET,
        tc.relative_url('app/rest/buildTypes/id:Responseweb_2_Branches_Package'),
        json=response_build_type, status=200,
        content_type='application/json',
    )

    with pytest.raises(exceptions.MultipleObjectsReturned):
        tc.queued_builds.all().get(
            branch='master',
            user='marca',
            start=2,
            lookup_limit=2,
            raise_multiple_objects_returned=True,
        )

    queued_builds = tc.queued_builds.all().filter(
        branch='master',
        user='marca',
        start=2,
        lookup_limit=2,
    )
    assert len(queued_builds) == 2
    for queued_build in queued_builds:
        assert hasattr(queued_build, 'build_type_id')
        assert hasattr(queued_build, 'branch_name')
        assert hasattr(queued_build, 'href')
        assert hasattr(queued_build, 'web_url')
    queued_build = tc.queued_builds.all().get(id=1471658)
    assert 'id=1471658' in repr(queued_build)
    assert 'Responseweb_2_Branches_Package' in repr(queued_build)
    assert isinstance(queued_build.queued_date, datetime.datetime)
    assert queued_build.queued_date.year == 2016
    assert queued_build.queued_date.month == 8
    assert queued_build.queued_date.day == 12
    assert queued_build.queued_date.hour == 9
    assert queued_build.queued_date.minute == 43
    assert queued_build.queued_date.second == 12
    assert queued_build.build_type.id == 'Responseweb_2_Branches_Package'
    assert queued_build.build_type.name == 'package'


@responses.activate
def test_trigger_build_with_responses():
    expected_raw_value = "".join([
        "password ",
        "display='hidden' ",
        "label='ansible_vault_password'",
    ])
    response_json = {
        "id": 1473600,
        "buildTypeId": "Dummysvc_Branches_Py27",
        "state": "queued",
        "branchName": "<default>",
        "defaultBranch": True,
        "href": "/guestAuth/app/rest/buildQueue/id:1473600",
        "webUrl": "https://tcserver/viewQueued.html?itemId=1473600",
        "buildType": {
            "id": "Dummysvc_Branches_Py27",
            "name": "py27",
            "projectName": "dummysvc :: branches",
            "projectId": "Dummysvc_Branches",
            "href": "/guestAuth/app/rest/buildTypes"
                    "/id:Dummysvc_Branches_Py27",
            "webUrl": "https://tcserver/viewType.html"
                      "?buildTypeId=Dummysvc_Branches_Py27",
        },
        "waitReason": "Waiting to start checking for changes",
        "queuedDate": "20160812T154256-0700",
        "triggered": {
            "type": "user",
            "date": "20160812T154256-0700",
            "user": {
                "username": "marca",
                "name": "Marc Abramowitz",
                "id": 16,
                "href": "/guestAuth/app/rest/users/id:16",
            },
        },
        "properties": {
            "count": 2,
            "property": [
                {
                    "name": "env.PIP_USE_WHEEL",
                    "value": "true",
                },
                {
                    "name": "env.PIP_WHEEL_DIR",
                    "value": "/tmp/wheelhouse",
                },
                {
                    'name': 'env.ANSIBLE_VAULT_PASSWORD',
                    'type': {'rawValue': expected_raw_value},
                },
            ],
        }
    }
    response_build_type = {
        "id": "Dummysvc_Branches_Py27",
        "name": "py27",
        "projectName": "dummysvc :: branches",
        "projectId": "Dummysvc_Branches",
        "href": "/guestAuth/app/rest/buildTypes"
                "/id:Dummysvc_Branches_Py27",
        "webUrl": "https://tcserver/viewType.html"
                  "?buildTypeId=Dummysvc_Branches_Py27",
    }

    # Response to triggering a build
    responses.add(
        responses.POST,
        tc.relative_url('app/rest/buildQueue/'),
        json=response_json, status=200,
        content_type='application/json',
    )
    # Response to canceling a build
    responses.add(
        responses.POST,
        tc.relative_url('app/rest/buildQueue/id:1473600'),
        status=500,
    )
    # Response to build type
    responses.add(
        responses.GET,
        tc.relative_url('app/rest/buildTypes/id:Dummysvc_Branches_Py27'),
        json=response_build_type, status=200,
        content_type='application/json'
    )

    queued_build = tc.queued_builds.all().trigger_build(
        build_type_id='Dummysvc_Branches_Py27',
        branch='master',
        agent_id=70,
        comment='just testing',
        parameters={'env.PIP_USE_WHEEL': 'true',
                    'env.PIP_WHEEL_DIR': '/tmp/wheelhouse'},
    )
    assert isinstance(queued_build.id, int)
    assert 'viewQueued.html' in queued_build.web_url
    assert queued_build.user.username == 'marca'
    assert isinstance(queued_build.queued_date, datetime.datetime)
    assert queued_build.build_type_id == 'Dummysvc_Branches_Py27'
    assert queued_build.build_type.name == 'py27'
    assert queued_build.build_type.id == 'Dummysvc_Branches_Py27'
    params = queued_build.parameters_dict
    assert params['env.PIP_USE_WHEEL'].value == 'true'
    assert params['env.PIP_WHEEL_DIR'].value == '/tmp/wheelhouse'

    # Now test canceling the build
    with pytest.raises(exceptions.HTTPError):
        queued_build.cancel(comment='This is a test')

    # Make sure that the origin field is set correctly.
    assert responses.calls[3].request.headers['origin'] == 'http://127.0.0.1'

    # Test case where build node has no build_attributes
    queued_build = tc.queued_builds.all().trigger_build(
        build_type_id='Dummysvc_Branches_Py27',
    )
    assert isinstance(queued_build.id, int)
    assert 'viewQueued.html' in queued_build.web_url
    assert queued_build.user.username == 'marca'
    assert isinstance(queued_build.queued_date, datetime.datetime)
    assert queued_build.build_type_id == 'Dummysvc_Branches_Py27'
    assert queued_build.build_type.name == 'py27'
    assert queued_build.build_type.id == 'Dummysvc_Branches_Py27'
    assert queued_build.branch_name == '<default>'
    params = queued_build.parameters_dict
    assert params['env.PIP_USE_WHEEL'].value == 'true'
    assert params['env.PIP_WHEEL_DIR'].value == '/tmp/wheelhouse'

    # Now test canceling the build
    with pytest.raises(exceptions.HTTPError):
        queued_build.cancel(comment='This is a test')


@responses.activate
def test_trigger_build_exception_with_responses():
    responses.add(
        responses.POST,
        tc.relative_url('app/rest/buildQueue/'),
        status=500,
    )

    with pytest.raises(exceptions.HTTPError):
        tc.queued_builds.all().trigger_build(
            build_type_id='Dummysvc_Branches_Py27',
        )


@responses.activate
def test_snapshot_dependencies():
    expected_raw_value = "".join([
        "password ",
        "display='hidden' ",
        "label='ansible_vault_password'",
    ])
    response_json_trigger_build = {
        "id": 553267,
        "buildTypeId": "Dummysvc_Branches_Py27",
        "state": "queued",
        "branchName": "<default>",
        "defaultBranch": True,
        "href": "/guestAuth/app/rest/buildQueue/id:1473600",
        "webUrl": "https://tcserver/viewQueued.html?itemId=1473600",
        "buildType": {
            "id": "Dummysvc_Branches_Py27",
            "name": "py27",
            "projectName": "dummysvc :: branches",
            "projectId": "Dummysvc_Branches",
            "href": "/guestAuth/app/rest/buildTypes"
                    "/id:Dummysvc_Branches_Py27",
            "webUrl": "https://tcserver/viewType.html"
                      "?buildTypeId=Dummysvc_Branches_Py27",
        },
        "waitReason": "Waiting to start checking for changes",
        "queuedDate": "20160812T154256-0700",
        "triggered": {
            "type": "user",
            "date": "20160812T154256-0700",
            "user": {
                "username": "marca",
                "name": "Marc Abramowitz",
                "id": 16,
                "href": "/guestAuth/app/rest/users/id:16",
            },
        },
        "properties": {
            "count": 2,
            "property": [
                {
                    "name": "env.PIP_USE_WHEEL",
                    "value": "true",
                },
                {
                    "name": "env.PIP_WHEEL_DIR",
                    "value": "/tmp/wheelhouse",
                },
                {
                    'name': 'env.ANSIBLE_VAULT_PASSWORD',
                    'type': {'rawValue': expected_raw_value},
                },
            ],
        }
    }

    # Response to triggering a build
    responses.add(
        responses.POST,
        tc.relative_url('app/rest/buildQueue/'),
        json=response_json_trigger_build, status=200,
        content_type='application/json',
    )

    response_json_snapshot_dependencies = {
        "count": 3,
        "href": "/app/rest/builds?locator=snapshotDependency:(to:(id:553267),includeInitial:true),defaultFilter:false",
        "build": [
            {
                "id": 553267,
                "buildTypeId": "Dummysvc_Branches_Py27",
                "number": "2695",
                "status": "UNKNOWN",
                "state": "queued",
                "branchName": "<default>",
                "defaultBranch": True,
                "href": "/app/rest/builds/id:553267",
                "webUrl": "http://tcserver/viewLog.html?buildId=553267&buildTypeId=Dummysvc_Branches_Py27"
            },
            {
                "id": 553266,
                "buildTypeId": "Some_Snapshot_Dependency",
                "number": "2695",
                "status": "UNKNOWN",
                "state": "running",
                "branchName": "<default>",
                "defaultBranch": True,
                "href": "/app/rest/builds/id:553266",
                "webUrl": "http://tcserver/viewLog.html?buildId=553266&buildTypeId=Some_Snapshot_Dependency"
            },
            {
                "id": 553264,
                "buildTypeId": "Some_Other_Snapshot_Dependency",
                "number": "2695",
                'queuedDate': '20160810T172739-0700',
                'startDate': '20160810T172741-0700',
                'finishDate': '20160810T172802-0700',
                "status": "SUCCESS",
                "state": "finished",
                "branchName": "<default>",
                "defaultBranch": True,
                "href": "/app/rest/builds/id:553264",
                "webUrl": "http://tcserver/viewLog.html?buildId=553264&buildTypeId=Some_Other_Snapshot_Dependency"
            },
        ]
    }

    responses.add(
        responses.GET,
        tc.relative_url(
            'app/rest/builds?locator=snapshotDependency:(to:(id:553267),includeInitial:true),defaultFilter:false'
        ),
        json=response_json_snapshot_dependencies, status=200,
        content_type='application/json',
    )

    queued_build = tc.queued_builds.all().trigger_build(
        build_type_id='Dummysvc_Branches_Py27',
        branch='master',
        agent_id=70,
        comment='just testing',
        parameters={'env.PIP_USE_WHEEL': 'true',
                    'env.PIP_WHEEL_DIR': '/tmp/wheelhouse'},
    )

    snapshot_dependencies = queued_build.get_snapshot_dependencies()

    assert len(snapshot_dependencies) == 3
    assert _queued_builds_equal(snapshot_dependencies[0], QueuedBuild.from_dict({
                "id": 553267,
                "buildTypeId": "Dummysvc_Branches_Py27",
                "number": "2695",
                "status": "UNKNOWN",
                "state": "queued",
                "branchName": "<default>",
                "defaultBranch": True,
                "href": "/app/rest/builds/id:553267",
                "webUrl": "http://tcserver/viewLog.html?buildId=553267&buildTypeId=Dummysvc_Branches_Py27"
            }, teamcity=tc))
    assert _queued_builds_equal(snapshot_dependencies[1], QueuedBuild.from_dict({
                "id": 553266,
                "buildTypeId": "Some_Snapshot_Dependency",
                "number": "2695",
                "status": "UNKNOWN",
                "state": "running",
                "branchName": "<default>",
                "defaultBranch": True,
                "href": "/app/rest/builds/id:553266",
                "webUrl": "http://tcserver/viewLog.html?buildId=553266&buildTypeId=Some_Snapshot_Dependency"
            }, teamcity=tc))
    assert _builds_equal(snapshot_dependencies[2], Build.from_dict({
                "id": 553264,
                "buildTypeId": "Some_Other_Snapshot_Dependency",
                "number": "2695",
                'queuedDate': '20160810T172739-0700',
                'startDate': '20160810T172741-0700',
                'finishDate': '20160810T172802-0700',
                "status": "SUCCESS",
                "state": "finished",
                "branchName": "<default>",
                "defaultBranch": True,
                "href": "/app/rest/builds/id:553264",
                "webUrl": "http://tcserver/viewLog.html?buildId=553264&buildTypeId=Some_Other_Snapshot_Dependency"
            }, teamcity=tc))


def _builds_equal(a, b):
    ''' Tests if two Builds are equal, ignoring build_query_set
    '''
    if not isinstance(a, Build):
        return False
    if not isinstance(b, Build):
        return False

    attrs = [
        'id',
        'number',
        'queued_date_string',
        'start_date_string',
        'finish_date_string',
        'build_type_id',
        'state',
        'status',
        'branch_name',
        'href',
        'build_query_set',
        'teamcity',
        ]

    trues = [
        getattr(a, attr) == getattr(b, attr) for attr in attrs
    ]

    return all(trues)


def _queued_builds_equal(a, b):
    ''' Tests if two QueuedBuilds are equal, ignoring build_query_set
    '''

    if not isinstance(a, QueuedBuild):
        return False
    if not isinstance(b, QueuedBuild):
        return False

    attrs = [
        'id',
        'build_type_id',
        'queued_date_string',
        'branch_name',
        'href',
        'web_url',
        'teamcity',
        ]

    trues = [
        getattr(a, attr) == getattr(b, attr) for attr in attrs
    ]

    return all(trues)
