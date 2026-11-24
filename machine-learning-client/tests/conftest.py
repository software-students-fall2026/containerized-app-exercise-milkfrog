"""Fixtures"""

import pytest


from client import create_app


@pytest.fixture(name="app")
def fixture_app():
    """Build app"""

    return create_app()


@pytest.fixture(name="client")
def fixture_client(app):
    """Give a test client"""
    return app.test_client()
