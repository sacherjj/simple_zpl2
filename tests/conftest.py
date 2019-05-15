import pytest
import PIL


@pytest.fixture
def image():
    return PIL.Image.new('RGBA', (200, 200))
