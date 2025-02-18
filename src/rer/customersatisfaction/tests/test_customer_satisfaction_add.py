# -*- coding: utf-8 -*-
from rer.customersatisfaction.testing import (
    RER_CUSTOMERSATISFACTION_API_FUNCTIONAL_TESTING,
)
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from rer.customersatisfaction.interfaces import ICustomerSatisfactionStore
from plone.restapi.testing import RelativeSession
from zope.component import getUtility

import transaction
import unittest


class TestCustomerSatisfactionAdd(unittest.TestCase):

    layer = RER_CUSTOMERSATISFACTION_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.user.create(
            email="memberuser@example.com",
            username="memberuser",
            password="secret",
        )

        self.document = api.content.create(
            title="Document", container=self.portal, type="Document"
        )

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.anon_api_session = RelativeSession(self.portal_url)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        self.url = "{}/@customer-satisfaction-add".format(self.document.absolute_url())
        transaction.commit()

    def tearDown(self):
        self.api_session.close()
        self.anon_api_session.close()

    def test_required_params(self):
        """ """
        # vote is required
        res = self.anon_api_session.post(self.url, json={"honey": ""})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["message"], "Campo obbligatorio mancante: vote")

    def test_validate_vote(self):
        resp = self.anon_api_session.post(
            self.url,
            json={"vote": 1, "comment": "i disagree", "honey": ""},
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["message"], "Voto non valido: 1")

    def test_correctly_save_data(self):
        self.anon_api_session.post(
            self.url,
            json={
                "vote": "ok",
                "comment": "i disagree",
                "honey": "",
            },
        )
        transaction.commit()
        tool = getUtility(ICustomerSatisfactionStore)
        self.assertEqual(len(tool.search()), 1)

    def test_store_only_known_fields(self):
        self.anon_api_session.post(
            self.url,
            json={
                "vote": "nok",
                "comment": "i disagree",
                "unknown": "mistery",
                "honey": "",
            },
        )
        transaction.commit()
        tool = getUtility(ICustomerSatisfactionStore)
        res = tool.search()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]._attrs.get("unknown", None), None)
        self.assertEqual(res[0]._attrs.get("vote", None), "nok")
        self.assertEqual(res[0]._attrs.get("comment", None), "i disagree")

    def test_honeypot_is_required(self):

        res = self.anon_api_session.post(self.url, json={})
        self.assertEqual(res.status_code, 403)

        res = self.anon_api_session.post(self.url, json={"vote": "ok"})
        self.assertEqual(res.status_code, 403)

        # HONEYPOT_FIELD is set in testing.py

        res = self.anon_api_session.post(self.url, json={"vote": "ok", "honey": ""})
        self.assertEqual(res.status_code, 204)

        # this is compiled by a bot
        res = self.anon_api_session.post(
            self.url, json={"vote": "ok", "honey": "i'm a bot"}
        )
        self.assertEqual(res.status_code, 403)
