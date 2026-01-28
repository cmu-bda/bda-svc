import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import argparse

# Import the logic we want to test
from bda_svc import app

# ---------------------------------------------------------------------------
# Test: Input Folder Validation (get_input_folder)
# ---------------------------------------------------------------------------

def test_get_input_folder_from_cmdline(tmp_path):
    """It should use the path provided via command line if it exists."""
    # Create a real temporary folder using pytest's tmp_path fixture
    d = tmp_path / "custom_input"
    d.mkdir()

    result = app.get_input_folder(str(d))
    assert result == d

def test_get_input_folder_from_env_var(monkeypatch, tmp_path):
    """It should use the BDA_INPUT env var if no command line arg is provided."""
    d = tmp_path / "env_input"
    d.mkdir()

    # Mock the environment variable
    monkeypatch.setenv("BDA_INPUT", str(d))

    # Pass None as cmdline_path to simulate no flag used
    result = app.get_input_folder(None)
    assert result == d

def test_get_input_folder_missing_exits(tmp_path):
    """It should SystemExit if the folder does not exist."""
    missing_dir = tmp_path / "does_not_exist"

    # Verify that the app actually crashes (exits) as expected
    with pytest.raises(SystemExit) as e:
        app.get_input_folder(str(missing_dir))

    # Optional: Check the exit message contains the path
    assert str(missing_dir) in str(e.value)

# ---------------------------------------------------------------------------
# Test: File Discovery (get_input_paths)
# ---------------------------------------------------------------------------

def test_get_input_paths_finds_images(tmp_path):
    """It should find valid image extensions recursively."""
    # Setup: Create dummy files
    (tmp_path / "subfolder").mkdir()
    (tmp_path / "image1.png").touch()
    (tmp_path / "subfolder/image2.jpg").touch()
    (tmp_path / "ignore_me.txt").touch()

    files = app.get_input_paths(tmp_path)

    # Should find the 2 images, ignore the text file
    assert len(files) == 2
    # Convert paths to filenames for easier checking
    filenames = [f.name for f in files]
    assert "image1.png" in filenames
    assert "image2.jpg" in filenames

def test_get_input_paths_empty_exits(tmp_path):
    """It should SystemExit if the folder has no valid images."""
    # Folder exists but is empty
    with pytest.raises(SystemExit):
        app.get_input_paths(tmp_path)

# ---------------------------------------------------------------------------
# Test: Main Integration (main)
# ---------------------------------------------------------------------------

@patch("bda_svc.app.VLM")  # Mock the ML model so we don't load it
@patch("bda_svc.app.get_input_folder")
@patch("bda_svc.app.get_input_paths")
@patch("bda_svc.app.get_args")
def test_main_workflow(mock_args, mock_get_folder, mock_get_paths, MockVLM):
    """It should tie the steps together: Get args -> Get Files -> Run VLM."""

    # 1. Setup Mocks
    mock_args.return_value = argparse.Namespace(input="some/path")
    mock_get_folder.return_value = Path("dummy/path")
    mock_get_paths.return_value = [Path("img1.png"), Path("img2.jpg")]

    # Mock the VLM instance and its analyze method
    vlm_instance = MockVLM.return_value
    vlm_instance.analyze_image.return_value = "Detected: Tank"

    # 2. Run Main
    # We need to import argparse here or inside the function if it wasn't imported globally

    app.main()

    # 3. Assertions
    # Did we initialize the model?
    MockVLM.assert_called_once()
    # Did we process both files?
    assert vlm_instance.analyze_image.call_count == 2
    # Check specifically that we called analyze on the paths
    vlm_instance.analyze_image.assert_any_call(Path("img1.png"))