from pathlib import Path

import pytest


def test_subscription_structure():
    """Test that the subscription structure is correctly implemented"""
    # Test that the sites directory exists
    sites_path = Path(__file__).parent.parent / "src" / "nonebot_plugin_monitor" / "sites"
    assert sites_path.exists(), "Sites directory should exist"

    # Test that required files exist
    required_files = ["__init__.py", "base.py", "template.py"]
    for file_name in required_files:
        file_path = sites_path / file_name
        assert file_path.exists(), f"Required site file {file_name} should exist"

    # Test that the example site exists
    example_path = sites_path / "example.py"
    assert example_path.exists(), "Example site file should exist"


def test_subscription_manager_exists():
    """Test that subscription manager module exists"""
    subscription_manager_path = (
        Path(__file__).parent.parent / "src" / "nonebot_plugin_monitor" / "manager.py"
    )
    assert subscription_manager_path.exists(), "Subscription manager module should exist"


def test_subscription_handlers_exist():
    """Test that subscription handlers module exists"""
    subscription_handlers_path = (
        Path(__file__).parent.parent / "src" / "nonebot_plugin_monitor" / "handler.py"
    )
    assert subscription_handlers_path.exists(), "Subscription handlers module should exist"


def test_site_files_content():
    """Test that site files have the expected content"""
    sites_path = Path(__file__).parent.parent / "src" / "nonebot_plugin_monitor" / "sites"

    # Test base site has abstract methods
    base_content = (sites_path / "__init__.py").read_text(encoding="utf-8")
    assert "BaseSite" in base_content
    assert "fetch_latest" in base_content
    assert "has_updates" in base_content
    assert "format_notification" in base_content
    assert "get_description" in base_content
    assert "get_schedule" in base_content

    # Test base implementation has required methods
    base_impl_content = (sites_path / "base.py").read_text(encoding="utf-8")
    assert "BaseSite" in base_impl_content
    assert "load_cache" in base_impl_content
    assert "save_cache" in base_impl_content

    # Test template has expected structure
    template_content = (sites_path / "template.py").read_text(encoding="utf-8")
    assert "TemplateSite" in template_content
    assert "NOT loaded by the plugin" in template_content

    # Test example site has expected structure
    example_content = (sites_path / "example.py").read_text(encoding="utf-8")
    assert "ExampleSite" in example_content
    assert "BaseSite" in example_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
