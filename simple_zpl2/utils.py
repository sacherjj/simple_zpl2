def convert_pil_image(image, width, height, dpmm=8, compression_type='A'):
    """
    Converts PIL.Image to compression type

    :param image: PIL image
    :param width: border to 99999
    :param height: border to 99999
    :param dpmm: * 8  = 200dpi
                 * 12 = 300dpi
                 * 24 = 600dpi
    :param compression_type: * 'A' - ASCII hexadecimal
                             * 'B' - binary
                             * 'C' - compressed binary
    """
    if compression_type != 'A':
        raise NotImplementedError('Compreesion Type {} not implemented'.format(compression_type))
    image = image.resize((int(width*dpmm), int(height*dpmm)))
    image = image.convert('L').convert('1')
    return image.tobytes().hex().upper()
