from .core.parameter import Parameter
from .core.queryset import QuerySet
from .core.utils import raise_on_status


class BuildType(object):
    def __init__(self, id, name, description, href, web_url,
                 project_id, project_name,
                 paused, template_flag,
                 teamcity, build_type_query_set, data_dict=None):
        self.id = id
        self.name = name
        self.description = description
        self.href = href
        self.web_url = web_url
        self.project_id = project_id
        self.project_name = project_name
        self.paused = paused
        self.template_flag = template_flag
        self.teamcity = teamcity
        self.build_type_query_set = build_type_query_set
        if self.teamcity is None and self.build_type_query_set is not None:
            self.teamcity = self.build_type_query_set.teamcity
        self._data_dict = data_dict

    def __repr__(self):
        return '<%s.%s: id=%r name=%r project_name=%r>' % (
            self.__module__,
            self.__class__.__name__,
            self.id,
            self.name,
            self.project_name)

    @classmethod
    def from_dict(cls, d, build_type_query_set=None, teamcity=None):
        return BuildType(
            id=d.get('id'),
            name=d.get('name'),
            description=d.get('description'),
            href=d.get('href'),
            web_url=d.get('webUrl'),
            project_id=d.get('projectId'),
            project_name=d.get('projectName'),
            paused=d.get('paused'),
            template_flag=d.get('templateFlag'),
            build_type_query_set=build_type_query_set,
            teamcity=teamcity,
            data_dict=d)

    @property
    def project(self):
        from .project import ProjectQuerySet

        teamcity = self.teamcity
        return ProjectQuerySet(teamcity).get(id=self.project_id)

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

    def set_paused(self, bool):
        url = self.teamcity.base_base_url + self.href + '/paused'
        res = self.teamcity.session.put(
            url=url,
            headers={'Content-Type': 'text/plain',
                     'Accept': 'text/plain'},
            data='true' if bool else 'false')
        raise_on_status(res)

    def reset_build_counter(self, counter):
        url = ''.join([
            self.teamcity.base_base_url,
            self.href,
            '/settings/buildNumberCounter'])
        res = self.teamcity.session.put(
            url=url,
            headers={'Content-Type': 'text/plain',
                     'Accept': 'text/plain'},
            data=str(counter))
        raise_on_status(res)

    def get_triggers(self):
        url = ''.join([
            self.teamcity.base_base_url,
            self.href,
            '/triggers'])
        res = self.teamcity.session.get(
            url,
            headers={'Content-Type': 'application/xml'}
        )
        raise_on_status(res)
        json = res.json()
        triggers = json.get('trigger', [])
        return triggers

    def get_trigger(self, trigger_locator):
        url = ''.join([
            self.teamcity.base_base_url,
            self.href,
            f'/triggers/{trigger_locator}'])
        res = self.teamcity.session.get(
            url,
            headers={'Content-Type': 'application/xml'}
        )
        raise_on_status(res)
        return res.json()

    def set_trigger(self, trigger_locator, trigger_data):
        url = ''.join([
            self.teamcity.base_base_url,
            self.href,
            f'/triggers/{trigger_locator}'])
        res = self.teamcity.session.put(
            url=url,
            headers={'Content-Type': 'text/plain'},
            data=trigger_data)
        raise_on_status(res)

    def set_trigger_property(self, trigger_locator, property_name, property_value):
        trigger_data = self.get_trigger(trigger_locator)
        trigger_properties = trigger_data['properties']['property']
        for i, prop in enumerate(trigger_properties):
            if prop['name'] == property_name:
                # Update the value of the existing property
                prop['value'] = property_value
                break
        else:
            # No existing property with name found, append a new property
            trigger_properties.append({'name': property_name, 'value': property_value})
        self.set_trigger(trigger_locator, str(trigger_data))

    def delete(self):
        url = self.teamcity.base_base_url + self.href
        res = self.teamcity.session.delete(url)
        raise_on_status(res)


class BuildTypeQuerySet(QuerySet):
    uri = '/app/rest/buildTypes/'
    _entity_factory = BuildType

    def filter(self, id=None, name=None,
               project_id=None, affected_project_id=None,
               paused=None, template_id=None, template_flag=None):
        if id is not None:
            self._add_pred('id', id)
        if name is not None:
            self._add_pred('name', name)
        if project_id is not None:
            self._add_pred('project', '(id:%s)' % project_id)
        if affected_project_id is not None:
            self._add_pred('affectedProject',
                           '(id:%s)' % affected_project_id)
        if paused is not None:
            self._add_pred('paused', paused)
        if template_id is not None:
            self._add_pred('template', '(id:%s)' % template_id)
        if template_flag is not None:
            self._add_pred('templateFlag', template_flag)
        return self

    def __iter__(self):
        return (BuildType.from_dict(d, self)
                for d in self._data()['buildType'])
