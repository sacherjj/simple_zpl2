import pytest

from simple_zpl2.utils import convert_pil_image


def test_convert_pil_image(image):
    data = convert_pil_image(image, 1, 1)

    expected_data = '0000000000000000'
    assert data == expected_data


@pytest.mark.parametrize('compression_type', (
    ('B',),
    ('C',),
))
def test_convert_pil_image_compression_error(compression_type, image):
    with pytest.raises(NotImplementedError):
        convert_pil_image(image, 1, 1, 8, compression_type)
