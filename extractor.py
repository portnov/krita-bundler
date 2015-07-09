
from lxml import etree
import io

try:
    import Image
    pil_available = True
except ImportError:
    try:
        from PIL import Image
        pil_available = True
    except ImportError:
        print("Warning: Neither PIL nor Pillow is available. Checking of bundle structure is not possible.")
        pil_available = False

if pil_available:

    class KPP(object):
        def __init__(self, filename, data=None):
            self.filename = filename
            self.data = data

        def get_preset_text(self):
            try:
                if self.data is not None:
                    stream = io.BytesIO(self.data)
                    self.image = Image.open(stream)
                else:
                    self.image = Image.open(self.filename)
            except Exception as e:
                print("Error: {}: can not read image: {}".format(self.filename, e))
                return None

            if self.image.format != 'PNG':
                print("Error: {} is not a PNG file".format(self.filename))
                return None
            if self.image.text is None:
                print("Error: {} does not contain text data".format(self.filename))
                return None
            if 'preset' not in self.image.text:
                print("Error: {} does not contain Krita preset".format(self.filename))
                return None

            return self.image.text['preset']

        def check(self):
            text = self.get_preset_text()
            if text is None:
                return None

            try:
                preset = etree.fromstring(text)
                return preset
            except etree.XMLSyntaxError as e:
                print("{} has invalid XML in preset info:\n{}".format(self.filename, e))
                return None

        def get_links(self):
            result = dict()

            preset = self.check()
            if preset is None:
                return result

            item = preset.find('param[@name="Texture/Pattern/PatternFileName"]')
            if item is not None:
                result['PatternFileName'] = item.text

            item = preset.find('param[@name="requiredBrushFile"]')
            if item is not None:
                result['requiredBrushFile'] = item.text

            return result

else:

    class KPP(object):
        def __init__(self, filename):
            pass

        def check(self):
            return dict()

