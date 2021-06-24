# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from zope.component import getUtility
from rer.customersatisfaction.interfaces import ICustomerSatisfactionStore
from plone import api
from Products.CMFPlone.PloneBatch import Batch

# -*- coding: utf-8 -*-
from plone import api
from plone.memoize import ram
from plone.protect.authenticator import createToken
from Products.Five import BrowserView
from time import time


import pkg_resources

JS_TEMPLATE = "{portal_url}/++plone++rer.customersatisfaction/react/dist/{env_mode}/{name}.js?v={version}"  # noqa
CSS_TEMPLATE = "{portal_url}/++plone++rer.customersatisfaction/react/dist/{env_mode}/{name}.css?v={version}"  # noqa


class View(BrowserView):
    """ """

    @ram.cache(lambda *args: time() // (60 * 60))
    def get_version(self):
        return pkg_resources.get_distribution(
            "rer.customersatisfaction"
        ).version

    def get_env_mode(self):
        return (
            api.portal.get_registry_record("plone.resources.development")
            and "dev"  # noqa
            or "prod"  # noqa
        )

    def get_resource_js(self, name="history"):
        return JS_TEMPLATE.format(
            portal_url=api.portal.get().absolute_url(),
            env_mode=self.get_env_mode(),
            name=name,
            version=self.get_version(),
        )

    def get_resource_css(self, name="history"):
        return CSS_TEMPLATE.format(
            portal_url=api.portal.get().absolute_url(),
            env_mode=self.get_env_mode(),
            name=name,
            version=self.get_version(),
        )

    def get_token(self):
        return createToken()
