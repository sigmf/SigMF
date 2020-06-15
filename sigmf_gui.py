# Copyright 2020 The Johns Hopkins University Applied Physics Laboratory LLC.  All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from PySimpleGUI import *
from sigmf.sigmffile import SigMFFile, fromarchive, dtype_info
from sigmf.archive import SIGMF_ARCHIVE_EXT
import os
import warnings

warnings.filterwarnings("error")

validate_button = Button('Update', bind_return_key=False, enable_events=True)
submit_button = Button('Save Archive', disabled=True, button_color=('white', '#D3D3D3'))
load_button = Button('Load', key='Load Archive')
combo_button = InputCombo((), size=(20, 1), enable_events=True, key='Capture Combo')


class Unit:
    MHZ = 'MHz'
    US = 'us'
    DBI = 'dBi'

    @staticmethod
    def convert(unit, value: float):
        if unit is None:
            return input

        if unit == Unit.MHZ:
            return value * 1e6
        elif unit == Unit.US:
            return value * 1e-6
        else:
            return value


class WindowElementGroup():
    def __init__(self, element_list, sigmf_tags, req_tags, el_types, el_units, el_tooltip, el_text, el_help,
                 el_multiline, el_selector, el_checkbox, el_size):
        self.element_list = element_list
        self.sigmf_tags = sigmf_tags
        self.req_tags = req_tags
        self.el_types = el_types
        self.el_units = el_units
        self.el_tooltips = el_tooltip
        self.el_text = el_text
        self.el_help = el_help
        self.el_multiline = el_multiline
        self.el_selector = el_selector
        self.el_checkbox = el_checkbox
        self.el_size = el_size

    def iter(self):
        for el in self.element_list:
            yield el

    def iter_x(self, x):
        next_tuple = ()
        for el in self.iter():
            next_tuple += (el,)
            if len(next_tuple) == x:
                yield next_tuple
                next_tuple = ()
        if next_tuple != ():
            yield next_tuple + tuple([None] * (x - len(next_tuple)))

    def get_tag(self, key):
        return key if key not in self.sigmf_tags else self.sigmf_tags[key]

    def get_el(self, tag):
        if tag not in self.sigmf_tags:
            return tag
        else:
            for el, val in self.sigmf_tags:
                if val == tag:
                    return el
            raise show_error('Element {} is not in window group key,tag list'.format(tag))


