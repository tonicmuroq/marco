import json
import unittest

import marco.app
from marco.ext.openid2_ext import OpenID2User


class AjaxTest(unittest.TestCase):
    def test_metrics(self):
        app = marco.app.create_app()
        with app.test_client() as c:
            c.set_cookie('localhost', 'PROFILE_COOKIE_NAME',
                         json.dumps({'username': 'tonic'}))
            r = c.get("/ajax/app/49/metrics?metric_name=notexists").data
            self.assertEqual(0, len(json.loads(r)['data'][0]['values']))

            r = c.get("/ajax/app/49/metrics?metric_name=' or ''='").data
            self.assertEqual(0, len(json.loads(r)['data'][0]['values']))
