from .build_type import BuildType
from .core.parameter import Parameter
from .core.queryset import QuerySet
from .core.web_browsable import WebBrowsable
from .core.utils import raise_on_status


class Project(WebBrowsable):
    def __init__(self, id, name, description,
                 href, web_url, parent_project_id,
                 teamcity, project_query_set,
                 data_dict=None):
        self.id = id
        self.name = name
        self.description = description
        self.href = href
        self.web_url = web_url
        self.parent_project_id = parent_project_id
        self.teamcity = teamcity
        self.project_query_set = project_query_set
        if self.teamcity is None and self.project_query_set is not None:
            self.teamcity = self.project_query_set.teamcity
        self._data_dict = data_dict

    def __repr__(self):
        return '<%s.%s: id=%r name=%r>' % (
            self.__module__,
            self.__class__.__name__,
            self.id,
            self.name)

    @classmethod
    def from_dict(cls, d, project_query_set=None, teamcity=None):
        return Project(
            id=d.get('id'),
            name=d.get('name'),
            description=d.get('description'),
            href=d.get('href'),
            web_url=d.get('webUrl'),
            parent_project_id=d.get('parentProjectId'),
            project_query_set=project_query_set,
            teamcity=teamcity,
            data_dict=d)

    @property
    def build_types(self):
        from .build_type import BuildTypeQuerySet

        teamcity = self.project_query_set.teamcity
        return BuildTypeQuerySet(teamcity).filter(project_id=self.id)

    @property
    def projects(self):
        teamcity = self.project_query_set.teamcity
        project_query_set = ProjectQuerySet(teamcity)
        project_query_set._data_dict = self._data_dict['projects']
        return project_query_set

    @property
    def parent_project(self):
        teamcity = self.project_query_set.teamcity
        return ProjectQuerySet(teamcity).get(id=self.parent_project_id)

    @property
    def parameters_dict(self):
        d = {}

        for param in self._data_dict['parameters']['property']:
            param_obj = Parameter()
            if 'value' in param:
                param_obj.value = param['value']
            if 'type' in param:
                param_obj.ptype = param['type']
            d[param['name']] = param_obj

        return d

    def delete(self):
        url = self.teamcity.base_base_url + self.href
        res = self.teamcity.session.delete(url)
        raise_on_status(res)

    def create_build_type(self, name):
        """
        Add an empty build type with name `name` to the project
        """

        url = self.teamcity.base_base_url + self.href + '/buildTypes'
        res = self.teamcity.session.post(
            url=url,
            headers={'Content-Type': 'text/plain'},
            data=name)
        raise_on_status(res)
        build_type = BuildType.from_dict(res.json(), teamcity=self.teamcity)
        return build_type

    def set_description(self, description):
        url = self.teamcity.base_base_url + self.href + '/description'
        res = self.teamcity.session.put(
            url=url,
            headers={'Content-Type': 'text/plain',
                     'Accept': 'text/plain'},
            data=description)
        raise_on_status(res)


class ProjectQuerySet(QuerySet):
    uri = '/app/rest/projects/'
    _entity_factory = Project

    def filter(self, id=None, name=None):
        if id is not None:
            self._add_pred('id', id)
        if name is not None:
            self._add_pred('name', name)
        return self

    def __iter__(self):
        return (Project.from_dict(d, self) for d in self._data()['project'])

    def create(self, name, id=None, parent_project_locator='id:_Root', source_project_locator=None):
        """ source_project_locator is an optional locator string of the project to create a copy of. """
        url = self.base_url
        attrs_dict = {'name': name}
        if id is not None:
            attrs_dict['id'] = id
        attrs = ' '.join([
            '%s="%s"' % (k, v) for k, v in attrs_dict.items()
        ])
        xml = f"""
              <newProjectDescription {attrs}>
                {f"<sourceProject locator='{source_project_locator}'/>" if source_project_locator is not None else ""}
                <parentProject locator='{parent_project_locator}'/>
              </newProjectDescription>
              """
        res = self.teamcity.session.post(
            url=url,
            headers={'Content-Type': 'application/xml'},
            allow_redirects=False,
            data=xml)
        raise_on_status(res)
        project = Project.from_dict(res.json(), teamcity=self.teamcity)
        return project
