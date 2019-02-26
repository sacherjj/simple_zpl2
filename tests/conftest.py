import pytest
from PIL import Image


@pytest.fixture
def image():
    image = Image.new('1', (1, 1))
    return image
