import pytest

from simple_zpl2.utils import convert_pil_image


def test_convert_pil_image(image):
    converted_image = convert_pil_image(image, 4, 4)

    assert converted_image.mode == '1'


@pytest.mark.parametrize('compression_type', (
    ('B',),
    ('C',),
))
def test_convert_pil_image_compression_error(compression_type, image):
    with pytest.raises(NotImplementedError):
        convert_pil_image(image, 1, 1, compression_type)