class WindowInput(WindowElementGroup):
    DATA_FILE = 'Data File'
    OUTPUT_FOLDER = 'Output Folder'
    LOAD_PATH = 'Load saved archive'
    DATA_TYPE_COMPLEX = 'Complex?'
    DATA_TYPE_UNSIGNED = 'Unsigned?'
    DATA_TYPE_FIXEDPOINT = 'Fixedpoint?'
    DATA_SAMPLE_SIZE = 'Data Sample Size'
    DATA_BYTE_ORDER = 'Data Byte Order'

    def __init__(self):
        DATA_OFFSET = 'Data Offset'
        DESCRIPTION = 'Description'
        AUTHOR = 'Author'
        DATE = 'Date'
        HARDWARE = 'Hardware'
        RECEIVER_RF = 'Receiver RF'
        RECEIVER_LAT = 'Receiver Lat'
        RECEIVER_LON = 'Receiver Lon'
        NORM_TECH = 'Normalization Technique'
        ANTEN_POL = 'Antenna Polarization'
        ANTEN_GAIN = 'Antenna Gain'

        self.core_element_list = [WindowInput.DATA_TYPE_COMPLEX, WindowInput.DATA_TYPE_UNSIGNED,
                                  WindowInput.DATA_TYPE_FIXEDPOINT, WindowInput.DATA_SAMPLE_SIZE,
                                  WindowInput.DATA_BYTE_ORDER, DATA_OFFSET, DESCRIPTION, AUTHOR, DATE]
        self.secondary_element_list = [HARDWARE, NORM_TECH, RECEIVER_LAT, ANTEN_POL, RECEIVER_LON, ANTEN_GAIN,
                                       RECEIVER_RF]
        self.file_element_list = [WindowInput.DATA_FILE, WindowInput.OUTPUT_FOLDER]
        self.partial_component_list = [WindowInput.DATA_TYPE_COMPLEX, WindowInput.DATA_TYPE_UNSIGNED,
                                       WindowInput.DATA_TYPE_FIXEDPOINT, WindowInput.DATA_SAMPLE_SIZE,
                                       WindowInput.DATA_BYTE_ORDER]
        sigmf_tags = {DESCRIPTION: SigMFFile.DESCRIPTION_KEY,
                      AUTHOR: SigMFFile.AUTHOR_KEY, DATE: SigMFFile.DATETIME_KEY, HARDWARE: SigMFFile.HW_KEY,
                      RECEIVER_RF: SigMFFile.FREQUENCY_KEY, RECEIVER_LAT: SigMFFile.LAT_KEY,
                      RECEIVER_LON: SigMFFile.LON_KEY}
        req_tags = [WindowInput.DATA_FILE, WindowInput.DATA_SAMPLE_SIZE, WindowInput.DATA_BYTE_ORDER, RECEIVER_RF]
        el_types = {WindowInput.DATA_TYPE_COMPLEX: bool, WindowInput.DATA_TYPE_UNSIGNED: bool,
                    WindowInput.DATA_TYPE_FIXEDPOINT: bool, DATA_OFFSET: int, RECEIVER_LAT: float,
                    RECEIVER_LON: float, ANTEN_GAIN: float, RECEIVER_RF: float}
        el_units = {ANTEN_GAIN: Unit.DBI, RECEIVER_RF: Unit.MHZ}
        el_tooltip = {DATE: 'YYYY-MM-DD',
                      DATA_OFFSET: 'int: bit offset from start of data file of first element'}
        el_text = {}
        el_help = {WindowInput.DATA_BYTE_ORDER: 'Data Type Help'}
        el_multiline = [DESCRIPTION]
        el_selector = {WindowInput.DATA_SAMPLE_SIZE: [8, 16, 32],
                       WindowInput.DATA_BYTE_ORDER: ['big endian', 'little endian']}
        el_checkbox = [WindowInput.DATA_TYPE_COMPLEX, WindowInput.DATA_TYPE_UNSIGNED, WindowInput.DATA_TYPE_FIXEDPOINT]
        el_size = {WindowInput.DATA_TYPE_COMPLEX: (3, 1), WindowInput.DATA_TYPE_UNSIGNED: (3, 1),
                   WindowInput.DATA_TYPE_FIXEDPOINT: (3, 1), WindowInput.DATA_SAMPLE_SIZE: (4, 1),
                   WindowInput.DATA_BYTE_ORDER: (15, 1)}
        self.first_line_size = 5
        super().__init__(self.core_element_list + self.secondary_element_list, sigmf_tags, req_tags, el_types, el_units,
                         el_tooltip, el_text, el_help, el_multiline, el_selector, el_checkbox, el_size)

    def iter_core(self):
        for el in self.core_element_list:
            yield el

    def iter_secondary(self):
        for el in self.secondary_element_list:
            yield el

    def iter_x_secondary(self, x):
        next_tuple = ()
        for el in self.iter_secondary():
            next_tuple += (el,)
            if len(next_tuple) == x:
                yield next_tuple
                next_tuple = ()
        if next_tuple != ():
            yield next_tuple + tuple([None] * (x - len(next_tuple)))


