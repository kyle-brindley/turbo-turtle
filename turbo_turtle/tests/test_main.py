from unittest.mock import patch

import pytest

from turbo_turtle import main
from turbo_turtle import _settings


def test_docs():
    """Test the docs subcommand behavior"""
    with patch("webbrowser.open") as mock_webbrowser_open, \
         patch("pathlib.Path.exists", return_value=True):
        main._docs()
        # Make sure the correct type is passed to webbrowser.open
        mock_webbrowser_open.assert_called_with(str(_settings._installed_docs_index))

    with patch("webbrowser.open") as mock_webbrowser_open, \
         patch("pathlib.Path.exists", return_value=True):
        main._docs(print_local_path=True)
        mock_webbrowser_open.assert_not_called()

    # Test the "unreachable" exit code used as a sign-of-life that the installed package structure assumptions in
    # _settings.py are correct.
    with patch("webbrowser.open") as mock_webbrowser_open, \
         patch("pathlib.Path.exists", return_value=False), \
         pytest.raises(SystemExit):
        main._docs(print_local_path=True)
        mock_webbrowser_open.assert_not_called()

def test_print_abaqus_module(capsys):
    """Test the print-abaqus-module subcommand behavior"""
    fake_subcommand = "fake_subcommand"
    fake_subcommand_list = [fake_subcommand]
    
    # Test printing behavior
    expected_output = f"{_settings._abaqus_python_abspath}/{fake_subcommand}.py\n"
    main._print_abaqus_module_location(fake_subcommand, fake_subcommand_list)
    returned_output = capsys.readouterr()
    assert expected_output == returned_output.out
    
    # Test the vaildation of the provided subcommand with subcommand list
    with patch("turbo_turtle._abaqus_python._mixed_utilities.sys_exit") as mock_sys_exit, \
         pytest.raises(SystemExit):
        another_fake_subcommand = "another_fake_subcommand"
        main._print_abaqus_module_location(another_fake_subcommand, fake_subcommand_list)
        mock_sys_exit.assert_called()
