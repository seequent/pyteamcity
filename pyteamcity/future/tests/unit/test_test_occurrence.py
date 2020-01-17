
import pytest
import responses

from pyteamcity.future import exceptions, TeamCity
from pyteamcity.future.core.manager import Manager
from pyteamcity.future.test_occurrence import TestDetailQuerySet


tc = TeamCity(username='user', password='password')


def test_filter_by_build_id():
    tests = tc.tests.all().filter(build_id='101')
    assert '?locator=build:(id:101)' in tests._get_url()


def test_filter_by_status():
    tests = tc.tests.all().filter(status='FAILURE')
    assert 'status:FAILURE' in tests._get_url()
    
    
def test_detail_filter_by_build_id():
    manager = Manager(teamcity=tc,
                      query_set_factory=TestDetailQuerySet)
    test_detail = manager.all().filter(build_id='101')
    assert 'build:(id:101)' in test_detail._get_url()
    
    
def test_detail_filter_by_test_id():
    manager = Manager(teamcity=tc,
                      query_set_factory=TestDetailQuerySet)
    test_detail = manager.all().filter(test_id='102')
    assert 'id:102' in test_detail._get_url()


@responses.activate
def test_detail():
    response_json = {
        'details': 'Failure details',
        'test': '',
        'build': '',
        'status': 'FAILURE',
        'duration': '11',
        'href': 'app/rest/testOccurrences/id:200,build:(id:100)',
        'name': 'Test 200',
        'id': 'id:200,build:(id:100)',
    }
    uri = 'app/rest/testOccurrences/id:200,build:(id:100)'
    responses.add(
        responses.GET,
        tc.relative_url(uri),
        json=response_json, status=200,
        content_type='application/json',
    )
    response_json = {
        'count': 1,
        'testOccurrence': [
            {
                'id': 'id:200,build:(id:100)',
                'name': 'Test 200',
                'status': 'FAILURE',
                'duration': '10',
                'href': '/app/rest/testOccurrences/id:200,build:(id:100)',
            },
        ],
    }
    responses.add(
        responses.GET,
        tc.relative_url('app/rest/testOccurrences/?locator=build:(id:100),status:FAILURE'),
        json=response_json, status=200,
        content_type='application/json',
    )
    tests = tc.tests.all().filter(
        build_id=100, status='FAILURE'
    )
    query_string = '?locator=build:(id:100),status:FAILURE'
    assert query_string in tests._get_url()
    for test in tests:
        assert "build_id='100' test_id='200' name='Test 200' status='FAILURE'" in repr(test)
        assert test.detail.details == 'Failure details'
        assert "name='Test 200' status='FAILURE'" in repr(test.detail)
