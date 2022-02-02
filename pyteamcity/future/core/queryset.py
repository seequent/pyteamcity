import itertools

import requests

from .. import exceptions
from .locator import Locator


class QuerySet(object):
    base_url = None
    _entity_factory = None

    def __init__(self, teamcity):
        self.teamcity = teamcity
        self.base_url = self.teamcity.base_url + self.__class__.uri
        self._locator = Locator()
        self._data_dict = {}

    def _add_pred(self, name, value):
        return self._locator.add_pred(name, value)

    def _get_url(self, details=False, href=None):
        if href is not None:
            return self.teamcity.base_url + href

        url = self.base_url

        locator_str = str(self._locator)
        if locator_str:
            if details:
                url += locator_str
            else:
                url += '?locator=' + locator_str

        return url

    def _fetch(self, details=False, href=None):
        self.url = self._get_url(details=details, href=href)
        res = self.teamcity.session.get(self.url)

        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 401:
                exception_class = exceptions.UnauthorizedError
            else:
                exception_class = exceptions.HTTPError
            raise exception_class(
                status_code=status_code,
                reason=str(e),
                text=e.response.text)

        data = res.json()
        return data

    def _data(self, details=False, href=None):
        if not self._data_dict:
            self._data_dict = self._fetch(details=details, href=href)

        return self._data_dict

    def fetch_all(self):
        if self._data_dict:
            return
        href = None
        while href != -1:
            # self._locator.page = (start, 50)
            page = self._fetch(href=href)
            for key, value in page.items():
                if key in self._data_dict:
                    if isinstance(value, list):
                        self._data_dict[key].extend(value)
                    elif isinstance(value, int):
                        self._data_dict[key] += value
                else:
                    self._data_dict[key] = value
            href = page.get('nextHref', -1)
        for key, value in self._data_dict.items():
            if isinstance(value, int):
                setattr(self, key, value)
        return self

    @classmethod
    def _from_dict(cls, d, query_set):
        return cls._entity_factory.from_dict(d, query_set)

    def get(self, just_url=False,
            raise_multiple_objects_returned=False,
            **kwargs):
        self.filter(**kwargs)
        if raise_multiple_objects_returned and len(self) > 1:
            raise exceptions.MultipleObjectsReturned()
        self._data_dict = None
        if just_url:
            return self._get_url(details=True)
        else:
            return self.__class__._from_dict(
                self._data(details=True), self)

    def __len__(self):
        data = self._data()
        return data.get('count', 0)

    def __next__(self):  # pragma: no cover
        return next(self.__iter__())

    next = __next__

    def __getitem__(self, index):
        try:
            return next(itertools.islice(self, index, index + 1))
        except TypeError:  # pragma: no cover
            return list(itertools.islice(
                self, index.start, index.stop, index.step))
