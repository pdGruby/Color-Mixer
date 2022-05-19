#!/usr/bin/env python3

import argparse
import warnings
import re
import colorsys

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode', help='select script mode: mix, lowest, highest, mix-saturate', default='mix')
parser.add_argument('colors', nargs='*')

args = parser.parse_args()
if args.mode not in ['mix', 'lowest', 'highest', 'mix-saturate']:
    warnings.warn(
        f"Invalid mode: {args.mode}. The mode value was set to the default (mix). "
        f"Valid modes: mix, lowest, highest, mix-saturate"
    )
    args.mode = 'mix'


class Color:
    def __init__(self, mode, colors):
        self.mode = mode
        self.colors = colors

        self.red = []
        self.green = []
        self.blue = []
        self.alpha = []
        self.lightness = []
        self.hue = []
        self.saturation = []

        self.hex_pattern = re.compile('^([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$')
        self.rgba_pattern = re.compile('^([0-9]{1,3},){3}[0-9]{1,3}$')

    def run_app(self):
        self.read_colors_from_txt_file()
        self.read_colors_from_parsed_arguments()

        if len(self.red) == 0:
            raise ValueError(
                'No valid colors were found - can not create a new color from nothing'
            )

        if self.mode == 'mix':
            new_color = self.return_mixed_colors()
        elif self.mode == 'lowest':
            new_color = self.return_lowest_colors()
        elif self.mode == 'highest':
            new_color = self.return_highest_colors()
        else:
            new_color = self.return_mixed_saturation_for_the_last_color()

        if len(new_color) != 8:  # when self.mode != 'mix_saturate'
            hue = self.calc_hue(new_color[:3])
            lightness, saturation = self.calc_lightness_and_saturation(new_color[:3])
        else:
            hue = new_color[5]
            saturation = new_color[6]
            lightness = new_color[7]

        print(
            '\nNew color info:\n'
            f'RED: {new_color[0]}\n'
            f'GREEN: {new_color[1]}\n'
            f'BLUE: {new_color[2]}\n'
            f'ALPHA: {new_color[3]}\n'
            f'HEX: {new_color[4]}\n'
            f'HUE: {round(hue, 2)}\n'
            f'SATURATION: {round(saturation, 2)}\n'
            f'LIGHTNESS: {round(lightness, 2)}\n'
        )

    def read_colors_from_txt_file(self):
        with open('colors.txt', 'r') as colors_file:
            colors_in_file = colors_file.readlines()

        for i, color in enumerate(colors_in_file):
            color = color.lower().strip().replace('#', '').replace('\n', '').replace(' ', '')

            if not color:
                continue

            if not bool(re.match(self.hex_pattern, color)) and not bool(re.match(self.rgba_pattern, color)):
                warnings.warn(
                    f'Invalid color format: {color} in line number {i} in colors.txt. The line was ignored'
                )
                continue

            if bool(re.match(self.hex_pattern, color)):
                color = Color.convert_hex_to_rgba(color)
            else:
                color = color.split(',')
                color = [int(element) for element in color]

            if not Color.check_if_valid_rgba_values(color):
                warnings.warn(
                    f'Invalid value in: {color} in line number {i} in colors.txt. The line was ignored'
                )
                continue

            self.update_class_attributes(color)

    def read_colors_from_parsed_arguments(self):
        if self.colors is None:
            return None

        for color in self.colors:
            color = color.lower().strip().replace('#', '').replace('\n', '').replace(' ', '')

            if not bool(re.match(self.hex_pattern, color)) and not bool(re.match(self.rgba_pattern, color)):
                warnings.warn(
                    f'Invalid color format: {color} in CLI. The color was ignored'
                )
                continue

            if bool(re.match(self.hex_pattern, color)):
                color = Color.convert_hex_to_rgba(color)
            else:
                color = color.split(',')
                color = [int(element) for element in color]

            if not Color.check_if_valid_rgba_values(color):
                warnings.warn(
                    f'Invalid value in: {color} in CLI. The color was ignored'
                )
                continue

            self.update_class_attributes(color)

    def update_class_attributes(self, color):
        rgb = [color[0], color[1], color[2]]
        hue = self.calc_hue(rgb)
        lightness, saturation = self.calc_lightness_and_saturation(rgb)

        self.red.append(color[0])
        self.green.append(color[1])
        self.blue.append(color[2])
        self.alpha.append(color[3])
        self.hue.append(hue)
        self.lightness.append(lightness)
        self.saturation.append(saturation)

    def return_mixed_colors(self):
        red = round(sum(self.red)/len(self.red))
        green = round(sum(self.green) / len(self.green))
        blue = round(sum(self.blue) / len(self.blue))
        alpha = round(sum(self.alpha) / len(self.alpha))
        hex_ = self.convert_rgba_to_hex([red, green, blue, alpha])

        return red, green, blue, alpha, hex_

    def return_lowest_colors(self):

        red = round(min(self.red))
        green = round(min(self.green))
        blue = round(min(self.blue))
        alpha = round(min(self.alpha))
        hex_ = self.convert_rgba_to_hex([red, green, blue, alpha])

        return red, green, blue, alpha, hex_

    def return_highest_colors(self):
        red = round(max(self.red))
        green = round(max(self.green))
        blue = round(max(self.blue))
        alpha = round(max(self.alpha))
        hex_ = self.convert_rgba_to_hex([red, green, blue, alpha])

        return red, green, blue, alpha, hex_

    def return_mixed_saturation_for_the_last_color(self):
        alpha = round(self.alpha[-1])
        hue = round(self.hue[-1])
        saturation = round(sum(self.saturation[:-1])/len(self.saturation[:-1]), 2)
        lightness = round(self.lightness[-1], 2)

        red, green, blue = colorsys.hls_to_rgb(hue/360, lightness, saturation)
        red = round(red * 255)
        green = round(green * 255)
        blue = round(blue * 255)
        hex_ = self.convert_rgba_to_hex([red, green, blue, alpha])

        return red, green, blue, alpha, hex_, hue, saturation, lightness

    @staticmethod
    def check_if_valid_rgba_values(color):
        for value in color:
            if value > 255 or value < 0:
                return False

        return True

    @staticmethod
    def convert_rgba_to_hex(color):
        new_color = '#{:02x}{:02x}{:02x}{:02x}'.format(*color)

        return new_color

    @staticmethod
    def convert_hex_to_rgba(color):
        if len(color) == 3:
            color = f'{color[0] * 2}{color[1] * 2}{color[2] * 2}'

        if len(color) == 6:
            color += 'ff'

        new_color = list(int(color[i:i+2], 16) for i in (0, 2, 4, 6))

        return new_color

    @staticmethod
    def calc_hue(rgb):
        standardized_rgb = [rgb[0]/255, rgb[1]/255, rgb[2]/255]
        r, g, b = standardized_rgb

        if max(standardized_rgb) == 0:
            return 0

        if r == g == b:
            return 0

        if r >= g >= b:
            hue = 60 * ((g - b) / (r - b))

        elif g > r >= b:
            hue = 60 * (2 - (r - b) / (g - b))

        elif g >= b > r:
            hue = 60 * (2 + (b - r) / (g - r))

        elif b > g > r:
            hue = 60 * (4 - (g - r) / (b - r))

        elif b > r >= g:
            hue = 60 * (4 + (r - g) / (b - g))

        elif r >= b > g:
            hue = 60 * (6 - (b - g) / (r - g))

        else:
            raise ValueError(
                'Can not calculate the hue value!'
            )

        return hue

    @staticmethod
    def calc_lightness_and_saturation(rgb):
        standardized_rgb = [rgb[0] / 255, rgb[1] / 255, rgb[2] / 255]
        maximum = max(standardized_rgb)
        minimum = min(standardized_rgb)

        if maximum == 0:
            return 0, 0

        if maximum == 1 and minimum == 1:
            return 1, 0

        lightness = 0.5 * (maximum + minimum)
        if lightness <= 0.5:
            saturation = (maximum - minimum) / (maximum + minimum)
        else:
            saturation = (maximum - minimum) / (2 - maximum - minimum)

        return lightness, saturation


Color(mode=args.mode, colors=args.colors).run_app()
