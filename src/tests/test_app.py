import pytest
from pathlib import Path
from bda_svc import app

def test_uses_command_line_path(tmp_path):
    """If a valid path is passed as an argument, use it."""
    # tmp_path is a built-in pytest fixture that creates a temporary folder
    real_folder = tmp_path / "my_test_images"
    real_folder.mkdir()

    # Run the function with the string version of that path
    result = app.get_input_folder(str(real_folder))

    # Assert it returned the correct Path object
    assert result == real_folder

def test_uses_env_var_if_no_arg(monkeypatch, tmp_path):
    """If arg is None, it should look at the BDA_INPUT environment variable."""
    env_folder = tmp_path / "env_images"
    env_folder.mkdir()

    # 'monkeypatch' lets us safely fake environment variables just for this test
    monkeypatch.setenv("BDA_INPUT", str(env_folder))

    # Pass None to simulate no command line flag being used
    result = app.get_input_folder(None)

    assert result == env_folder

def test_exits_if_folder_missing():
    """If the folder doesn't exist, the program should SystemExit."""
    bad_path = "/this/path/definitely/does/not/exist"

    # bda_svc.app uses sys.exit(), so we must catch it or the test crashes
    with pytest.raises(SystemExit):
        app.get_input_folder(bad_path)