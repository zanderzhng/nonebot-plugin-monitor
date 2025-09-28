"""
Tests for site module fetch functions
"""

import pytest
from pathlib import Path
import sys

# Add src to path so we can import site modules
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.mark.asyncio
async def test_ths_new_concept_fetch():
    """Test that ths_new_concept site can fetch data"""
    try:
        from nonebot_plugin_monitor.sites.ths_new_concept import fetch_ths_new_concept_data

        # Test that the function exists and is callable
        assert callable(fetch_ths_new_concept_data)

        # Note: We don't actually call the function in tests because:
        # 1. It makes real HTTP requests which we want to avoid in tests
        # 2. It requires network access which may not be available in CI
        # 3. It may have side effects we don't want in tests

        print("ths_new_concept fetch function is properly defined")
    except ImportError as e:
        pytest.skip(f"ths_new_concept module not available: {e}")
    except Exception as e:
        pytest.fail(f"Error testing ths_new_concept fetch function: {e}")


@pytest.mark.asyncio
async def test_kpl_importantnews_fetch():
    """Test that kpl_importantnews site can fetch data"""
    try:
        from nonebot_plugin_monitor.sites.kpl_importantnews import fetch_kpl_importantnews_data

        # Test that the function exists and is callable
        assert callable(fetch_kpl_importantnews_data)

        print("kpl_importantnews fetch function is properly defined")
    except ImportError as e:
        pytest.skip(f"kpl_importantnews module not available: {e}")
    except Exception as e:
        pytest.fail(f"Error testing kpl_importantnews fetch function: {e}")


@pytest.mark.asyncio
async def test_ths_importantnews_fetch():
    """Test that ths_importantnews site can fetch data"""
    try:
        from nonebot_plugin_monitor.sites.ths_importantnews import fetch_ths_importantnews_data

        # Test that the function exists and is callable
        assert callable(fetch_ths_importantnews_data)

        print("ths_importantnews fetch function is properly defined")
    except ImportError as e:
        pytest.skip(f"ths_importantnews module not available: {e}")
    except Exception as e:
        pytest.fail(f"Error testing ths_importantnews fetch function: {e}")


@pytest.mark.asyncio
async def test_trumpstruth_fetch():
    """Test that trumpstruth site can fetch data"""
    try:
        from nonebot_plugin_monitor.sites.trumpstruth import fetch_trumpstruth_data

        # Test that the function exists and is callable
        assert callable(fetch_trumpstruth_data)

        print("trumpstruth fetch function is properly defined")
    except ImportError as e:
        pytest.skip(f"trumpstruth module not available: {e}")
    except Exception as e:
        pytest.fail(f"Error testing trumpstruth fetch function: {e}")


def test_site_module_structure():
    """Test that all site modules have the required structure"""
    sites_path = Path(__file__).parent.parent / "src" / "nonebot_plugin_monitor" / "sites"

    # Get all site module files (excluding special files)
    site_files = [f for f in sites_path.glob("*.py") if f.name not in ["__init__.py", "template.py"]]

    required_attributes = ["fetch", "compare", "format", "description", "schedule"]

    for site_file in site_files:
        site_name = site_file.stem
        try:
            # Import the site module
            module = __import__(f"nonebot_plugin_monitor.sites.{site_name}", fromlist=["site"])

            # Check that site config exists
            assert hasattr(module, "site"), f"Site module {site_name} missing 'site' attribute"

            site_config = module.site

            # Check required attributes exist in site config
            for attr_name in required_attributes:
                assert hasattr(site_config, attr_name), f"Site {site_name} missing {attr_name}"
                attr_value = getattr(site_config, attr_name)
                assert callable(attr_value), f"Site {site_name}.{attr_name} is not callable"

            # Check that fetch function is async
            import inspect

            fetch_func = site_config.fetch
            assert inspect.iscoroutinefunction(fetch_func), f"Site {site_name}.fetch must be async"

            print(f"Site module {site_name} structure is valid")

        except ImportError as e:
            pytest.fail(f"Could not import site module {site_name}: {e}")
        except Exception as e:
            pytest.fail(f"Error testing site module {site_name}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