class CaptureData(WindowElementGroup):
    START_INDEX = 'Start Index'

    def __init__(self):
        SAMPLING_RATE = 'Sampling Rate'
        EMITTER = 'Emitter'
        MODE_OF_OPERATION = 'Mode(s) of Operation'
        SIGNAL_RF = 'Signal RF'
        SIGNAL_BANDWIDTH = 'Signal Bandwidth'
        MODULATION = 'Modulation'
        PRF = 'PRF'
        STAGGER = 'Stagger'
        FREQUENCY_HOPPING = 'Frequency Hopping'
        PW = 'Pulse Width'
        BEAM_PATTERN = 'Observed Beam Pattern'
        SNR = 'Observed SNR'
        CHIP_RATE = 'Chip Rate'

        COMMENT = 'Comment'

        self.annotation_element_list = [COMMENT]
        element_list = [CaptureData.START_INDEX, SAMPLING_RATE, EMITTER, MODE_OF_OPERATION, SIGNAL_RF, SIGNAL_BANDWIDTH,
                        MODULATION, PRF, STAGGER, FREQUENCY_HOPPING, PW, BEAM_PATTERN, SNR,
                        CHIP_RATE] + self.annotation_element_list

        sigmf_tags = {CaptureData.START_INDEX: SigMFFile.START_INDEX_KEY, SAMPLING_RATE: SigMFFile.SAMPLE_RATE_KEY,
                      COMMENT: SigMFFile.COMMENT_KEY}
        req_tags = [CaptureData.START_INDEX, SAMPLING_RATE]
        el_types = {CaptureData.START_INDEX: int, SAMPLING_RATE: float, SIGNAL_RF: float, SIGNAL_BANDWIDTH: float,
                    PRF: float, PW: float, SNR: float, CHIP_RATE: float}
        el_units = {SIGNAL_RF: Unit.MHZ, PW: Unit.US, SIGNAL_BANDWIDTH: Unit.MHZ}
        el_tooltip = {CaptureData.START_INDEX: 'int: start index in file of capture'}
        el_text = {}
        el_help = {}
        el_multiline = []
        el_selector = {}
        el_checkbox = []
        el_size = {}
        super().__init__(element_list, sigmf_tags, req_tags, el_types, el_units, el_tooltip, el_text, el_help,
                         el_multiline, el_selector, el_checkbox, el_size)


def update_dictionary(dictionary, key, val):
    dictionary[key] = val


def add_sigmf_field(funct, values, field_name, *args, required=False, type=None, unit=None, **kwargs):
    input = str(values[field_name]) if field_name in values else ''
    print(args)
    print(input)
    print(kwargs)
    if input != '':
        if type == int:
            if '.' in input:
                show_error('Expected an integer for: {}'.format(field_name))
                return False
            try:
                input = int(input)
            except:
                show_error('Expected an integer for: {}'.format(field_name))
                return False
        elif type == float:
            try:
                input = float(input)
            except:
                show_error('Expected a double for: {}'.format(field_name))
                return False
        elif type == bool:
            try:
                if input != 'False' and input != 'True':
                    raise ValueError('Unexpected input for boolean')
                input = True if input == 'True' else False
            except:
                show_error('Expected a bool for: {}'.format(field_name))
                return False
        Unit.convert(unit, input)
        try:
            if kwargs:
                funct(*args, input, **kwargs)
            else:
                funct(*args, input)
        except UserWarning as w:
            Popup('Warning: '.format(repr(w)), title='Warning')
        except Exception as e:
            show_error(repr(e))
            return False
    elif required:
        show_error('Missing required field: {}'.format(field_name))
        return False
    return True


def show_error(message):
    PopupError(message, title='Error', line_width=60)


def validate_data(file):
    isValid = file.validate()
    print('Valid: ', isValid)
    if not isValid:
        show_error('Metadata not valid: ' + isValid.error)
        submit_button.Update(disabled=True)
        return False
    else:
        PopupOK('Data is valid\n', file.dumps(pretty=True), title='')
        return True


