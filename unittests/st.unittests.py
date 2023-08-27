import unittest
import StructuredText as st

class TestStructuredText(unittest.TestCase):

  def test_extract_from_file(self):
    # Test extracting from a valid file
    result = st.extract('test00-st-format.st')
    self.assertIn('PROJECT_NAME', result)
    self.assertEqual(result['PROJECT_NAME'], 'StructuredText')

  def test_extract_from_list(self):
    # Test extracting from a list
    lines = [
      '# Comment line',
      'KEY1: value1',
      'KEY2: """\nMulti-line\nvalue\n"""',
    ]
    result = st.extract(lines)
    self.assertEqual(result['KEY1'], 'value1')
    self.assertEqual(result['KEY2'], 'Multi-line\nvalue')

  def test_extract_with_strict_mode(self):
    # Test strict mode with invalid content
    lines = [
      '# Comment line',
      'Invalid line without key-value',
      'KEY1: value1',
    ]
    with self.assertRaises(Exception): # Assuming custom exception is implemented
      st.extract(lines, strict=True)

  def test_write_to_file(self):
    # Test writing to a file
    variables = {'KEY1': 'value1', 'KEY2': 'value2'}
    st.write_dict_to_st(variables, filename='output_file.st')
    with open('output_file.st', 'r') as file:
      content = file.read()
    self.assertIn('KEY1: value1', content)
    self.assertIn('KEY2: value2', content)

  def test_write_multiline_value(self):
    # Test writing multi-line value
    variables = {'KEY_MULTILINE': '"""This is\na multi-line\nvalue"""'}
    st.write_dict_to_st(variables, filename='output_multiline.st')
    with open('output_multiline.st', 'r') as file:
      content = file.read()
    self.assertIn('KEY_MULTILINE: """\nThis is\na multi-line\nvalue"""', content)

if __name__ == '__main__':
  unittest.main()
