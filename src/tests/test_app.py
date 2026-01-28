# tests/test_app.py

from bda_svc.app import main

def test_app_starts():
    """A simple test to ensure the app structure exists."""
    # This doesn't actually run the full app, it just checks
    # if we can import it without crashing.
    assert callable(main)