def update_capture_screen(capture_data_input, capture_text_blocks, capture_dict):
    for el in capture_data_input.iter():
        tag = capture_data_input.get_tag(el)
        if capture_dict is not None and tag in capture_dict:
            capture_text_blocks[el].Update(value=capture_dict[tag])
        else:
            capture_text_blocks[el].Update(value='')


def update_global_screen(window_data_input, window_text_blocks, window_dict, archive):
    data_type = window_dict[SigMFFile.DATATYPE_KEY]
    data_info = dtype_info(data_type)
    sample_size = 32 if '32' in data_type else 16 if '16' in data_type else 8 if '8' in data_type else None
    assert sample_size is not None
    window_text_blocks[WindowInput.DATA_TYPE_FIXEDPOINT].Update(bool(data_info['is_fixedpoint']))
    window_text_blocks[WindowInput.DATA_TYPE_UNSIGNED].Update(bool(data_info['is_unsigned']))
    window_text_blocks[WindowInput.DATA_TYPE_COMPLEX].Update(bool(data_info['is_complex']))
    window_text_blocks[WindowInput.DATA_SAMPLE_SIZE].Update(sample_size)
    window_text_blocks[WindowInput.DATA_BYTE_ORDER].Update(
        'little endian' if '<' in str(data_info['sample_dtype']) else 'big endian')

    for el in window_data_input.iter():
        if el in window_data_input.partial_component_list:
            continue
        tag = window_data_input.get_tag(el)
        if window_dict is not None and tag in window_dict:
            window_text_blocks[el].Update(value=window_dict[tag])
        else:
            window_text_blocks[el].Update(value='')
    window_text_blocks[WindowInput.DATA_FILE].Update(value=archive.data_file)


def add_capture(capture_data_input, values, capture_selector_dict, file_data, from_archive=False):
    capture_dict = dict()
    added = True
    for el in capture_data_input.iter():
        req_field = True if el in capture_data_input.req_tags else False
        el_type = capture_data_input.el_types.get(el, None)
        el_unit = capture_data_input.el_units.get(el, None)
        field = capture_data_input.get_tag(el) if from_archive else el
        added = added and add_sigmf_field(update_dictionary, values, field, capture_dict,
                                          capture_data_input.get_tag(el),
                                          required=req_field, type=el_type, unit=el_unit)
    if not added:
        # requirement not given
        return False
    annotation_dict = {capture_data_input.get_tag(CaptureData.START_INDEX): capture_dict[
        capture_data_input.get_tag(CaptureData.START_INDEX)]}
    tmp_capture_subset = {}
    for field in capture_data_input.element_list + [CaptureData.START_INDEX]:
        tag = capture_data_input.get_tag(field)
        if tag in capture_dict:
            if field in capture_data_input.annotation_element_list:
                annotation_dict[tag] = capture_dict[tag]
            else:
                tmp_capture_subset[tag] = capture_dict[tag]

    add_capture = True
    for capture in file_data.get_captures():
        if int(capture[capture_data_input.get_tag(CaptureData.START_INDEX)]) == int(
                capture_dict[capture_data_input.get_tag(CaptureData.START_INDEX)]):
            add_capture = False
            break
    if add_capture:
        add_sigmf_field(SigMFFile.add_capture, tmp_capture_subset, capture_data_input.get_tag(CaptureData.START_INDEX),
                        file_data,
                        metadata=tmp_capture_subset, type=capture_data_input.el_types[CaptureData.START_INDEX])

        capture_length = 0
        try:
            capture_length = file_data._count_samples()
        except Exception as e:
            show_error('{}\n{}'.format(repr(e), 'In call - count_samples()'))
        if capture_length < 1:
            show_error('No samples in file. Make sure you have selected your input data file')
            return False

        add_sigmf_field(SigMFFile.add_annotation, annotation_dict, capture_data_input.get_tag(CaptureData.START_INDEX),
                        file_data,
                        length=capture_length, metadata=annotation_dict,
                        type=capture_data_input.el_types[CaptureData.START_INDEX])

    new_values = combo_button.Values
    new_val = 'Capture {}'.format(capture_dict[capture_data_input.get_tag(CaptureData.START_INDEX)])
    capture_selector_dict.update({new_val: capture_dict})
    if new_val not in list(new_values):
        new_values = list(new_values) + [new_val]
        combo_button.Update(values=tuple(new_values), value=new_val)


