from PIL import Image, ImageOps


def convert_pil_image(image, width, height, compression_type='A'):
    """
    Converts PIL.Image to compression type

    :param image: PIL image
    :param width: border to 99999
    :param height: border to 99999
    :param compression_type: * 'A' - ASCII hexadecimal
                             * 'B' - binary
                             * 'C' - compressed binary
    """
    if compression_type != 'A':
        raise NotImplementedError('Compreesion Type {} not implemented'.format(compression_type))
    image = image.resize((int(width), int(height)))
    image = image.convert("RGBA")
    alpha = image.getchannel("A")

    image_without_alpha = Image.new("RGBA", image.size, (255, 255, 255) + (255,))
    image_without_alpha.paste(image, mask=alpha)
    image_without_alpha = image_without_alpha.convert('L')
    image_without_alpha = ImageOps.invert(image_without_alpha)
    image_without_alpha = image_without_alpha.point(lambda x: 255 if x > 5 else 0, '1')

    return image_without_alpha
