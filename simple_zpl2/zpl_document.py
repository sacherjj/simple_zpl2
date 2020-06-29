# -*- coding: utf-8 -*-
import binascii
import math
import requests
from functools import wraps

from simple_zpl2.utils import convert_pil_image


def _newline_after(func):
    """
    Decorator to append a newline after the function
    """

    @wraps(func)
    def decorated(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self._newline()

    return decorated


class _BaseZPL(object):
    # TODO: Break out '^', '~', and ',' because can be changed

    _START = '^XA'
    _END = '^XZ'

    _ORIENTATION_NORMAL = 'N'
    _ORIENTATION_90 = 'R'
    _ORIENTATION_180 = 'I'
    _ORIENTATION_270 = 'B'

    _JUSTIFICATION_LEFT = 0
    _JUSTIFICATION_RIGHT = 1
    _JUSTIFICATION_AUTO = 2

    _TEXT_JUSTIFICATION_LEFT = 'L'
    _TEXT_JUSTIFICATION_CENTER = 'C'
    _TEXT_JUSTIFICATION_RIGHT = 'R'
    _TEXT_JUSTIFICATION_JUSTIFIED = 'J'

    _QR_ERROR_CORRECTION_ULTRA_HIGH = 'H'
    _QR_ERROR_CORRECTION_HIGH = 'Q'
    _QR_ERROR_CORRECTION_STANDARD = 'M'
    _QR_ERROR_CORRECTION_LOW = 'H'

    def __init__(self):
        self.zpl = list()

    def __str__(self):
        return ''.join(self.zpl)

    def _add_comma(self, comma):
        if comma:
            self.zpl.append(',')

    def _newline(self):
        self.zpl.append('\n')

    def _add_int(self, value):
        value = int(value)  # May raise ValueError
        self.zpl.append(str(value))

    def _add_int_value_in_range(self, value, field, min_value, max_value, comma, reset_back=False):
        """
        Add a value that should be an integer within a range

        :param value: value to add to zpl
        :param field:  name of field for exception text
        :param min_value: minimum that value can equal
        :param max_value: maximum that value can equal
        :param comma: prefix with comma?
        :param reset_back: pull value back to min_value or max_value if outside of bounds
        """
        if not isinstance(value, int):
            raise ValueError('{} must be int not {}'.format(field, type(value).__name__))
        if reset_back:
            value = min(max_value, value)  # bring back to max of max_value
            value = max(min_value, value)  # bring back to min of min_value
        else:
            if not min_value <= value <= max_value:
                raise ValueError('{} must be between {} and {} (inclusive)'
                                 .format(str(field), str(min_value), str(max_value)))
        self._add_comma(comma)
        self._add_int(value)

    def _add_value_in_list(self, value, field, valid_values, comma):
        """
        Used when you want to add a value that can only be part of a select few items

        :param value: values to add to zpl
        :param field:  name of field for exception text
        :param valid_values: iterable if valid values
        :param comma: prefix with comma?
        """
        valid_values = [str(val) for val in valid_values]
        if not value:
            raise ValueError('{} must be in {}'.format(field, str(valid_values)))
        if str(value) not in valid_values:
            raise ValueError('{} must be in {}'.format(field, str(valid_values)))
        self._add_comma(comma)
        self.zpl.append(str(value))

    def _add_orientation(self, orientation, comma):
        self._add_value_in_list(orientation, 'orientation', ('N', 'R', 'I', 'B'), comma)

    def _add_character_height(self, character_height, comma):
        self._add_int_value_in_range(character_height, 'character_height', 10, 32000, comma, False)

    def _add_yes_no(self, value, field, comma):
        self._add_value_in_list(value, field, ('Y', 'N'), comma)

    def _add_line_color(self, color, comma):
        self._add_value_in_list(color, 'color', ('B', 'W'), comma)

    def _add_decimal_value_in_range(self, value, field, min_value, max_value, comma):
        if not min_value <= value <= max_value:
            raise ValueError('{} must be between {} and {} by 0.1'.format(field, min_value, max_value))
        self._add_comma(comma)
        self.zpl.append(str(round(value, 1)))

    @staticmethod
    def _verify_legal_characters(data, characters):
        valid_chars = set(characters)
        if not all(char in valid_chars for char in data):
            raise ValueError('Illegal character found in data. Must contain only "{}"'.format(characters))

    @staticmethod
    def _verify_7bit_ascii(data):
        ord_data = [ord(char) for char in data]
        outside = [val for val in ord_data if val > 127]
        if outside:
            raise ValueError('Extended ASCII can only encode ASCII 1-127.\n'
                             'Detected ASCII values outside this range: {}'.format(str(outside)))

    @staticmethod
    def _verify_data_numeric(data):
        if isinstance(data, int):
            return True
        if not data.isdigit():
            raise ValueError('Data must contain only digits.')

    @staticmethod
    def _verify_data_alphanumeric(data):
        if not data.isalnum():
            raise ValueError('Data must contain only alphanumeric characters.')

    @staticmethod
    def _format_field_data(data, replace_newlines):
        if replace_newlines:
            data = data.replace('\n', '\&')
        return data

    @_newline_after
    def _add_field_data(self, data_list, replace_newlines=False):
        """
        Field Data for Text or Barcode (^FD with 1-many ^FS)

        :param data_list:  if list or tuple, multiple data blocks with '^FS' separator
                           otherwise, single field with value
        :param replace_newlines: If true, replaces \n with \&
        """
        data = data_list
        if type(data) in (list, tuple):
            data = '^FS'.join(self._format_field_data(data, replace_newlines))
        else:
            data = self._format_field_data(data, replace_newlines)
        self.zpl.append('^FD{}^FS'.format(data))

    @_newline_after
    def _add_field_block(self, width=0, max_lines=1, dots_between_lines=0,
                         text_justification='L', hanging_indent=0):
        """
        Field Block (^FB)

        :param width: width of text 0 to label width
        :param max_lines: max number of lines in block, 1 to 9999
        :param dots_between_lines: dots between line adjustment -9999 to 9999
        :param text_justification:
            * 'L' - Left
            * 'C' - center
            * 'R' - right
            * 'J' - justified
        :param hanging_indent: 0 to 9999
        """
        self.zpl.append('^FB')
        max_label_width = 4 * 600 * 2  # 4" x 600 dpi doubled
        self._add_int_value_in_range(width, 'width', 0, max_label_width, False)
        self._add_int_value_in_range(max_lines, 'max_lines', 1, 9999, True)
        self._add_int_value_in_range(dots_between_lines, 'dots_between_lines', -9999, 9999, True)
        self._add_value_in_list(text_justification, 'text_justification', ('L', 'C', 'R', 'J'), True)
        self._add_int_value_in_range(hanging_indent, 'hanging_indent', 0, 9999, True, False)


class _Barcode(_BaseZPL):
    _CODE39_SET = '01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ-.$/+% '

    def __init__(self, data):
        self.data = data
        super().__init__()

    def _add_data(self):
        self._validate_data()
        self._process_data()
        self._add_field_data(self.data)

    def _validate_data(self):
        """
        Overload for data validation
        """
        pass

    def _process_data(self):
        """
        Overload for data modification
        """
        pass


class _1DBarcode(_Barcode):
    """
    Common Barcode output for 1D barcodes

    :param zpl_code: code for bar code type.  (ex: 'BZ','BE')
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    """

    def __init__(self, zpl_code, data, orientation=None, check_digit_one=None,
                 height=None, print_text=None, text_above=None,
                 check_digit_two=None):
        super().__init__(data)
        self._initial_build(zpl_code, orientation, check_digit_one,
                            height, print_text, text_above, check_digit_two)
        self._newline()
        self._add_data()

    def _initial_build(self, zpl_code, orientation, check_digit_one,
                       height, print_text, text_above, check_digit_two):
        self.zpl.append('^{}'.format(zpl_code))
        if orientation is None:
            return
        self._add_orientation(orientation, False)

        if check_digit_one:  # This is optional and will not trigger early exit if missing
            self._add_yes_no(check_digit_one, 'check_digit', True)

        if height is None:
            return
        self._add_int_value_in_range(height, 'height', 1, 32000, True, False)

        if print_text is None:
            return
        self._add_yes_no(print_text, 'print_text', True)

        if text_above is None:
            return
        self._add_yes_no(text_above, 'text_above', True)

        if check_digit_two is None:
            return
        self._add_yes_no(check_digit_two, 'check_digit', True)


class Code11_Barcode(_1DBarcode):
    """
    Code 11 Bar Code (^B1)

    Characters to encode (0-9 and -)

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param check_digit: * 'Y' - 1 digit
                        * 'N' - 2 digits
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    """

    def __init__(self, data, orientation=None, check_digit=None,
                 height=None, print_text=None, text_above=None):
        super().__init__('B1', data, orientation, check_digit, height, print_text, text_above, None)

    def _validate_data(self):
        self._verify_legal_characters(self.data, '0123456789-')


class Interleaved2of5_Barcode(_1DBarcode):
    """
    Interleaved 2 of 5 Bar Code (^B2)

    Characters to encode (0-9)

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    :param check_digit: calculate and print Mod 10 check digit ('Y', 'N')
    """

    def __init__(self, data, orientation=None, height=None,
                 print_text=None, text_above=None, check_digit=None):
        super().__init__('B2', data, orientation, None, height, print_text, text_above, check_digit)

    def _validate_data(self):
        self._verify_data_numeric(self.data)


class Industrial2of5_Barcode(_1DBarcode):
    """
    Industrial 2 of 5 Bar Code (^BI)

    Characters to encode (0-9)

    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    """

    def __init__(self, data, orientation=None, height=None,
                 print_text=None, text_above=None):
        super().__init__('BI', data, orientation, height, print_text, text_above)

    def _verify_data(self):
        self._verify_data_numeric(self.data)


class Standard2of5_Barcode(_1DBarcode):
    """
    Standard 2 of 5 Bar Code (^BJ)

    Characters to encode (0-9)

    :param data: barcode data numeric characters
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    """

    def __init__(self, data, orientation=None, height=None,
                 print_text=None, text_above=None):
        super().__init__('BJ', data, orientation, None, height, print_text, text_above)

    def _validate_data(self):
        self._verify_data_numeric(self.data)


class Code39_Barcode(_1DBarcode):
    """
    Code 39 Bar Code (^B3)

    Characters to encode (0-9, A-Z, -, ., $, /, +, %, ' ') with normal.

    If scanner supports extended ASCII, with encode with +$ and -$

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param check_digit: calculate and print Mod 43 check digit ('Y', 'N')
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    """

    _EXTENDED_MAP = {1: '$A', 2: '$B', 3: '$C', 4: '$D', 5: '$E',
                     6: '$F', 7: '$G', 8: '$H', 9: '$I', 10: '$J',
                     11: '$K', 12: '$L', 13: '$M', 14: '$N', 15: '$O',
                     16: '$P', 17: '$Q', 18: '$R', 19: '$S', 20: '$T',
                     21: '$U', 22: '$V', 23: '$W', 24: '$X', 25: '$Y',
                     26: '$Z', 27: '%A', 28: '%B', 29: '%C', 30: '%D',
                     31: '%E', 32: ' ', 33: '/A', 34: '/B', 35: '/C',
                     36: '/D', 37: '/E', 38: '/F', 39: '/G', 40: '/H',
                     41: '/I', 42: '/J', 43: '/K', 44: '/L', 45: '-',
                     46: '.', 47: '/O', 48: '0', 49: '1', 50: '2',
                     51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8',
                     57: '9', 58: '/Z', 59: '%F', 60: '%G', 61: '%H',
                     62: '%I', 63: '%J', 64: '%V', 65: 'A', 66: 'B',
                     67: 'C', 68: 'D', 69: 'E', 70: 'F', 71: 'G', 72: 'H',
                     73: 'I', 74: 'J', 75: 'K', 76: 'L', 77: 'M', 78: 'N',
                     79: 'O', 80: 'P', 81: 'Q', 82: 'R', 83: 'S', 84: 'T',
                     85: 'U', 86: 'V', 87: 'W', 88: 'X', 89: 'Y', 90: 'Z',
                     91: '%K', 92: '%L', 93: '%M', 94: '%N', 95: '%O',
                     96: '%W', 97: '+A', 98: '+B', 99: '+C', 100: '+D',
                     101: '+E', 102: '+F', 103: '+G', 104: '+H', 105: '+I',
                     106: '+J', 107: '+K', 108: '+L', 109: '+M', 110: '+N',
                     111: '+O', 112: '+P', 113: '+Q', 114: '+R', 115: '+S',
                     116: '+T', 117: '+U', 118: '+V', 119: '+W', 120: '+X',
                     121: '+Y', 122: '+Z', 123: '%P', 124: '%Q', 125: '%R',
                     126: '%S', 127: '%T'}

    def __init__(self, data, orientation=None, check_digit=None, height=None,
                 print_text=None, text_above=None, extended_ascii=False):
        self.extended_ascii = extended_ascii
        super().__init__('B3', data, orientation, check_digit, height, print_text, text_above)

    def _validate_data(self):
        if self.extended_ascii:
            self._verify_7bit_ascii(self.data)
        else:
            self._verify_legal_characters(self.data, self._CODE39_SET)

    def _process_data(self):
        if self.extended_ascii:
            # Need to surround with +$ and -$ and translate
            self.data = ''.join(['+$'] + [self._EXTENDED_MAP[ord(char)]
                                          for char in list(self.data)] + ['-$'])


class PlanetCode_Barcode(_1DBarcode):
    """
    Planet Code Bar Code (^B5)

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 9999)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    """

    def __init__(self, data, orientation=None, height=None,
                 print_text=None, text_above=None):
        super().__init__('B5', data, orientation, None, height, print_text, text_above)

    def _validate_data(self):
        self._verify_data_numeric(self.data)


class EAN8_Barcode(_1DBarcode):
    """
    EAN 8 Bar Code (^B8)

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    """

    def __init__(self, data, orientation=None, height=None, print_text=None, text_above=None):
        super().__init__('B8', data, orientation, None, height, print_text, text_above)

    def _validate_data(self):
        self._verify_data_numeric(self.data)


class UPC_Barcode(_1DBarcode):
    """
    UPC-E Bar Code (^B9)

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    :param check_digit: print check digit ('Y', 'N')
    """

    def __init__(self, data, orientation=None, height=None, print_text=None,
                 text_above=None, check_digit=None):
        super().__init__('B9', orientation, None, height, print_text, text_above, check_digit)

    def _validate_data(self):
        self._verify_data_numeric(self.data)


class Code49_Barcode(_Barcode):
    """
    Code 49 Bar Code (^B4)

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height_multiplier: 1 to height of label (recommending much more than 1)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    :param starting_mode: * 0 - Regular Alphanumeric Mode
                          * 1 - Multiple Read Alphanumeric
                          * 2 - Regular Numeric Mode
                          * 3 - Group Alphanumeric Mode
                          * 4 - Regular Alphanumeric Shift 1
                          * 5 - Regular Alphanumeric Shift 2
                          * A - Automatic Mode. The printer determines the
                            starting mode by analyzing the field data.
    """

    def __init__(self, data, orientation=None, height_multiplier=None, print_text=None,
                 text_above=None, starting_mode=None):
        super().__init__(data)
        self._initial_build(orientation, height_multiplier, print_text, text_above, starting_mode)
        self._add_field_data(data)

    def _initial_build(self, orientation, height_multiplier, print_text, text_above, starting_mode):
        self.zpl.append('^B4')

        if orientation is None:
            return
        self._add_orientation(orientation, False)

        if height_multiplier is None:
            return
        # 1 to height of label, how to we validate?
        self._add_int(height_multiplier)

        if print_text is None:
            return
        if print_text not in ('Y', 'N'):
            raise ValueError('print_text should be Y or N')
        if text_above not in (None, 'Y', 'N'):  # Allow None because might not be included
            raise ValueError('text_above should be Y or N')
        # Translated common arguments to non-standard text printing variable
        if print_text == 'Y':
            if text_above == 'Y':
                interpretation_line = 'A'
            else:
                interpretation_line = 'B'
        else:
            interpretation_line = 'N'
        self._add_comma(True)
        self.zpl.append(interpretation_line)

        if starting_mode is None:
            return
        self._add_value_in_list(starting_mode, 'starting_mode', (0, 1, 2, 3, 4, 5, 'A'), True)
        if starting_mode != 'A':
            raise ValueError('Only Automatic Starting Mode is Implemented.')

    def _validate_data(self):
        # TODO: Add validation for all Regular and Shift 1, Shift 2 characters
        pass


class Aztec_Barcode(_Barcode):
    """
    Aztec Barcode (^B0 [zero] or ^BO [letter])

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param magnification: 1 to 10
    :param ecic: * 'Y' - data contains ECICs
                 * 'N' - does not contain ECICs
    :param ec_symbol_size: * 0 - default error correction
                           * 01-99 - error correction percentage
                           * 101-104 - 1-4 layer compact symbol
                           * 201-232 - 1-32 layer full-range symbol
                           * 300 - simple Aztec "Rune"
    :param menu_symbol: * 'Y' - a menu or barcode reader initialization sybmol
                        * 'N' - not menu symbol
    :param number_of_symbols: Structured append 1-26 sybmols
    :param structured_id_append: up to 24 character ID data
    """

    def __init__(self, data, orientation=None, magnification=None,
                 ecic=None, ec_symbol_size=None,
                 menu_symbol=None, number_of_symbols=None,
                 structured_id_append=None):
        super().__init__(data)
        self._initial_build(orientation, magnification, ecic, ec_symbol_size,
                            menu_symbol, number_of_symbols, structured_id_append)
        self._add_field_data(data)

    def _initial_build(self, orientation, magnification, ecic, ec_symbol_size,
                       menu_symbol, number_of_symbols, structured_id_append):
        self.zpl.append('^B0')

        if orientation is None:
            return
        self._add_orientation(orientation, False)

        if magnification is None:
            return
        self._add_int_value_in_range(magnification, 'magnification', 1, 10, True)

        if ecic is None:
            return
        self._add_yes_no(ecic, 'ecic', True)

        if ec_symbol_size is None:
            return
        if not (0 <= ec_symbol_size <= 99 or
                101 <= ec_symbol_size <= 104 or
                201 <= ec_symbol_size <= 232 or
                ec_symbol_size == 300):
            raise ValueError('ec_symbol_size must be 0, 1-99, 101-104, 201-232, or 300.')
        if 1 <= ec_symbol_size <= 9:
            ec_string = '0' + str(ec_symbol_size)
        else:
            ec_string = str(ec_symbol_size)
        self._add_comma(True)
        self.zpl.append(ec_string)

        if menu_symbol is None:
            return
        self._add_yes_no(menu_symbol, 'menu_symbol', True)

        if number_of_symbols is None:
            return
        self._add_int_value_in_range(number_of_symbols, 'number_of_symbols', 1, 26, True)

        if structured_id_append is None:
            return
        if len(structured_id_append) > 24:
            raise ValueError('structured_id_append length maximum is 24.')
        self._add_comma(True)
        self.zpl.append(structured_id_append)


class _PDF_Barcode(_Barcode):

    def __init__(self, data):
        super().__init__(data)

    def multiple_field_origin(self, *args):
        """
        Adds ^FM Multiple Field Origin Locations

        Pass in pairs of x, y with a limit of 60 pairs

        :param args: x1, y1 0 to 32000 or e to exclude
        """
        if len(args) % 2 != 0:
            raise ValueError('Uneven number of arguments, must be x, y pairs.')
        if len(args) > 120:
            raise ValueError('Max number of pairs is 60.')
        self.zpl.append('^FM')
        for val in args:
            if val != 'e' and (val < 0 or val > 32000):
                raise ValueError("x and y arguments must be between 0 to 32000 or 'e'")
        self.zpl.append(','.join([str(val) for val in args]))
        self._newline()


class PDF417_Barcode(_PDF_Barcode):
    """
    PDF417 Bar Code (^B7)

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height:  height of individual dots, recommends larger than 1
    :param security_level: 0 - error detection only, 1-8 correction level
    :param data_column_count: number of code word columns (1-30)
    :param row_count: number of rows to encode (3-90)
    :param truncate: truncate right row indicators and stop pattern ('Y', 'N')
    """

    def __init__(self, data, orientation=None, height=None, security_level=None,
                 data_column_count=None, row_count=None, truncate=None):
        super().__init__(data)
        self._initial_build(orientation, height, security_level,
                            data_column_count, row_count, truncate)
        self._add_field_data(data)

    def _initial_build(self, orientation, height, security_level,
                       data_column_count, row_count, truncate):
        self.zpl.append('^B7')

        if orientation is None:
            return
        self._add_orientation(orientation, False)

        if height is None:
            return
        self._add_int(height)

        if security_level is None:
            return
        self._add_int_value_in_range(security_level, 'security_level', 0, 8, True)

        if data_column_count is None:
            return
        self._add_int_value_in_range(data_column_count, 'data_column_count', 1, 30, True)

        if row_count is None:
            return
        self._add_int_value_in_range(row_count, 'row_count', 3, 90, True)

        if truncate is None:
            return
        self._add_yes_no(truncate, 'truncate', True)


class MicroPDF417_Barcode(_PDF_Barcode):
    """
    MicroPDF417 Bar Code (^BF)

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 9999)
    :param mode: 0-33

    .. note::

        To encode data into a MicroPDF417 bar code, complete these steps:

            1. Determine the type of data to be encoded (for example, ASCII characters, numbers, 8-bit
            data, or a combination).

            2. Determine the maximum amount of data to be encoded within the bar code (for
            example, number of ASCII characters, quantity of numbers, or quantity of 8-bit data
            characters).

            3. Determine the percentage of check digits that are used within the bar code. The higher
            the percentage of check digits that are used, the more resistant the bar code is to
            damage — however, the size of the bar code increases.

            4. Use Table with the information gathered from the questions above to select the mode
            of the bar code.

         MO - mode

         DC - Number of Data Columns

         DR - Number of Data Rows

         EC - % of CWS for EC

         MX - Max Alpha Characters

         MD - Max Digits

        +----+----+----+----+----+----+
        | MO | DC | DR | EC | MX | MD |
        +====+====+====+====+====+====+
        |  0 |  1 | 11 | 64 |  6 |  8 |
        +----+----+----+----+----+----+
        |  1 |  1 | 14 | 50 | 12 | 17 |
        +----+----+----+----+----+----+
        |  2 |  1 | 17 | 41 |  18|  26|
        +----+----+----+----+----+----+
        |  3 |  1 | 20 | 40 | 22 | 32 |
        +----+----+----+----+----+----+
        |  4 |  1 | 24 | 33 | 30 | 44 |
        +----+----+----+----+----+----+
        |  5 |  1 | 28 | 29 | 38 | 55 |
        +----+----+----+----+----+----+
        |  6 |  2 |  8 | 50 | 14 | 20 |
        +----+----+----+----+----+----+
        |  7 |  2 | 11 | 41 | 24 | 35 |
        +----+----+----+----+----+----+
        |  8 |  2 | 14 | 32 | 36 | 52 |
        +----+----+----+----+----+----+
        |  9 |  2 | 17 | 29 | 46 | 67 |
        +----+----+----+----+----+----+
        | 10 |  2 | 20 | 28 | 56 | 82 |
        +----+----+----+----+----+----+
        | 11 |  2 | 23 | 28 | 64 | 93 |
        +----+----+----+----+----+----+
        | 12 |  2 | 26 | 29 | 72 |105 |
        +----+----+----+----+----+----+
        | 13 |  3 |  6 | 67 | 10 | 14 |
        +----+----+----+----+----+----+
        | 14 |  3 |  8 | 58 | 18 | 26 |
        +----+----+----+----+----+----+
        | 15 |  3 | 10 | 53 | 26 | 38 |
        +----+----+----+----+----+----+
        | 16 |  3 | 12 | 50 | 34 | 49 |
        +----+----+----+----+----+----+
        | 17 |  3 | 15 | 47 | 46 | 67 |
        +----+----+----+----+----+----+
        | 18 |  3 | 20 | 43 | 66 | 96 |
        +----+----+----+----+----+----+
        | 19 |  3 | 26 | 41 | 90 |132 |
        +----+----+----+----+----+----+
        | 20 |  3 | 32 | 40 | 114| 167|
        +----+----+----+----+----+----+
        | 21 |  3 | 38 | 39 | 138| 202|
        +----+----+----+----+----+----+
        | 22 |  3 | 44 | 38 | 162| 237|
        +----+----+----+----+----+----+
        | 23 |  4 |  6 | 50 |  22|  32|
        +----+----+----+----+----+----+
        | 24 |  4 |  8 | 44 |  34|  49|
        +----+----+----+----+----+----+
        | 25 |  4 | 10 | 40 |  46|  67|
        +----+----+----+----+----+----+
        | 26 |  4 | 12 | 38 |  58|  85|
        +----+----+----+----+----+----+
        | 27 |  4 | 15 | 35 |  76| 111|
        +----+----+----+----+----+----+
        | 28 |  4 | 20 | 33 | 106| 155|
        +----+----+----+----+----+----+
        | 29 |  4 | 26 | 31 | 142| 208|
        +----+----+----+----+----+----+
        | 30 |  4 | 32 | 30 | 178| 261|
        +----+----+----+----+----+----+
        | 31 |  4 | 38 | 29 | 214| 313|
        +----+----+----+----+----+----+
        | 32 |  4 | 44 | 28 | 250| 366|
        +----+----+----+----+----+----+
        | 33 |  4 |  4 | 50 | 14 | 20 |
        +----+----+----+----+----+----+
    """

    def __init__(self, data, orientation=None, height=None, mode=None):
        super().__init__(data)
        self.zpl.append('^BF')

        if orientation is None:
            return
        self._add_orientation(orientation, False)

        if height is None:
            return
        self._add_int_value_in_range(height, 'height', 1, 9999, True)

        if mode is None:
            return
        self._add_int_value_in_range(mode, 'mode', 0, 33, True)


class Code93_Barcode(_1DBarcode):
    """
    Code 93 Bar Code (^BA)

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    :param check_digit: print check digit ('Y', 'N')
    """

    _ENC_MAP = {0: "'U", 1: '&A', 2: '&B', 3: '&C', 4: '&D',
                5: '&E', 6: '&F', 7: '&G', 8: '&H', 9: '&I',
                10: '&J', 11: '&K', 12: '&L', 13: '&M', 14: '&N',
                15: '&O', 16: '&P', 17: '&Q', 18: '&R', 19: '&S',
                20: '&T', 21: '&U', 22: '&V', 23: '&W', 24: '&X',
                25: '&Y', 26: '&Z', 27: "'A", 28: "'B", 29: "'C",
                30: "'D", 31: "'E", 32: ' ', 33: '(A', 34: '(B',
                35: '(C', 36: '(D', 37: '(E', 38: '(F', 39: '(G',
                40: '(H', 41: '(I', 42: '(J', 43: '+', 44: '(L',
                45: '-', 46: '.', 47: '/', 48: '0', 49: '1',
                50: '2', 51: '3', 52: '4', 53: '5', 54: '6',
                55: '7', 56: '8', 57: '9', 58: '(Z', 59: "'F",
                60: "'G", 61: "'H", 62: "'I", 63: "'J", 64: "'V",
                65: 'A', 66: 'B', 67: 'C', 68: 'D', 69: 'E',
                70: 'F', 71: 'G', 72: 'H', 73: 'I', 74: 'J',
                75: 'K', 76: 'L', 77: 'M', 78: 'N', 79: 'O',
                80: 'P', 81: 'Q', 82: 'R', 83: 'S', 84: 'T',
                85: 'U', 86: 'V', 87: 'W', 88: 'X', 89: 'Y',
                90: 'Z', 91: "'K", 92: "'L", 93: "'M", 94: "'N",
                95: "'O", 96: "'W", 97: ')A', 98: ')B', 99: ')C',
                100: ')D', 101: ')E', 102: ')F', 103: ')G', 104: ')H',
                105: ')I', 106: ')J', 107: ')K', 108: ')L', 109: ')M',
                110: ')N', 111: ')O', 112: ')P', 113: ')Q', 114: ')R',
                115: ')S', 116: ')T', 117: ')U', 118: ')V', 119: ')W',
                120: ')X', 121: ')Y', 122: ')Z', 123: "'P", 124: "'Q",
                125: "'R", 126: "'S", 127: "'T"}

    def __init__(self, data, orientation=None, height=None,
                 print_text=None, text_above=None, check_digit=None,
                 extended_ascii=False):
        self.extended_ascii = extended_ascii
        super().__init__('BA', data, orientation, None, height,
                         print_text, text_above, check_digit)

    def _validate_data(self):
        normal_set = '01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ-.$/+%&,() '
        if self.extended_ascii:
            self._verify_7bit_ascii(self.data)
        else:
            self._verify_legal_characters(self.data, normal_set)

    def _process_data(self):
        if self.extended_ascii:
            # Need to surround with +$ and -$ and translate
            self.data = ''.join(['+$'] + [self._ENC_MAP[ord(char)]
                                          for char in list(self.data)] + ['-$'])


class CODABLOCK_Barcode(_Barcode):
    """
    CODABLOCK Bar Code (^BB)

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: height of individual dots (2 to 32000)
    :param security_level: ('Y', 'N') only 'N' if mode is 'A'
    :param characters_per_row: 2-62
    :param row_count: mode A: 1-22, mode E,F: 2-4
    :param mode: * 'A' - Code 39
                 * 'F' - Code 128
                 * 'E' - Code 128 with FNC1
    """

    def __init__(self, data, orientation=None, height=None,
                 security_level=None, characters_per_row=None,
                 row_count=None, mode='F'):
        super().__init__(data)
        self.zpl.append('^BB')

        if orientation is None:
            return
        self._add_orientation(orientation, False)

        if height is None:
            return
        self._add_int_value_in_range(height, 'height', 2, 32000, True)

        if security_level is None:
            return
        self._add_yes_no(security_level, 'security_level', True)

        if characters_per_row is None:
            return
        self._add_int_value_in_range(characters_per_row, 'characters_per_row', 2, 62, True)

        if row_count is None:
            return

        # mode comes later, so setting to default value 'F' istead of None.
        # if an invalid mode is sent in, we will not add a row_count,
        # but a Value Error will be thrown adding mode, so nothing lost.
        if mode in ('E', 'F'):
            self._add_int_value_in_range(row_count, 'row_count for type E and F', 2, 4, True)
        elif mode == 'A':
            self._add_int_value_in_range(row_count, 'row_count for type A', 1, 22, True)

        self._add_value_in_list(mode, 'mode', ('A', 'E', 'F'), True)

    def _validate_data(self):
        """
        Validation based on mode.

        If mode = 'A', Code 39 valid characters
        Otherwise, Code 128 character set
        :return:
        """
        raise NotImplementedError()

    def _add_data(self):
        raise NotImplementedError()


class Code128_Barcode(_1DBarcode):
    """
    Code 128 Barcode (^BC)

    Only Code B is currently implemented, in the printable ASCII subset
    of ASCII > 95.

    :param data: data for barcode
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    :param check_digit: Add Mod10 check digit to Mod103 ('Y', 'N')

    .. todo::

        * Add Invocation Character Handling
        * Add Code A and C handling
        * Add Code B > 94 handling
        *
    """

    _START_CODE_A = 103
    _START_CODE_B = 104
    _START_CODE_C = 105

    _INV_CODES = {'><': 62, '>0': 30, '>=': 94, '>1': 95, '>2': 96,
                  '>3': 97, '>4': 98, '>5': 99, '>6': 100, '>7': 101,
                  '>8': 102, '>9': 103, '>:': 104, '>;': 105}

    def __init__(self, data, orientation, height=None, print_text=None,
                 text_above=None, check_digit=None):
        super().__init__('BC', data, orientation, None, height, print_text, text_above, check_digit)

    def _validate_data(self):
        start = ord(self.data[0])
        try:
            inv_code = self._INV_CODES[self.data[:1]]
        except:
            inv_code = None
        if start == self._START_CODE_A or inv_code == self._START_CODE_A:
            raise NotImplementedError('Code A mode not implemented.')
        if start == self._START_CODE_C or inv_code == self._START_CODE_C:
            raise NotImplementedError('Code C mode not implemented.')
        for value in self._INV_CODES.keys():
            if value in self.data:
                raise NotImplementedError('Invocation Characters not implemented')

    def _process_data(self):
        # TODO: Add translation based in start mode coding and inline coding
        pass


class ANSICodabar_Barcode(_1DBarcode):
    """
    ANSI Codabar Bar Code (^BK)

    Characters to encode (0-9)

    :param data: barcode data numeric
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    :param start_character: 'A', 'B', 'C', 'D'
    :param stop_character: 'A', 'B', 'C', 'D'
    """

    def __init__(self, data, orientation=None, height=None,
                 print_text=None, text_above=None,
                 start_character=None, stop_character=None):
        super().__init__('BK', data, orientation, 'N', height, print_text, text_above)

        self.start_char = start_character
        self.stop_char = stop_character
        if start_character is None:
            return
        self._add_value_in_list(start_character, 'start_character', ('A', 'B', 'C', 'D'), True)

        if stop_character is None:
            return
        self._add_value_in_list(stop_character, 'stop_character', ('A', 'B', 'C', 'D'), True)

    def _validate_data(self):
        allowed = '0123456789-:.$/+'
        if self.start_char and self.stop_char:
            allowed += self.start_char + self.stop_char
        else:
            # We don't know start and stop, so allow all.
            # Maybe we should
            allowed += 'ABCD'
        self._verify_legal_characters(self.data, allowed)


class EAN13_Barcode(_1DBarcode):
    """
    EAN-13 Bar Code (^BE)

    Following Field data is limited to exactly 12 characters.

    :param data: numeric data only and 12 numerals.  Truncated or padded to 12.
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    """

    def __init__(self, data, orientation=None, height=None, print_text=None, text_above=None):
        super().__init__('BE', data, orientation, None, height, print_text, text_above)

    def _verify_data(self):
        self._verify_data_numeric(self.data)

    def _process_data(self):
        self.data = str(self.data)
        if len(self.data) > 12:
            self.data = self.data[:12]  # Truncate to 12
        if len(self.data) < 12:
            self.data = self.data.zfill(12)


class LOGMARS_Barcode(_1DBarcode):
    """
    LOGMARS Bar Code (^BL)

    This is a special application of Code 39 used by Department of Defense.
    LOGMARS - Logistics Applications of Automated Marking and Reading Symbols

    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param text_above: print text above barcode ('Y', 'N')
    """

    def __init__(self, data, orientation=None, height=None, text_above=None):
        super().__init__('BJ', data, orientation, None, height)

        if text_above is None:
            return
        self._add_yes_no(text_above, 'text_above', True)

    def _validate_data(self):
        self._verify_legal_characters(self.data, self._CODE39_SET)


class MSI_Barcode(_Barcode):
    """
    MSI Bar Code (^BM)

    Characters to encode (0-9)

    :param data: barcode data numeric only
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param check_digit: * A - no check digits
                        * B - 1 Mod 10
                        * C - 2 Mod 10
                        * D - 1 Mod 11 and 1 Mod 10
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    :param insert_check_digit: Add check digit to text line  ('Y', 'N')
    """

    @_newline_after
    def add_barcode_msi(self, data, orientation=None, check_digit=None, height=None,
                        print_text=None, text_above=None, insert_check_digit=None):
        self.zpl.append('^BM')

        if orientation is None:
            return
        self._add_orientation(orientation, False)

        self.check_digit = check_digit
        if check_digit is None:
            return
        self._add_value_in_list(check_digit, 'check_digit', ('A', 'B', 'C,', 'D'), True)

        if height is None:
            return
        self._add_int_value_in_range(height, 'height', 1, 32000, True)

        if print_text is None:
            return
        self._add_yes_no(print_text, 'print_text', True)

        if text_above is None:
            return
        self._add_yes_no(text_above, 'text_above', True)

        if insert_check_digit is None:
            return
        self._add_yes_no(insert_check_digit, 'insert_check_digit', True)

    def _validate_data(self):
        if self.check_digit in ('B', 'C', 'D'):
            max_len = 13
        else:
            # for A or unknown, give max possible
            max_len = 14
        if len(str(self.data)) > max_len:
            raise ValueError('msi barcode data has maximum len of 13 for check_digit B,C,D or 14 for check_digit A.')
        self._verify_data_numeric(self.data)


class UPSMaxicode_Barcode(_Barcode):
    """
    UPS MaxiCode Bar Code

    Note: Data adding isn't completed.  Must be done with manual add_data_field.

    :param mode:
        * 2 - structured carrier message: numeric postal code (U.S.)
        * 3 - structured carrier message: alphanumeric postal code (non-U.S.)
        * 4 - standard symbol, secretary
        * 5 - full EEC
        * 6 - reader program, secretary
    :param symbol_number: 1-8
    :param symbol_count: 1-8

    .. note::

    Considerations for ^FD when Using ^BD
    The ^FD statement is divided into two parts: a high priority message (hpm) and a low priority
    message (lpm). There are two types of high priority messages. One is for a U.S. Style Postal Code;
    the other is for a non-U.S. Style Postal Code. The syntax for either of these high priority messages
    must be exactly as shown or an error message is generated.
    Format: ^FD <hpm><lpm>

    <hpm> = high priority message (applicable only in Modes 2 and 3)
        Values: 0 to 9, except where noted
        U.S. Style Postal Code (Mode 2)
            <hpm> = aaabbbcccccdddd
            aaa = three-digit class of service
            bbb = three-digit country zip code
            ccccc = five-digit zip code
            dddd = four-digit zip code extension (if none exists, four zeros (0000) must be
            entered)
        non-U.S. Style Postal Code (Mode 3)
            <hpm> = aaabbbcccccc
            aaa = three-digit class of service
            bbb = three-digit country zip code
            ccccc = six-digit zip code (A through Z or 0 to 9)

    <lpm> = low priority message (only applicable in Modes 2 and 3)
        GS is used to separate fields in a message (0x1D).
        RS is used to separate format types (0x1E).
        EOT is the end of transmission characters.

        Message Header [)>RS
        Transportation Data
        Format Header01GS96
        Tracking Number*<tracking number>
        SCAC*GS<SCAC>
        UPS Shipper NumberGS<shipper number>
        Julian Day of PickupGS<day of pickup>
        Shipment ID NumberGS<shipment ID number>
        Package n/xGS<n/x>
        Package WeightGS<weight>
        Address ValidationGS<validation>
        Ship to Street AddressGS<street address>
        Ship to CityGS<city>
        Ship to StateGS<state>
        RSRS
        End of MessageEOT
        (* Mandatory Data for UPS)

    Comments
    • The formatting of <hpm> and <lpm> apply only when using Modes 2 and 3.
    Mode 4, for example, takes whatever data is defined in the ^FD command and places it in the
    symbol.
    • UPS requires that certain data be present in a defined manner. When formatting MaxiCode data
    for UPS, always use uppercase characters. When filling in the fields in the <lpm> for UPS,
    follow the data size and types specified in Guide to Bar Coding with UPS.
    • If you do not choose a mode, the default is Mode 2. If you use non-U.S. Postal Codes, you
    probably get an error message (invalid character or message too short). When using non-U.S.
    codes, use Mode 3.
    • ZPL II doesn’t automatically change your mode based on the zip code format.
    • When using special characters, such as GS, RS, or EOT, use the ^FH command to tell ZPL II to
    use the hexadecimal value following the underscore character ( _ ).
    """

    def __init__(self, mode=None, symbol_number=None, symbol_count=None):
        super().__init__('')
        self.zpl.append('^BD')

        if mode is None:
            return
        self._add_int_value_in_range(mode, 'mode', 2, 6, False)

        if symbol_number is None:
            return
        self._add_int_value_in_range(symbol_number, 'symbol_number', 1, 8, True)

        if symbol_count is None:
            return
        self._add_int_value_in_range(symbol_count, 'symbol_count', 1, 8, True)

    def _add_data(self):
        # TODO: Add hpm and lpm messages
        pass


class DataMatrix_Barcode(_Barcode):
    """
    Data Matrix Bar Code (^BX)

    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: height of individual symbol elements 1-width of label
    :param quality: amount of data added for error correction 0, 50, 80, 100, 140, 200
    :param columns: * columns to encode 9-49
                    * odd values only for quality 0-140
                    * even values for quality 200
    :param rows: rows to encode 9-49
    :param format_id: * 1 = field data is numeric + space (0..9,”) – No \&
                      * 2 = field data is uppercase alphanumeric + space (A..Z,’’) – No \&’’
                      * 3 = field data is uppercase alphanumeric + space, period, comma, dash, and slash (
                        0..9,A..Z,“.-/”)
                      * 4 = field data is upper-case alphanumeric + space (0..9,A..Z,’’) – no \&’’
                      * 5 = field data is full 128 ASCII 7-bit set
                      * 6 = field data is full 256 ISO 8-bit set
    :param escape_sequence: any character
    :param aspect_ratio: * 1 = square
                         * 2 = rectangular

    .. note::

    Effects of ^BY on ^BX

        w = module width (no effect)

        r = ratio (no effect)

        h = height of symbol

            If the dimensions of individual symbol elements are not specified in the ^BY command,
            the height of symbol value is divided by the required rows/columns, rounded, limited to a
            minimum value of one, and used as the dimensions of individual symbol elements.

    Field Data (^FD) for ^BX

        Quality 000 to 140

            * The \& and || can be used to insert carriage returns, line feeds, and the backslash, similar to the
              PDF417. Other characters in the control character range can be inserted only by using ^FH.
              Field data is limited to 596 characters for quality 0 to 140. Excess field data causes no symbol to
              print; if ^CV is active, INVALID-L prints. The field data must correspond to a user-specified
              format ID or no symbol prints; if ^CV is active, INVALID-C prints.

            * The maximum field sizes for quality 0 to 140 symbols are shown in the tktable in the g parameter.

        Quality 200

            * If more than 3072 bytes are supplied as field data, it is truncated to 3072 bytes. This limits the
              maximum size of a numeric Data Matrix symbol to less than the 3116 numeric characters that
              the specification would allow. The maximum alphanumeric capacity is 2335 and the maximum
              8-bit byte capacity is 1556.

            * If ^FH is used, field hexadecimal processing takes place before the escape sequence
              processing described below.

            * The underscore is the default escape sequence control character for quality 200 field data. A
              different escape sequence control character can be selected by using parameter g in the ^BX
              command.

            The information that follows applies to firmware version: V60.13.0.12, V60.13.0.12Z, V60.13.0.12B,
            V60.13.0.12ZB, or later. The input string escape sequences can be embedded in quality 200 field
            data using the ASCII 95 underscore character ( _ ) or the character entered in parameter g:

              * _X is the shift character for control characters (e.g., _@=NUL,_G=BEL,_0 is PAD)
              * _1 to _3 for FNC characters 1 to 3 (explicit FNC4, upper shift, is not allowed)
              * FNC2 (Structured Append) must be followed by nine digits, composed of three-digit numbers
                with values between 1 and 254, that represent the symbol sequence and file identifier (for
                example, symbol 3 of 7 with file ID 1001 is represented by _2214001001)
              * 5NNN is code page NNN where NNN is a three-digit code page value (for example, Code Page
                9 is represented by _5009)
              * _dNNN creates ASCII decimal value NNN for a code word (must be three digits)
              * _ in data is encoded by __ (two underscores)
                The information that follows applies to all other versions of firmware. The input string escape
                sequences can be embedded in quality 200 field data using the ASCII 7E tilde character (~) or the
                character entered in parameter g:
              * ~X is the shift character for control characters (e.g., ~@=NUL,~G=BEL,~0 is PAD)
              * ~1 to ~3 for FNC characters 1 to 3 (explicit FNC4, upper shift, is not allowed)
              * FNC2 (Structured Append) must be followed by nine digits, composed of three-digit numbers
                with values between 1 and 254, that represent the symbol sequence and file identifier (for
                example, symbol 3 of 7 with file ID 1001 is represented by ~2214001001)
              * 5NNN is code page NNN where NNN is a three-digit code page value (for example, Code Page
                9 is represented by ~5009)
              * ~dNNN creates ASCII decimal value NNN for a code word (must be three digits)
              * ~ in data is encoded by a ~ (tilde)
    """

    def __init__(self, data, orientation=None, height=None, quality=None, columns=None,
                 rows=None, format_id=None, escape_sequence=None, aspect_ratio=None):
        super().__init__(data)
        self._initial_setup(orientation, height, quality, columns,
                            rows, format_id, escape_sequence, aspect_ratio)
        # TODO: Validation of data
        self._add_field_data(data)

    def _initial_setup(self, orientation, height, quality, columns,
                       rows, format_id, escape_sequence, aspect_ratio):
        self.zpl.append('^BX')
        if orientation is None:
            return
        self._add_orientation(orientation, False)

        if height is None:
            return
        # How to validate 1 to height of label?
        self._add_int_value_in_range(height, 'height', 1, 32000, True)

        if quality is None:
            return
        self._add_value_in_list(quality, 'quality', (0, 50, 80, 100, 140, 200), True)

        if columns is None:
            return
        if quality == 200:
            if columns % 2 == 1:
                raise ValueError('columns must be even for quality of 200.')
        else:
            if columns % 2 == 0:
                raise ValueError('columns must be odd for quality of (0, 50, 80, 100, 140).')
        self._add_int_value_in_range(columns, 'columns', 9, 49, True)

        if rows is None:
            return
        self._add_int_value_in_range(rows, 'rows', 9, 49, True)

        if format_id is None:
            return
        self._add_int_value_in_range(format_id, 'format_id', 1, 6, True)

        if escape_sequence is None:
            return
        if len(escape_sequence) != 1:
            raise ValueError('escape_sequence must be a single character.')
        self._add_comma(True)
        self.zpl.append(escape_sequence)

        if aspect_ratio is None:
            return
        self._add_int_value_in_range(aspect_ratio, 'aspect_ratio', 1, 2, True)

    # def add_field_data_data_matrix(self, data, format_id, quality):
    #     # maximum data lengths based on quality, format_id
    #     max_len_map = {(0, 1): 596, (0, 2): 425, (0, 3): 394, (0, 4): 413, (0, 5): 310, (0, 6): 271,
    #                    (50, 1): 457, (50, 2): 333, (50, 3): 291, (50, 4): 305, (50, 5): 228, (50, 6): 200,
    #                    (80, 1): 402, (80, 2): 293, (80, 3): 256, (80, 4): 268, (80, 5): 201, (80, 6): 176,
    #                    (100, 1): 300, (100, 2): 218, (100, 3): 190, (100, 4): 200, (100, 5): 150, (100, 6): 131,
    #                    (140, 1): 144, (140, 2): 105, (140, 3): 91, (140, 4): 96, (140, 5): 72, (140, 6): 63}
    #     try:
    #         max_len = max_len_map[(int(quality), int(format_id))]
    #     except KeyError:
    #         raise ValueError('format_id or quality was an invalid value, unable to lookup max data length.')
    #
    #     if len(data) > max_len:
    #         raise ValueError('data length is limited to {} for format_id={} and quality={}'.format(max_len,
    #                                                                                                format_id,
    #                                                                                                quality))
    #     self.add_field_data(data)


class Plessey_Barcode(_1DBarcode):
    """
    Plessey Bar Code (^BP)

    Characters to encode (0-9 A-F)

    :param data: data for barcode 0-9 or A-F
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param check_digit: print check digit ('Y', 'N')
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    """

    def __init__(self, data, orientation=None, check_digit=None,
                 height=None, print_text=None, text_above=None):
        super().__init__('BP', data, orientation, check_digit, height, print_text, text_above)

    def _validate_data(self):
        allowed = '0123456789ABCDEF'
        self._verify_legal_characters(self.data, allowed)


class TLC39_Barcode(_BaseZPL):
    """
    TLC39 Bar Code (^BT)

    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param code_39_width: width of the Code 39 bar code 1-10
    :param code_39_ratio: wide to narrow bar width ratio of Code 39 bar code 2.0-3.0 by 0.1
    :param code_39_height: height of the Code 39 bar code 1-9999
    :param micropdf417_height: height of MicroPDF417 bar code 1-255
    :param micropdf417_width: width of MicroPDF417 bar code 1-10

    .. note::

        ECI Number.

            If the seventh character is not a comma, only Code 39 prints. This means if
            more than 6 digits are present, Code 39 prints for the first six digits (and no Micro-PDF
            symbol is printed).

            * Must be 6 digits.
            * Firmware generates invalid character error if the firmware sees anything but 6 digits.
            * This number is not padded.

        Serial number.

            The serial number can contain up to 25 characters and is variable length.
            The serial number is stored in the Micro-PDF symbol. If a comma follows the serial
            number, then additional data is used below.

            * If present, must be alphanumeric (letters and numbers, no punctuation).
              This value is used if a comma follows the ECI number.

        Additional data.

            If present, it is used for things such as a country code.
            Data cannot exceed 150 bytes. This includes serial number commas.

            * Additional data is stored in the Micro-PDF symbol and appended after the
              serial number. A comma must exist between each maximum of 25 characters
              in the additional fields.
            * Additional data fields can contain up to 25 alphanumeric characters per field.
    """

    def __init__(self, orientation=None, code_39_width=None,
                 code_39_ratio=None, code_39_height=None,
                 micropdf417_height=None, micropdf417_width=None):
        self._data_added = False
        super().__init__()
        self.zpl.append('^BT')

        if orientation is None:
            return
        self._add_orientation(orientation, False)

        if code_39_width is None:
            return
        self._add_int_value_in_range(code_39_width, 'code_39_width', 1, 10, True)

        if code_39_ratio is None:
            return
        self._add_decimal_value_in_range(code_39_ratio, 'code_39_ratio', 2, 3, True)

        if code_39_height is None:
            return
        self._add_int_value_in_range(code_39_height, 'code_39_height', 1, 9999, True)

        if micropdf417_height is None:
            return
        self._add_int_value_in_range(micropdf417_height, 'micropdf417_height', 1, 255, True)

        if micropdf417_width is None:
            return
        self._add_int_value_in_range(micropdf417_width, 'micropdf417_width', 1, 10, True)

    def add_data(self, eci_number, serial_number=None, additional_data=None):
        """
        Add data field for tlc39 barcode

        :param eci_number: exactly 6 digit number
        :param serial_number: optional up to 26 character alphanumeric
        :param additional_data: string or list/tuple
        """
        if self._data_added:
            raise Exception('add_data can only be called once per object.')
        self._data_added = True
        data = []
        if not (len(eci_number) == 6 and eci_number.isdigit()):
            raise ValueError('eci_number must be exactly 6 digital')
        data.append(eci_number)

        if serial_number is None:
            self._add_field_data(','.join(data))
            return
        if not (1 <= len(serial_number) <= 26 and serial_number.isalnum()):
            raise ValueError('serial_number must be alphanumeric between 1 and 26 characters.')
        data.append(serial_number)

        if additional_data is None:
            self._add_field_data(','.join(data))
            return

        if type(additional_data) in (tuple, list):
            # Verify that each data block is 25 characters or less
            for ad in additional_data:
                if len(ad) >= 25:
                    raise ValueError('additional_data blocks are limited to 25 characters.')
            # join all data, as will need to be less than 139 (140 with serial number comma)
            ad_joined = ','.join(additional_data)
        else:
            if len(additional_data) > 25:
                raise ValueError('additional_data blocks are limited to 25 characters.')
            ad_joined = additional_data
        if len(ad_joined) > 139:
            raise ValueError('additional_data is limited to 139 characters after joining with commas.' +
                             'Data sent length is {}'.format(len(ad_joined)))
        if not ad_joined.isalnum():
            raise ValueError('additional_data must be alphanumeric.')
        data.append(ad_joined)

        self._add_field_data(','.join(data))


class QR_Barcode(_Barcode):
    """
    QR Barcode (^BQ)

    :param model: 1 - original, 2 - enhanced
    :param magnification: 1 to 10
    :param error_correction: * 'H' - ultra-high
                             * 'Q' - high'
                             * 'M' - standard
                             * 'L' - low
    :param mask_value: 0-7 defaults 7

    .. note::

        QR Switches (formatted into the ^FD field data)
        There are 4 switch fields that are allowed, some with associated parameters and some without. Two
        of these fields are always present, one is optional, and one’s presence depends on the value of
        another. The switches are always placed in a fixed order. The four switches, in order are:

        Mixed mode <D>iijjxx,Optional (note that this switch ends with a comma “,”)
        Error correction level <H, Q, M, L>Mandatory
        Data input <A, M>,Mandatory (note that this switch ends with a comma “,”)
        Character Mode <N, A, Bdddd, K>Conditional (present if data input is M)

        Mixed mode (Optional)

            = D - allows mixing of different types of character modes in one code.
            ii = code No. – a 2 digit number in the range 01 to 16
            Value = subtracted from the Nth number of the divided code (must be two digits).
            jj = No. of divisions – a 2 digit number in the range 02 to 16
            Number of divisions (must be two digits).
            xx = parity data – a 2 digit hexadecimal character in the range 00 to FF
            Parity data value is obtained by calculating at the input data (the original input data before
            divided byte-by-byte through the EX-OR operation).
            , = the mixed mode switch, when present, is terminated with a comma

        Error correction level (Required)
            = H, Q, M, or L

            * H = ultra-high reliability level
            * Q = high reliability level
            * M = standard level (default)
            * L = high density level

        Data input (Required)
            = A or M followed by a comma

            * A = Automatic Input (default). Character Mode is not specified.
              Data character string JIS8 unit, Shift JIS. When the input mode is Automatic Input, the binary codes
              of 0x80 to 0x9F and 0xE0 to 0xFF cannot be set.
            * M = Manual Input. Character Mode must be specified.
              Two types of data input mode exist: Automatic (A) and Manual (M). If A is specified, the
              character mode does not need to be specified. If M is specified, the character mode must be
              specified.

        Character Mode (Required when data input = M)
            = N, A, Bxxxx, or K

            * N = numeric: digits 0 – 9
            * A = alphanumeric: digits 0 – 9, upper case letters A – Z, space, and $%*+-./:) (45 characters)
            * Bxxxx = 8-bit byte mode. The ‘xxxx’ is the number of characters and must be exactly 4 decimal
              digits.
              This handles the 8-bit Latin/Kana character set in accordance with JIS X 0201 (character values
              0x00 to 0xFF).
            * K = Kanji — handles only Kanji characters in accordance with the Shift JIS system based on JIS X
              0208. This means that all parameters after the character mode K should be 16-bit characters. If
              there are any 8-bit characters (such as ASCII code), an error occurs.
              The data to be encoded follows immediately after the last switch.

    Considerations for ^FD When Using the QR Code:

        QR Switches (formatted into the ^FD field data)

        mixed mode <D>
            D = allows mixing of different types of character modes in one code.
            code No. <01 16>
            Value = subtracted from the Nth number of the divided code (must be two digits).

        No. of divisions <02 16>
            Number of divisions (must be two digits).

        parity data <1 byte>
            Parity data value is obtained by calculating at the input data (the original input data
            before divided byte-by-byte through the EX-OR operation).

        error correction level <H, Q, M, L>
            * H = ultra-high reliability level
            * Q = high reliability level
            * M = standard level (default)
            * L = high density level

        character Mode <N, A, B, K>
            * N = numeric
            * A = alphanumeric
            * Bxxxx = 8-bit byte mode. This handles the 8-bit Latin/Kana character set in accordance
              with JIS X 0201 (character values 0x00 to 0xFF).
              xxxx = number of data characters is represented by two bytes of BCD code.
            * K = Kanji — handles only Kanji characters in accordance with the Shift JIS system based
              on JIS X 0208. This means that all parameters after the character mode K should be 16-bit
              characters. If there are any 8-bit characters (such as ASCII code), an error occurs.

        data character string <Data>
            Follows character mode or it is the last switch in the ^FD statement.

        data input <A, M>
            * A = Automatic Input (default). Data character string JIS8 unit, Shift JIS. When the input
              mode is Automatic Input, the binary codes of 0x80 to 0x9F and 0xE0 to 0xFF cannot be
              set.
            * M = Manual Input
              Two types of data input mode exist: Automatic (A) and Manual (M). If A is specified, the character
              mode does not need to be specified. If M is specified, the character mode must be specified.

    ^FD Field Data (Normal Mode)
        Automatic Data Input (A) with Switches
        ^FD
        <error correction level>A,
        <data character string>
        ^FS

    Manual Data Input (M) with Switches
        ^FD
        <error correction level>M,
        <character mode><data character string>
        ^FS

    ^FD Field Data (Mixed Mode – requires more switches)
        Automatic Data Input (A) with Switches
        ^FD
        <D><code No.> <No. of divisions> <parity data>,
        <error correction level> A,
        <data character string>,
        <data character string>,
        < : >,
        <data character string n**>
        ^FS

    Manual Data Input (M) with Switches
        ^FD
        <code No.> <No. of divisions> <parity data>,
        <error correction level> M,
        <character mode 1> <data character string 1>,
        <character mode 2> <data character string 2>,
        < : > < : >,
        <character mode n> <data character string n**>
        ^FS

        n** up to 200 in mixed mode
    """

    def __init__(self, data, model=None, magnification=None, error_correction=None, mask_value=None):
        # TODO: FD data QR switches
        super().__init__(data)
        self._initial_setup(model, magnification, error_correction, mask_value)
        self._add_data()

    def _initial_setup(self, model, magnification, error_correction, mask_value):
        self.zpl.append('^BQN')

        if model is None:
            return
        self._add_value_in_list(model, 'model', (1, 2), True)

        if magnification is None:
            return
        self._add_int_value_in_range(magnification, 'magnification', 1, 10, True)

        if error_correction is None:
            return
        self._add_value_in_list(error_correction, 'error_correction', ('H', 'Q', 'M', 'L'), True)

        if mask_value is None:
            return
        self._add_int_value_in_range(mask_value, 'mask_value', 0, 7, True)


class Postal_Barcode(_1DBarcode):
    """
    Postal Bar Code (^BZ)

    Characters (0-9)

    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    :param code_type: * 0 = Postnet bar code
                      * 1 = Plant Bar Code
                      * 2 = Reserved
                      * 3 = USPS Intelligent Mail bar code
    """

    def __init__(self, data, orientation=None, height=None, print_text=None,
                 text_above=None, code_type=None):
        super().__init__('BZ', data, orientation, None, height, print_text, text_above)
        if code_type is None:
            return
        self._add_int_value_in_range(code_type, 'code_type', 0, 3, True, False)

    def _validate_data(self):
        self._verify_data_numeric(self.data)


class GS1Databar_Barcode(_Barcode):
    """
    GS1 Databar Bar Code (^BR)

    :param gtin_data: GTIN-12 or GTIN13 data
    :param composite_data: optional additional data
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param symbology_type: * 1 = GS1 DataBar Omnidirectional
                           * 2 = GS1 DataBar Truncated
                           * 3 = GS1 DataBar Stacked
                           * 4 = GS1 DataBar Stacked Omnidirectional
                           * 5 = GS1 DataBar Limited
                           * 6 = GS1 DataBar Expanded
                           * 7 = UPC-A
                           * 8 = UPC-E
                           * 9 = EAN-13
                           * 10 = EAN-8
                           * 11 = UCC/EAN-128 and CC-A/B
                           * 12 = UCC/EAN-128 and CC-C
    :param magnification: 1-10
    :param separator_height: 1 or 2
    :param bar_height: bar code height 1-32000 dots
    :param segment_width: 2 - 22 (even numbers only)
    """

    def __init__(self, gtin_data, composite_data=None, orientation='R',
                 symbology_type=1, magnification=3,
                 separator_height=1, bar_height=25, segment_width=22):
        # TODO: Find out more about GTIN-12/GTIN-13 and validate data
        data = str(gtin_data)
        if composite_data:
            data += '|' + composite_data
        super().__init__(data)
        self._initial_build(orientation, symbology_type, magnification,
                            separator_height, bar_height, segment_width)
        self._add_field_data(data)

    @_newline_after
    def _initial_build(self, orientation, symbology_type, magnification,
                       separator_height, bar_height, segment_width):
        self.zpl.append('^BR')

        self._add_orientation(orientation, False)
        self._add_int_value_in_range(symbology_type, 'symbology_type', 1, 12, True)
        self._add_int_value_in_range(magnification, 'magnification', 1, 10, True)
        self._add_value_in_list(separator_height, 'separator_height', (1, 2), True)
        self._add_int_value_in_range(bar_height, 'height', 1, 32000, True)
        # width is only available on GS1 DataBar Expanded (6)
        if symbology_type != 6:
            return
        if segment_width % 2 == 1:
            raise ValueError('width must be even.')
        self._add_int_value_in_range(segment_width, 'width', 2, 22, True)


class UPC_A_Barcode(_1DBarcode):
    """
    UPC-A Bar Code (^BU)

    :param data: barcode data
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 9999)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    :param check_digit: print check digit ('Y', 'N')
    """

    def __init__(self, data, orientation, height, print_text='Y',
                 text_above='N', check_digit='Y'):
        super().__init__('BU', data, orientation, None, height, print_text, text_above, check_digit)
        # Default height max is 32000
        if height > 9999:
            raise ValueError('height must be between 1 and 9999 (inclusive)')

    def _validate_data(self):
        self._verify_data_numeric(self.data)
        if str(self.data).replace('0', '') == '':
            raise ValueError('UPC data cannot be zero.')

    def _process_data(self):
        self.data = str(self.data)
        if len(self.data) < 11:
            self.data = self.data.zfill(11)  # zero pad if needed for 11
        if len(self.data) > 11:
            self.data = self.data[:11]


class UPC_EAN_Extensions_Barcode(_1DBarcode):
    """
    UPC/EAN Extensions Bar Code (^BS)

    :param data: barcode data
    :param orientation: * 'N' - normal
                        * 'R' - rotate 90
                        * 'I' - inverted
                        * 'B' - rotate 270
    :param height: bar code height in dots (1 to 32000)
    :param print_text: print text of data ('Y', 'N')
    :param text_above: print text above barcode ('Y', 'N')
    """

    def __init__(self, data, orientation='N', height=100, print_text='Y', text_above='Y'):
        super().__init__('BS', data, orientation, None, height, print_text, text_above)

    def _validate_data(self):
        self.data = str(self.data)
        if len(self.data) not in (2, 5):
            raise ValueError('UPC/EAN Extension barcode is limited to 2 or 5 digits only.')
        self._verify_data_numeric(self.data)


class ZPLDocument(_BaseZPL):
    """
    Builds ZPL II label data based on methods called and data passed.

    .. note::

     Dots to real measurements based on printer dpi:

        * 150 dpi: 6 dots = 1 mm, 152 dots = 1 in,
        * 200 dpi: 8 dots = 1 mm, 203 dots = 1 in,
        * 300 dpi: 12 dots = 1 mm, 300 dots = 1 in,
        * 600 dpi: 24 dots = 1mm, 600 dots = 1 in
    """

    # TODO: Assure numbers are integers and then convert to str
    # TODO: Detect '^' or '~' on Field Data, is there a way to escape this?
    # TODO: Change Barcode and Field Data with custom error checking
    # TODO: Make Barcode classes for custom handling like UPS

    def __init__(self):
        super().__init__()
        self._newline()

    def add_barcode(self, barcode_object):
        self.zpl.append(str(barcode_object))

    @staticmethod
    def _is_upper_alpha(value):
        if len(value) != 1:
            return False
        if value.isalpha() and value.isupper():
            return True
        return False

    @staticmethod
    def _is_single_digit(value):
        if len(value) != 1:
            return False
        return value.isdigit()

    @_newline_after
    def add_font(self, font_name, orientation=None, character_height=None,
                 character_width=None):
        """
        Specify font to use in text field (^A)

        :param font_name: A-Z or 0-9 of font stored in printer
        :param orientation:
            * 'N' - Normal
            * 'R' - Rotated 90 clockwise
            * 'I' - Inverted
            * 'B' - Bottom Up (270 rotate)
        :param character_height: 10 to 32000 dots
        :param width: 10 to 32000 dots
        """
        self.zpl.append('^A')
        font_name = str(font_name)
        if self._is_upper_alpha(font_name) or self._is_single_digit(font_name):
            self.zpl.append(font_name)
        else:
            raise ValueError("Valid font_name is 'A'-'Z' or '0'-'9'.")

        if orientation is None:
            return
        self._add_orientation(orientation, False)

        if character_height is None:
            return
        self._add_int_value_in_range(character_height, 'character_height', 10, 32000, True)

        if character_width:
            self._add_int_value_in_range(character_width, 'width', 10, 32000, True)

    @_newline_after
    def add_default_font(self, font_name, character_height=None, character_width=None):
        """
        Specify default font to use for all text fields (^CF)

        :param font_name: A-Z or 0-9 of font stored in printer
        :param character_height: 10 to 32000 dots
        :param character_width: 10 to 32000 dots
        """
        self.zpl.append('^CF')
        self.zpl.append(font_name)

        if character_height is None:
            return
        self._add_int_value_in_range(character_height, 'character_height', 10, 32000, True)

        if character_width is None:
            return
        self._add_int_value_in_range(character_width, 'character_width', 10, 32000, True)

    def add_field_block(self, width=0, max_lines=1, dots_between_lines=0,
                        text_justification='L', hanging_indent=0):
        """
        Field Block (^FB)

        :param width: width of text 0 to label width
        :param max_lines: max number of lines in block, 1 to 9999
        :param dots_between_lines: dots between line adjustment -9999 to 9999
        :param text_justification:
            * 'L' - Left
            * 'C' - center
            * 'R' - right
            * 'J' - justified
        :param hanging_indent: 0 to 9999
        """
        self._add_field_block(width, max_lines, dots_between_lines,
                              text_justification, hanging_indent)

    def add_field_data(self, data_list, replace_newlines=False):
        """
        Field Data for Text or Barcode (^FD with 1-many ^FS)

        :param data_list:  if list or tuple, multiple data blocks with '^FS' separator
                           otherwise, single field with value
        :param replace_newlines: If true, replaces \n with \&
        """
        self._add_field_data(data_list, replace_newlines)

    @_newline_after
    def add_zpl_raw(self, zpl_data):
        """
        Used to add raw ZPLII to the document, to cover any ZPL Commands not coded via existing methods.

        :param zpl_data: Raw zpl data
        """
        self.zpl.append(zpl_data)

    @_newline_after
    def add_text_blocks(self, block_rotation, block_width, block_height):
        """

        :param block_rotation: * 'N' - normal
                               * 'R' - rotate 90
                               * 'I' - inverted
                               * 'B' - rotate 270
        :param block_width: 1 to label width in dots
        :param block_height: 1 to label length in dots
        """
        self.zpl.append('^TB')
        self._add_orientation(block_rotation, False)
        # TODO: Get label dimensions in dots for limits.
        label_width = 600 * 4 * 2  # 600 dpi * 4" doubled.
        label_height = 600 * 8 * 2  # 600 dpi * 8" doubled
        self._add_int_value_in_range(block_width, 'block_width', 1, label_width, True)
        self._add_int_value_in_range(block_height, 'block_height', 1, label_height, True)

    @_newline_after
    def add_label_home(self, x_pos=None, y_pos=None):
        """
        Label Home Position (^LH)

        :param x_pos: x axis position in dots (0 to 32000)
        :param y_pos: y axis position in dots (0 to 32000)
        """
        self.zpl.append('^LH')

        if x_pos is None:
            return
        self._add_int_value_in_range(x_pos, 'x_pos', 0, 32000, False)

        if y_pos is None:
            return
        self._add_int_value_in_range(y_pos, 'y_pos', 0, 32000, True)

    @_newline_after
    def add_field_origin(self, x_pos=0, y_pos=0, justification=None):
        """
        Field Origin (^FO)

        Location where Field should start.

        :param x_pos: x axis position in dots (0 to 32000)
        :param y_pos: y axis position in dots (0 to 32000)
        :param justification:
            * 0 - left
            * 1 - right
            * 2 - auto
        """
        self.zpl.append('^FO')
        self._add_int_value_in_range(x_pos, 'x_pos', 0, 32000, False)
        self._add_int_value_in_range(y_pos, 'y_pos', 0, 32000, True)

        if justification is None:
            return
        self._add_value_in_list(justification, 'justification', (0, 1, 2), True)

    @_newline_after
    def add_print_quantity(self, quantity, pause_and_cut_count=0,
                           replicates_of_serial=0,
                           override_pause='N', cut_on_error='Y'):
        """
        Control Printing Quantity and Pausing (^PQ)

        :param quantity: total quantity of labels to print (1 to 99,999,999)
        :param pause_and_cut_count:  number before pause and cut (0 to 99,999,999 with 0 as disabled)
        :param replicates_of_serial: number of serial duplicates (0 to 99,999,999 with 0 as none)
        :param override_pause: override pause count ('Y', 'N')
        :param cut_on_error: cut on RFID void error label ('Y', 'N')
        """
        self.zpl.append('^PQ')
        self._add_int_value_in_range(quantity, 'quantity', 1, 99999999, False)
        self._add_int_value_in_range(pause_and_cut_count, 'pause_and_cut_count', 0, 99999999, True)
        self._add_int_value_in_range(replicates_of_serial, 'replicates_of_serial', 0, 99999999, True)
        self._add_yes_no(override_pause, 'override_pause', True)
        self._add_yes_no(cut_on_error, 'cut_on_error', True)

    @_newline_after
    def add_start_print(self, dot_row_start_printing):
        """
        Start Print (^SP)

        This allows printing parts of label while other is being transmitted and formatted.


        Example:  add_start_print(500), will print Segment 1

           +-------------------------------+  Dot position 0
           |                               |
           |    Label Segment 2            |
           |                               |
           + - - - - - - - - - - - - - - - +  Dot position 500
           |                               |
           |    Label Segment 1            |
           |                               |
           +-------------------------------+  Dot position 1000

        :param dot_row_start_printing: 0 to 32000 to print to for segment
        """
        self.zpl.append('^SP')
        self._add_int_value_in_range(dot_row_start_printing, 'dot_row_start_printing',
                                     0, 32000, False)

    @_newline_after
    def add_serialization_data(self, starting_value, change_value, add_leading_zeros='N'):
        """
        Create data field and increment or decrement values. (^SN)

        :param starting_value: max of 12 digit number
        :param change_value: max of 12 digit number ('-' prefix for decrement)
        :param add_leading_zeros: 'Y' or 'N'
        """
        self.zpl.append('^SN')
        self._add_int_value_in_range(starting_value, 'starting_value', 0, 999999999999, False)
        self._add_int_value_in_range(change_value, 'change_value', -99999999999, 999999999999, True)
        self._add_yes_no(add_leading_zeros, 'add_leading_zeros', True)

    @_newline_after
    def add_barcode_default(self, module_width=None, wide_narrow_ratio=None, height=None):
        """
        Set defaults for bar codes (^BY)

        :param module_width: 1 to 10 dots (default 2)
        :param wide_narrow_ratio: 2.0 to 3.0 is 0.1 increments (default 3.0)
        :param height: bar code height in dots (default 10)
        """
        self.zpl.append('^BY')
        if module_width is None:
            return
        self._add_int_value_in_range(module_width, 'module_width', 1, 10, False)

        if wide_narrow_ratio is None:
            return
        self._add_decimal_value_in_range(wide_narrow_ratio, 'wide_narrow_ratio', 2, 3, True)

        if module_width is None:
            return
        self._add_int_value_in_range(module_width, 'module_width', 1, 10, True)

        if height is None:
            return
        self._add_int_value_in_range(height, 'height', 1, 200, True)

    @_newline_after
    def add_comment(self, comment_text):
        """
        Comment Block (^FX)

        :param comment_text: Text to insert as comment
        """
        self.zpl.append('^FX{}^FS'.format(comment_text))

    @_newline_after
    def add_graphic_box(self, width=1, height=1, border=1, line_color='B', corner_rounding=0):
        """
        Produce Graphic Box on Label (^GB)

        :param width: border to 32000
        :param height: border to 32000
        :param border: 1 to 32000
        :param line_color: * 'B' - black
                           * 'W' - white
        :param corner_rounding: 0 (none) to 8 (heaviest rounding)
        """
        self.zpl.append('^GB')
        self._add_int_value_in_range(width, 'width', border, 32000, False, False)
        self._add_int_value_in_range(height, 'height', border, 32000, True, False)
        self._add_int_value_in_range(border, 'border', 1, 32000, True, False)
        self._add_line_color(line_color, True)
        self._add_int_value_in_range(corner_rounding, 'corner_rounding', 0, 8, True, False)
        self.zpl.append('^FS')

    @_newline_after
    def add_graphic_circle(self, diameter=3, border=1, color='B'):
        """
        Produce Circle on Label (^GC)

        :param diameter: 3 to 4095
        :param border: 1 to 4095
        :param color: * 'B' - black
                      * 'W' - white
        """
        self.zpl.append('^GC')
        self._add_int_value_in_range(diameter, 'diameter', 3, 4095, False, True)
        self._add_int_value_in_range(border, 'border', 1, 4095, True, True)
        self._add_line_color(color, True)
        self.zpl.append('^FS')

    @_newline_after
    def add_graphic_field(self, image, width, height=0, compression_type='A'):
        """
        Produce Graphic Field on Label (^GF)

        :param image: PIL image
        :param width: border to 99999
        :param height: border to 99999
        :param compression_type: * 'A' - ASCII hexadecimal
                                 * 'B' - binary
                                 * 'C' - compressed binary
        """
        if not height:
            height = int(float(image.size[1]) / image.size[0] * width)

        bytesperrow = math.ceil(width / 8.00)

        image = convert_pil_image(image, width, height)
        totalbytes = len(image.tobytes())
        data = binascii.hexlify(image.tobytes()).decode().upper()

        self.zpl.append('^GF{}'.format(compression_type))
        self._add_int_value_in_range(len(data), 'len data', 1, 99999, True, False)
        self._add_int_value_in_range(int(totalbytes), 'width', 1, 99999, True, False)
        self._add_int_value_in_range(bytesperrow, 'height', 1, 99999, True, False)
        self._add_comma(True)
        self.zpl.append(data)

    @_newline_after
    def add_printer_sleep(self, sleep_seconds, shutdown_while_queued):
        """
        Place printer in sleep mode (^ZZ)

        Only valid on battery powered printers.

        :param sleep_seconds: 0 to 9999999 (0 sleep disabled)
        :param shutdown_while_queued: * 'Y' - Shutdown, even if labels are queued
                                      * 'N' - Print labels before shutdown
        """
        self.zpl.append('^ZZ')
        self._add_int_value_in_range(sleep_seconds, 'sleep_seconds', 0, 999999, False)
        self._add_yes_no(shutdown_while_queued, 'shutdown_while_queued', True)

    @property
    def zpl_text(self):
        """
        Renders zpl text as string for debugging.

        :param strip_newline: Default False,
        :return: text string
        """
        return ''.join([str(item)
                        for item
                        in [self._START] + self.zpl + [self._END]])

    @property
    def zpl_bytes(self):
        """
        Renders zpl code as bytestring in UTF-8 formatting.

        This is what you would typically send to a printer.

        :return: byte array
        """
        return bytes(self.zpl_text, 'UTF-8')

    def render_png(self, label_width, label_height,
                   dpmm=8, index=0):
        """
        Uses labelary.com api to generate a PNG file

        See: examples/display_label_png.py

        :param label_width: width in inches
        :param label_height: height in inches
        :param dpmm: dots per mm, default 8
        :param index: label index (only important if you use in label)
        :return: byte array of PNG file
        """
        url = 'http://api.labelary.com/v1/printers/{}dpmm/labels/{}x{}/{}/'
        filled_url = url.format(dpmm, label_width, label_height, index)
        response = requests.post(filled_url, self.zpl_text)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception('Expected status_code 200, received {}\n{}'
                            .format(response.status_code, response.content))