def run_gui():
    window_input = WindowInput()
    capture_data_input = CaptureData()
    capture_text_blocks = dict()
    window_text_blocks = dict()
    f = SigMFFile()
    capture_selector_dict = dict()

    layout = [[Text('This is the APL SIGMF tool to archive RF datasets', size=(80, 1))],
              [Text('Enter your data and signal captures below. You must include', auto_size_text=True),
               Text('required', text_color='red', font=DEFAULT_FONT + ('italic',), auto_size_text=True),
               Text('fields.', size=(50, 1), auto_size_text=True)],
              [Text('_' * 150, auto_size_text=True)]]

    layout.append([Text('Global Data', font=('Arial', 12, 'bold'))])
    num_components = 0
    line = []
    for el in window_input.iter_core():
        size = (30, 1) if len(line) == 0 else (None, None)
        auto_size = True if len(line) == 0 else (10, 1)
        line.extend([Text(el, justification='right', size=size,
                          text_color='red' if el in window_input.req_tags else None, auto_size_text=auto_size)])
        if el in window_input.el_multiline:
            window_text_blocks.update({el: Multiline(window_input.el_text.get(el, ''), key=el,
                                                     tooltip=window_input.el_tooltips.get(el, None), size=(30, 2))})
        elif el in window_input.el_selector:
            window_text_blocks.update({el: Combo(values=window_input.el_selector[el], key=el,
                                                 size=window_input.el_size.get(el, (None, None)))})
        elif el in window_input.el_checkbox:
            window_text_blocks.update({el: Checkbox(window_input.el_text.get(el, ''), key=el,
                                                    size=window_input.el_size.get(el, (None, None)))})
        else:
            window_text_blocks.update({el: InputText(window_input.el_text.get(el, ''), key=el,
                                                     tooltip=window_input.el_tooltips.get(el, None))})
        line.append(window_text_blocks[el])

        if el in window_input.el_units:
            line.append(Text(window_input.el_units[el]))

        num_components += 1
        if num_components < window_input.first_line_size:
            continue
        layout.append(line)
        line = []

    for el1, el2 in window_input.iter_x_secondary(2):
        line = []
        for el, size in zip([el1, el2], [30, 22]):
            if el is None:
                continue
            color = 'red' if el in window_input.req_tags else None
            window_text_blocks.update({el: InputText(window_input.el_text.get(el, ''), key=el,
                                                     tooltip=window_input.el_tooltips.get(el, None))})
            line.extend([Text(el, justification='right', size=(size, 1), text_color=color), window_text_blocks[el]])
            if el in window_input.el_units:
                line.append(Text(window_input.el_units[el], size=(5, 1)))
            else:
                line.append(Text('', size=(5, 1)))
        layout.append(line)

    layout.extend(
        [[Text('_' * 150, auto_size_text=True)],
         [Text('Individual Capture Data', font=('Arial', 12, 'bold'))],
         [Text('Capture Selector', auto_size_text=True), combo_button, Text('', size=(10, 1)),
          Button('Add Capture', enable_events=True), Button('Remove Capture', enable_events=True, size=(15, 1)),
          Button('Clear Capture', enable_events=True, size=(15, 1))]]
    )

    for el1, el2, el3 in capture_data_input.iter_x(3):
        line = []
        for el in [el1, el2, el3]:
            if el is None:
                continue
            capture_text_blocks.update({el: InputText(key=el, tooltip=capture_data_input.el_tooltips.get(el, None))})
            color = 'red' if el in capture_data_input.req_tags else None
            line.extend([Text(el, justification='right', size=(20, 1), text_color=color), capture_text_blocks[el]])
            if el in capture_data_input.el_units:
                line.append(Text(capture_data_input.el_units[el], size=(5, 1)))
            else:
                line.append(Text('', size=(5, 1)))
        layout.append(line)

    window_text_blocks.update(
        {WindowInput.DATA_FILE: InputText('', key=WindowInput.DATA_FILE)})
    layout.extend(
        [[Text('_' * 150, auto_size_text=True)],
         [Text('Data Location', font=('Arial', 12, 'bold'))],
         [Text(WindowInput.DATA_FILE, size=(30, 1), justification='right', text_color='red'),
          window_text_blocks[WindowInput.DATA_FILE], FileBrowse()],
         [Text(WindowInput.OUTPUT_FOLDER, size=(30, 1), justification='right'),
          InputText('', key=WindowInput.OUTPUT_FOLDER), FolderBrowse(), submit_button],
         [Text(WindowInput.LOAD_PATH, size=(30, 1), justification='right'), InputText('', key=WindowInput.LOAD_PATH),
          FileBrowse(file_types=(("Archive Files", "*.sigmf"),)), load_button],
         [validate_button, Button('View Data')]]
    )

    window = Window('APL SigMF Archive Creator',
                    auto_size_buttons=False,
                    default_element_size=(20, 1),
                    auto_size_text=False,
                    default_button_element_size=(10, 1)
                    ).Layout(layout)

    while True:
        validate_button.Update(text='Update')
        load_button.Update(text='Load')
        submit_button.Update(text='Save Archive')

        window.Refresh()
        event, values = window.Read()
        print(event, values)
        if event == 'Load Archive':
            load_path = values[WindowInput.LOAD_PATH]
            if load_path == '':
                show_error('No archive file provided')
                continue

            load_button.Update(text='Loading...')
            window.Refresh()
            print('reading from ', values[WindowInput.LOAD_PATH])
            f = fromarchive(values[WindowInput.LOAD_PATH])
            update_global_screen(window_input, window_text_blocks, f.get_global_info(), f)
            capture_selector_dict = {}
            for capture in f.get_captures():
                add_capture(capture_data_input, capture, capture_selector_dict, f, from_archive=True)

        elif event == 'Data Type Help':
            PopupOK(
                'Format: <TypeCharacters><ElementBitSize>_<Endianness>\n\n'
                '\tTypeCharacters:\n'
                '\t\tUnsigned data: \"u\"\n'
                '\t\tComplex data: \"c\"\n'
                '\t\tFixedpoint data: \"f\"\n'
                '\tElementBitSize:\n'
                '\t\t32 bits, 16 bits, or 8 bits\n'
                '\tEndianness:\n'
                '\t\tl: Little Endian\n'
                '\t\tb: Big Endian\n\n\n\n'
                'Example: \"uc32_l\"\n'
                'Unsigned complex data where each element is 32 bits, or 64 bits total, formatted in little endian.',
                title='Data Type Help'
            )
        elif event == 'Update':
            validate_button.Update(text='Validating...')
            window.Refresh()
            window_data_type_dict = {}
            added = True
            for el in window_input.iter():
                req_field = True if el in window_input.req_tags else False
                el_type = window_input.el_types.get(el, None)
                el_unit = window_input.el_units.get(el, None)
                if el in window_input.partial_component_list:
                    added = added and add_sigmf_field(update_dictionary, values, el, window_data_type_dict,
                                                      window_input.get_tag(el), required=req_field,
                                                      type=el_type, unit=el_unit)
                else:
                    added = added and add_sigmf_field(SigMFFile.set_global_field, values, el, f,
                                                      window_input.get_tag(el),
                                                      required=req_field, type=el_type, unit=el_unit)

            data_type_str = ''
            data_type_str += 'c' if bool(window_data_type_dict[WindowInput.DATA_TYPE_COMPLEX]) else ''
            data_type_str += 'f' if not bool(window_data_type_dict[WindowInput.DATA_TYPE_FIXEDPOINT]) else ''
            data_type_str += 'u' if bool(window_data_type_dict[WindowInput.DATA_TYPE_UNSIGNED]) else ''
            data_type_str += str(window_data_type_dict[WindowInput.DATA_SAMPLE_SIZE]) + '_'
            data_type_str += 'l' if window_data_type_dict[WindowInput.DATA_BYTE_ORDER] == 'little endian' else 'b'
            data_type_dict = {SigMFFile.DATATYPE_KEY: data_type_str}
            added = added and add_sigmf_field(SigMFFile.set_global_field, data_type_dict, SigMFFile.DATATYPE_KEY, f,
                                              SigMFFile.DATATYPE_KEY, required=True)
            print('HERE: ', window_data_type_dict)
            added = added and add_sigmf_field(SigMFFile.set_data_file, values, WindowInput.DATA_FILE, f,
                                              required=True) and added
            if not added:
                # requirement not given
                continue

            if validate_data(f):
                submit_button.Update(disabled=False, button_color=DEFAULT_BUTTON_COLOR)
        elif event == 'Capture Combo':
            capture_dict = capture_selector_dict[values['Capture Combo']]
            update_capture_screen(capture_data_input, capture_text_blocks, capture_dict)
        elif event == 'Add Capture':
            add_capture(capture_data_input, values, capture_selector_dict, f)

        elif event == 'Remove Capture':
            capture_dict = dict()
            added = add_sigmf_field(update_dictionary, values, CaptureData.START_INDEX, capture_dict,
                                    SigMFFile.START_INDEX_KEY, required=True, type=int)
            if not added:
                # requirement not given
                continue

            captures = []
            for capture in f._metadata[SigMFFile.CAPTURE_KEY]:
                if capture[SigMFFile.START_INDEX_KEY] != capture_dict[SigMFFile.START_INDEX_KEY]:
                    captures.append(capture)
            f._metadata[SigMFFile.CAPTURE_KEY] = captures

            annotations = []
            for annotation in f._metadata[SigMFFile.ANNOTATION_KEY]:
                if annotation[SigMFFile.START_INDEX_KEY] != capture_dict[SigMFFile.START_INDEX_KEY]:
                    annotations.append(annotation)
            f._metadata[SigMFFile.ANNOTATION_KEY] = annotations

            new_values = list(combo_button.Values)
            rm_val = 'Capture {}'.format(capture_dict[SigMFFile.START_INDEX_KEY])
            if rm_val in capture_selector_dict:
                capture_selector_dict.pop(rm_val)
            if rm_val in new_values:
                new_values.remove(rm_val)
                combo_button.Update(values=new_values, set_to_index=0)
                capture_dict = capture_selector_dict.get(combo_button.DefaultValue, None)
                update_capture_screen(capture_data_input, capture_text_blocks, capture_dict)
        elif event == 'Clear Capture':
            update_capture_screen(capture_data_input, capture_text_blocks, None)
        elif event == 'View Data':
            PopupOK('Current data:\n', f.dumps(pretty=True), title='')
        elif event == 'Save Archive':
            output_folder = values[WindowInput.OUTPUT_FOLDER]
            if output_folder == '':
                show_error('No output folder provided')
                continue
            elif len(capture_selector_dict.keys()) == 0:
                show_error('No capture data specified')
            submit_button.Update(text='Saving...')
            window.Refresh()
            archive_file = output_folder + '/' + os.path.basename(f.data_file).split('.')[0] + SIGMF_ARCHIVE_EXT
            f.archive(archive_file)
            PopupOK('Saved archive as \n', archive_file, title='')
        elif event in ['Cancel', None, 'Exit']:
            window.Close()
            break

    window.Close()


if __name__ == '__main__':
    run_gui()
