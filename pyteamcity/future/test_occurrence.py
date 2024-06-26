
import re

from .core.queryset import QuerySet


class Test(object):
    def __init__(self, id, name, status, muted, duration, href,
                 test_query_set, teamcity, data_dict=None):
        try:
            self.build_id, self.test_id = re.match('build:\(id:(\d+)\),id:(\d+)', id).groups()
        except AttributeError:
            self.test_id, self.build_id = re.match('id:(\d+),build:\(id:(\d+)\)', id).groups()
        self.name = name
        self.status = status
        self.muted = muted
        self.duration = duration
        self.href = href
        self.test_query_set = test_query_set
        self.teamcity = teamcity
        if self.teamcity is None and self.test_query_set is not None:
            self.teamcity = self.test_query_set.teamcity
        self._data_dict = data_dict

    def __repr__(self):
        return '<%s.%s: build_id=%r test_id=%r name=%r status=%r muted=%r>' % (
            self.__module__,
            self.__class__.__name__,
            self.build_id,
            self.test_id,
            self.name,
            self.status,
            self.muted)

    @classmethod
    def from_dict(cls, d, test_query_set=None, teamcity=None):
        return Test(
            id=d.get('id'),
            name=d.get('name'),
            status=d.get('status'),
            muted=d.get('muted'),
            duration=d.get('duration'),
            href=d.get('href'),
            test_query_set=test_query_set,
            teamcity=teamcity,
            data_dict=d)

    @property
    def detail(self):
        detail = TestDetailQuerySet(self.teamcity).get(test_id=self.test_id, 
                                                       build_id=self.build_id)
        return detail


class TestQuerySet(QuerySet):
    uri = '/app/rest/testOccurrences/'
    _entity_factory = Test

    def filter(self,
               build_id=None, status=None):
        if build_id is not None:
            self._add_pred('build', f'(id:{build_id})')
        if status is not None:
            self._add_pred('status', status)
        return self

    def __iter__(self):
        try:
            return (Test.from_dict(d, self, teamcity=self.teamcity)
                    for d in self._data()['testOccurrence'])
        except KeyError:
            return iter(())
        

class TestDetail(object):
    def __init__(self, id, name, status, muted, duration, href, details, ignore_details,
                 test, build, test_detail_query_set, teamcity, data_dict=None):
        self.id = id
        self.name = name
        self.status = status
        self.muted = muted
        self.duration = duration
        self.href = href
        self.details = details
        self.ignore_details = ignore_details
        self.test_detail_query_set = test_detail_query_set
        self.teamcity = teamcity
        if self.teamcity is None and self.test_detail_query_set is not None:
            self.teamcity = self.test_detail_query_set.teamcity
        self.build = build
        self.test = test
        self._data_dict = data_dict

    def __repr__(self):
        return '<%s.%s: id=%r name=%r status=%r muted=%r>' % (
            self.__module__,
            self.__class__.__name__,
            self.id,
            self.name,
            self.status,
            self.muted)

    @classmethod
    def from_dict(cls, d, test_detail_query_set=None, teamcity=None):
        return TestDetail(
            id=d.get('id'),
            name=d.get('name'),
            status=d.get('status'),
            muted=d.get('muted'),
            duration=d.get('duration'),
            href=d.get('href'),
            details=d.get('details'),
            ignore_details=d.get('ignore_details'),
            test=d.get('test'),
            build=d.get('build'),
            test_detail_query_set=test_detail_query_set,
            teamcity=teamcity,
            data_dict=d)


class TestDetailQuerySet(QuerySet):
    uri = '/app/rest/testOccurrences/'
    _entity_factory = TestDetail
    
    def filter(self,
               test_id=None, build_id=None):
        if test_id is not None:
            self._add_pred('id', test_id)
        if build_id is not None:
            self._add_pred('build', f'(id:{build_id})')
        return self
