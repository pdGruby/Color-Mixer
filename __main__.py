import argparse
import warnings
import re

parser = argparse.ArgumentParser()
parser.add_argument(
    '-m', '--mode',
    help='choose the script mode',
    default='mix'
)
parser.add_argument(
    '-c', '--colors',
    help='add colors to be mixed',
    action='append',
    nargs='*'
)

args = parser.parse_args()
if args.mode not in ['mix', 'lowest', 'highest', 'mix-saturate']:
    warnings.warn(
        f'Invalid mode: {args.mode}. The mode value was set to the ''default (mix)'
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

        if self.mode == 'mix':
            new_color = self.return_mixed_colors()
        elif self.mode == 'lowest':
            new_color = self.return_lowest_colors()
        elif self.mode == 'highest':
            new_color = self.return_highest_colors()
        else:
            new_color = self.return_mixed_saturation_for_the_last_color()

        print(
            'New color info:\n'
            f'RED: {new_color[0]}\n'
            f'GREEN: {new_color[1]}\n'
            f'BLUE: {new_color[2]}\n'
            f'ALPHA: {new_color[3]}\n'
            f'HEX: {new_color[4]}\n'
            f'HUE: {round(new_color[5], 2)}\n'
            f'SATURATION: {round(new_color[6], 2)}\n'
            f'LIGHTNESS: {round(new_color[7], 2)}\n'
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
                        f'Invalid color format: {color} at the line number {i} in colors.txt. The value was ignored'
                    )
                    continue

                if bool(re.match(self.hex_pattern, color)):
                    color = Color.convert_hex_to_rgba(color)
                else:
                    color = color.split(',')
                    str_elements_to_int = [int(element) for element in color]
                    color = str_elements_to_int

                rgb = color[:-1]
                hue = self.calc_hue(rgb) / 255
                lightness = 0.5 * (max(rgb) / 255 + min(rgb) / 255)
                if lightness == 1:
                    saturation = 0
                else:
                    saturation = (max(rgb) / 255 - min(rgb) / 255) / (1 - abs(2 * lightness - 1))

                self.red.append(color[0])
                self.green.append(color[1])
                self.blue.append(color[2])
                self.alpha.append(color[3])
                self.hue.append(hue)
                self.lightness.append(lightness)
                self.saturation.append(saturation)

    def read_colors_from_parsed_arguments(self):
        invalid_values = []

        for colors_set in self.colors:
            for color in colors_set:
                color = color.lower().strip().replace('#', '').replace('\n', '').replace(' ', '')

                if not bool(re.match(self.hex_pattern, color)) and not bool(re.match(self.rgba_pattern, color)):
                    invalid_values.append(color)
                    continue

                if bool(re.match(self.hex_pattern, color)):
                    color = Color.convert_hex_to_rgba(color)
                else:
                    color = color.split(',')
                    str_elements_to_int = [int(element) for element in color]
                    color = str_elements_to_int

                rgb = color[:-1]
                hue = self.calc_hue(rgb)
                lightness = 0.5 * (max(rgb) / 255 + min(rgb) / 255)
                if lightness == 1:
                    saturation = 0
                else:
                    saturation = (max(rgb) / 255 - min(rgb) / 255) / (1 - abs(2 * lightness - 1))

                self.red.append(color[0])
                self.green.append(color[1])
                self.blue.append(color[2])
                self.alpha.append(color[3])
                self.hue.append(hue)
                self.lightness.append(lightness)
                self.saturation.append(saturation)

        if invalid_values:
            warnings.warn(
                f'Some invalid values for colors (-c or --colors) occured: {invalid_values}. The invalid values were ignored'
            )

    def return_mixed_colors(self):
        red = round(sum(self.red)/len(self.red))
        green = round(sum(self.green) / len(self.green))
        blue = round(sum(self.blue) / len(self.blue))
        alpha = round(sum(self.alpha) / len(self.alpha))
        hex_ = self.convert_rgba_to_hex([red, green, blue, alpha])
        hue = sum(self.hue) / len(self.hue)
        saturation = sum(self.saturation) / len(self.saturation)
        lightness = sum(self.lightness) / len(self.lightness)

        return red, green, blue, alpha, hex_, hue, saturation, lightness

    def return_lowest_colors(self):
        red = min(self.red)
        green = min(self.green)
        blue = min(self.blue)
        alpha = min(self.alpha)
        hex_ = self.convert_rgba_to_hex([red, green, blue, alpha])
        hue = min(self.hue)
        saturation = min(self.saturation)
        lightness = min(self.lightness)

        return red, green, blue, alpha, hex_, hue, saturation, lightness

    def return_highest_colors(self):
        red = max(self.red)
        green = max(self.green)
        blue = max(self.blue)
        alpha = max(self.alpha)
        hex_ = self.convert_rgba_to_hex([red, green, blue, alpha])
        hue = max(self.hue)
        saturation = max(self.saturation)
        lightness = max(self.lightness)

        return red, green, blue, alpha, hex_, hue, saturation, lightness

    def return_mixed_saturation_for_the_last_color(self):
        red = self.red[-1]
        green = self.green[-1]
        blue = self.blue[-1]
        alpha = self.alpha[-1]
        hex_ = self.convert_rgba_to_hex([red, green, blue, alpha])
        hue = self.hue[-1]
        saturation = sum(self.saturation[:-1])/len(self.saturation[:-1])
        lightness = self.lightness[-1]

        return red, green, blue, alpha, hex_, hue, saturation, lightness

    @staticmethod
    def convert_rgba_to_hex(color):
        new_color = '#{:02x}{:02x}{:02x}{:02x}'.format(*color)
        return new_color

    @staticmethod
    def convert_hex_to_rgba(color):
        color = list(color)

        letters_to_int = {
            'a': 10, 'b': 11, 'c': 12,
            'd': 13, 'e': 14, 'f': 15
        }

        color_with_only_ints = []
        for element in color:
            try:
                color_with_only_ints.append(letters_to_int[element])
            except KeyError:
                color_with_only_ints.append(int(element))

        if len(color_with_only_ints) == 3:
            updated_color_to_6_digits = []
            for element in color_with_only_ints:
                updated_color_to_6_digits.extend([element] * 2)
            color_with_only_ints = updated_color_to_6_digits

        R = (color_with_only_ints[0] * 16) + color_with_only_ints[1]
        G = (color_with_only_ints[2] * 16) + color_with_only_ints[3]
        B = (color_with_only_ints[4] * 16) + color_with_only_ints[5]

        if len(color_with_only_ints) == 8:
            A = (color_with_only_ints[6] * 16) + color_with_only_ints[7]
            new_color = [R, G, B, A]
        else:
            new_color = [R, G, B, 255]

        return new_color

    @staticmethod
    def calc_hue(rgb):
        r, g, b = rgb

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

        return round(hue, 1)


Color(mode=args.mode, colors=args.colors).run_app()
# Wywołuj błąd, gdy któraś z wprowawdzonych wartości dla RGBA będzie > 255 albo mniejsza od 0. Pomyśl, czy trzeba wywołać jakieś inne błędy
# Shebang
# Pomyśl czy da się zrobić tak, żeby wszystko co będzie wpisane po -m (lub bez tego) było brane jako argumenty bez pisania -c
