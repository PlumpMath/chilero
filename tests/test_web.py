from aiohttp import test_utils, client, request
import asyncio
from dmonroy import web
from dmonroy.web.test import WebTestCase, asynctest
import logging

logging.basicConfig(level=logging.DEBUG)

class MultiView(web.View):

    def get(self):
        t = self.request.match_info.get('type')

        types = dict(
            plain=lambda: web.Response('Hello world!'),
            html=lambda: web.HTMLResponse('<h1>Hello world!</h1>'),
            json=lambda: web.JSONResponse(dict(hello='world!')),
            javascript=lambda: web.JavaScriptResponse('// hello world!'),
        )

        return types.get(t, 'plain')()


class TestWeb(WebTestCase):
    routes = [
        ['/{type}', MultiView]
    ]

    @asynctest
    def test_view(self):

        types = dict(
            plain=[None, 'Hello world!'],
            html=['text/html', '<h1>Hello world!</h1>'],
            javascript=['application/javascript', '// hello world!'],
            json=['text/json', '{"hello": "world!"}']
        )

        for t in types.keys():
            resp = yield from request(
                'GET', self.full_url('/{}'.format(t)), loop=self.loop
            )

            self.assertEqual(resp.status, 200)

            self.assertEqual(
                types[t][0], resp.headers.get('CONTENT-TYPE'))

            text = yield from resp.text()

            # self.assertEqual(types[t][1], text)